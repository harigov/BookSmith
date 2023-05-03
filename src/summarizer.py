import logging
import os
from typing import Dict, List
from transformers import GPT2Tokenizer

from langchain.llms import OpenAIChat

from models import Chapter, Section

MAX_TOKENS = 3000
MODEL_NAME = "gpt-3.5-turbo"


SUMMARIZER_PROMPT = "Generate a summary of the text."

IMPORTANCE_CLASSIFER_PROMPT = """You are a bot whose job is to identify which sections of a text \
provide useful information that doesn't involve irrelevant background about author. Just give a \
single word answer of 'yes' or 'no'."""

def gen_prefix_messages(prompt):
    return [{"role": "system", "content": prompt}]

section_summarizer = OpenAIChat(
    model_name=MODEL_NAME,
    openai_api_key=os.environ.get('OPENAI_API_KEY'),
    prefix_messages=gen_prefix_messages(SUMMARIZER_PROMPT))
section_ranker = OpenAIChat(
    model_name=MODEL_NAME,
    openai_api_key=os.environ.get('OPENAI_API_KEY'),
    prefix_messages=gen_prefix_messages(IMPORTANCE_CLASSIFER_PROMPT))

def count_gpt_tokens(text):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokens = tokenizer.tokenize(text)
    token_count = len(tokens)
    return token_count

def summary_is_useful(summary):
    response = section_ranker(summary)
    return response.lower() == 'yes'

def generate_summary(section: Section, allow_splitting: bool = True):
    try:
        section_text = str(section)
        num_tokens = count_gpt_tokens(section_text)
        if num_tokens > MAX_TOKENS and allow_splitting:
            # Split the section into multiple sections
            # and summarize each one
            chunks = section_text.split('\n')
            buffer = []
            summaries = []

            for chunk in chunks:
                buffer.append(chunk)
                token_count = count_gpt_tokens('\n'.join(buffer))
                if token_count > MAX_TOKENS:
                    buffer.pop()
                    summary = section_summarizer('\n'.join(buffer))
                    summaries.append(summary)
                    buffer = [chunk]

            if buffer:
                summary = section_summarizer('\n'.join(buffer))
                summaries.append(summary)

            return ' '.join(summaries)
        else:
            return section_summarizer(section_text)
    except Exception as e:
        return 'Sorry, I could not summarize this section.'

def summary_has_errors(summary):
    # These are the words that show up in the summarization
    # result if it failed summarization
    return 'sorry' in summary.lower() or 'summarize' in summary.lower()


def summarize_chapters(chapters: List[Chapter], synthesize: bool = False, allow_splitting: bool = True, only_important: bool = False) -> List[Dict]:
    # Loop through each chapter, get all the sections and then summarize
    # the sections using OpenAI's GPT-3 API and then serialize the chapters
    # and sections to a JSON file. Only include the summary of each
    # section.
    chapter_dicts = []
    all_summary_length = 0
    for chapter in chapters:
        logging.info(
            f'Processing chapter {chapter.name}: {len(chapter.sections)} sections')
        out_chapter = {'name': chapter.name, 'sections': []}
        for section in chapter.sections:
            logging.info(f'Processing section {section.name}')
            section_summary = generate_summary(section, allow_splitting)
            section_dict = {
                'name': section.name,
                'summary': section_summary,
                'has_errors': summary_has_errors(section_summary),
                'useful': summary_is_useful(section_summary) if only_important else True,
            }

            out_chapter['sections'].append(section_dict)
            all_summary_length += len(section_summary.split(' '))
        chapter_dicts.append(out_chapter)

    logging.info(f'Total summary word length: {all_summary_length}')

    if synthesize:
        total_words = 0
        total_useful_words = 0
        ignored_section_count = 0
        unignored_sections = []
        for chapter in chapter_dicts:
            logging.info(f'# {chapter["name"]}')
            for section in chapter["sections"]:
                logging.info(f'## {section["name"]}')
                try:
                    if 'has_errors' not in section:
                        section['has_errors'] = summary_has_errors(
                            section['summary'])

                    if section['has_errors']:
                        # logging.info(f'Ignoring section {section["name"]} because it failed summarization')
                        ignored_section_count += 1
                        continue

                    if 'useful' not in section:
                        section['useful'] = summary_is_useful(
                            section['summary'])

                    if section['useful']:
                        total_useful_words += len(
                            section['summary'].split(' '))
                except Exception as e:
                    logging.info(f'Error with section {section["name"]}')
                    logging.info(e)
                    section['has_errors'] = True
                    continue

                unignored_sections.append(section)
                total_words += len(section['summary'].split(' '))

        logging.info(f'Ignored {ignored_section_count} sections')
        logging.info(f'Total words in all section summaries: {total_words}')
        logging.info(
            f'Total useful words in all section summaries: {total_useful_words}')

    return chapter_dicts

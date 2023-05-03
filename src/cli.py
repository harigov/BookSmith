import argparse
import json
import logging
import os
import sys
from typing import List
from extractors.epub_extractor import EpubChapterExtractor

from extractors.pdf_extractor import PdfChapterExtractor

from models import Chapter
from summarizer import summarize_chapters



def extract_chapters(input_path: str, pages: str = None) -> List[Chapter]:
    if input_path.endswith('.pdf'):
        pdf_path = input_path
        if pages:
            pages_range = [int(p) for p in pages.split('-')]
            page_numbers = range(pages_range[0], pages_range[1] + 1)
        else:
            pages_range = None
            page_numbers = None

        logging.info(
            f'Extracting chapters from {pdf_path} pages {pages_range}')
        chapters = PdfChapterExtractor().extract(pdf_path, page_numbers)
        logging.info(
            f'Extracted {len(chapters)} chapters from {pdf_path} pages {pages_range}')

    elif input_path.endswith('.epub'):
        epub_path = input_path
        if pages:
            logging.error("Page numbers are not supported for EPUB files")
            sys.exit(1)

        logging.info(
            f'Extracting chapters from {epub_path}')
        chapters = EpubChapterExtractor().extract(epub_path)
        logging.info(
            f'Extracted {len(chapters)} chapters from {epub_path}')
    else:
        raise NotImplementedError(f"Input file type is not supported")

    return chapters

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, required=True, help='Path to the input epub or pdf file that needs to be processed')
    parser.add_argument('--pages', type=str, default=None, required=False, help='Page numbers to extract from the input file. Example: 1-10')
    parser.add_argument(
        '--output_path',
        type=str,
        default=None,
        required=False,
        help='Path to the output file where the summary will be written. Can either be a markdown file or a json file.')
    parser.add_argument(
        '--only_important',
        type=bool,
        default=True,
        required=False,
        help='Whether to only include important sections in the summary')
    parser.add_argument(
        '--allow_splitting',
        type=bool,
        default=True,
        required=False,
        help='Whether to allow splitting of sections into multiple parts to deal with model token limit')
    parser.add_argument(
        '--synthesize',
        type=bool,
        default=True,
        required=False,
        help='Whether to synthesize the content further from the summary')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - [%(levelname)s] %(message)s')

    if not os.environ.get('OPENAI_API_KEY', None):
        logging.error(
            'OPENAI_API_KEY environment variable is not set. Please set it to your OpenAI API key')
        sys.exit(1)

    chapters = extract_chapters(args.input_path, args.pages)
    chapter_dicts = summarize_chapters(chapters, args.synthesize, args.allow_splitting, args.only_important)

    if args.output_path:
        if args.output_path.endswith('.json'):
            logging.info(f'Writing output to {args.output_path}')
            with open(args.output_path, 'w') as f:
                json.dump(chapter_dicts, f, indent=4)
        elif args.output_path.endswith('.md'):
            logging.info(f'Writing output to {args.output_path}')
            with open(args.output_path, 'w') as f:
                for chapter in chapter_dicts:
                    f.write(f'# {chapter["name"]}\n\n')
                    for section in chapter["sections"]:
                        f.write(f'## {section["name"]}\n')
                        f.write(f'{section["summary"]}\n\n')
                        f.write('\n\n')
        else:
            raise NotImplementedError(f"Output file type is not supported")

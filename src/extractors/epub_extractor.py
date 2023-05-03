from collections import Counter
import logging
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

from models import Chapter, Section
from .extractor_base import TextExtractorBase


class EpubChapterExtractor(TextExtractorBase):
    def extract(self, epub_path:str, page_numbers: list[int] = None) -> list[Chapter]:
        book = epub.read_epub(epub_path)
        heading_counter = Counter()
        
        # First pass: Analyze heading levels across all chapters
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.content, 'html.parser')
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            heading_counter.update([h.name for h in headings])

        # Determine chapter and section heading levels
        most_common_headings = [t[0] for t in heading_counter.most_common(2)]
        most_common_headings.reverse()
        chapter_heading_level, section_heading_level = most_common_headings
        
        # Second pass: Extract chapters and sections based on identified heading levels
        chapters = []
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.content, 'html.parser')

            # Extract chapter and section titles
            titles = soup.find_all(chapter_heading_level)
            chapter_title = ' - '.join([t.text.strip() for t in titles]).capitalize()
            if not chapter_title:
                continue

            sections = soup.find_all(section_heading_level)


            section_objs = []
            for i, section in enumerate(sections):
                section_title = section.text.strip()

                # Find paragraphs between the current section and the next section
                if i < len(sections) - 1:
                    next_section = sections[i + 1]
                    paragraphs = section.find_all_next(['p', section_heading_level], limit=50)
                    paragraphs = [p for p in paragraphs if p.name == 'p' and p.find_next(section_heading_level) == next_section]
                else:
                    paragraphs = section.find_all_next('p', limit=50)

                paragraphs = [p.text.strip() for p in paragraphs]
                section_objs.append(Section(section_title, paragraphs))

            if not section_objs:
                continue

            chapters.append(Chapter(chapter_title, section_objs))

        return chapters



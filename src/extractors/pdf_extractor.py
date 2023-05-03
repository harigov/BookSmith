"""Extract chapters and sections from a PDF file. """
from extractors.extractor_base import TextExtractorBase
from pdfminer.high_level import extract_text
from models import Chapter, Section

MIN_PARAGRAPH_WORDS = 8


class PdfChapterExtractor(TextExtractorBase):
    def extract(self, pdf_path: str, page_numbers: list[int]) -> list[Chapter]:
        return self._extract_chapters(pdf_path, page_numbers)

    def _extract_paragraphs(self, pdf_path, page_numbers) -> list[str]:
        text = extract_text(pdf_path, page_numbers=page_numbers)
        paragraphs = text.split('\n\n')
        out_paragraphs = []
        for paragraph in paragraphs:
            para_str = ' '.join(paragraph.split('\n'))
            para_words = para_str.split(' ')
            # Ignore paragraphs with small number of words
            # unless they're all capital case, which represents
            # a section or chapter title
            if not all([w.isupper() for w in para_words]) and len(
                    para_words) < MIN_PARAGRAPH_WORDS:
                continue

            out_paragraphs.append(para_str)

        # Post process paragraphs by merging any paragraphs beginning
        # with a lower case letter with the preceding paragraph
        for i in range(len(out_paragraphs) - 1, 0, -1):
            if out_paragraphs[i][0].islower():
                out_paragraphs[i - 1] += ' ' + out_paragraphs[i]
                out_paragraphs[i] = ''

        return [p for p in out_paragraphs if p]

    def _extract_section_name_from_paragraph(self, paragraph: str) -> str:
        # Extract all the upper case words from the first line
        # of the paragraph
        title = ''
        for w in paragraph.split(' '):
            if w.isupper():
                title += w + ' '
            else:
                break
        return title

    def _extract_chapters(self, pdf_path, page_numbers) -> list[Chapter]:
        out_sections: list[Section] = []
        section_paragraphs: list[str] = []
        # Merge multiple paragraphs into sections by looking
        # at the first word of each paragraph. If the first word
        # is in all caps, then it is a new section.
        paragraphs = self._extract_paragraphs(pdf_path, page_numbers)
        for paragraph in paragraphs:
            if paragraph.split(' ')[0].isupper():
                if section_paragraphs:
                    section_name = self._extract_section_name_from_paragraph(
                        section_paragraphs[0])
                    section = Section(section_name, section_paragraphs)
                    out_sections.append(section)
                section_paragraphs = [paragraph]
            else:
                section_paragraphs.append(paragraph)

        if section_paragraphs:
            section_name = self._extract_section_name_from_paragraph(
                section_paragraphs[0])
            section = Section(section_name, section_paragraphs)
            out_sections.append(section)

        # Convert sections into Section objects
        out_chapters: list[Chapter] = []
        chapter_sections: list[Section] = []
        for section in out_sections:
            if str(section).split(' ')[0].strip().isnumeric():
                if chapter_sections:
                    chapter_title = str(chapter_sections[0]).strip()
                    out_chapters.append(
                        Chapter(chapter_title, chapter_sections[1:]))
                chapter_sections = [section]
            else:
                chapter_sections.append(section)

        if chapter_sections:
            chapter_title = str(chapter_sections[0]).strip()
            out_chapters.append(Chapter(chapter_title, chapter_sections[1:]))

        return out_chapters


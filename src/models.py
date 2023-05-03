
class Section:
    def __init__(self, name, paragraphs: list[str]):
        self.name = name
        self.paragraphs = paragraphs

    def __str__(self):
        return '\n\n'.join(self.paragraphs)

    def __repr__(self):
        return f'{self.name}'

class Chapter:
    def __init__(self, name, sections: list[Section]):
        self.name = name
        self.sections = sections

    def __str__(self):
        return '\n\n'.join(self.sections)

    def __repr__(self):
        return f'{self.name}, {len(self.sections)} sections'

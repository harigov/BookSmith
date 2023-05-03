from abc import ABC, abstractmethod

from models import Chapter

class TextExtractorBase(ABC):
    @abstractmethod
    def extract(self, file_path: str, page_numbers: list[int]=None) -> list[Chapter]:
        raise NotImplementedError("Please Implement this method")

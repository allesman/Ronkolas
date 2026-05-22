from abc import ABC, abstractmethod
from pathlib import Path
from type.ASCII import ASCII

class Filter(ABC):
    @abstractmethod
    def apply(self, ascii : ASCII) -> ASCII:
        ...
    
    @abstractmethod
    def configure(self, params: dict[str, any]) -> None:
        ...
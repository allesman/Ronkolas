from abc import ABC, abstractmethod
from typing import Optional

class Logger(ABC):
    @abstractmethod
    def info(self, msg: str) -> None:
        ...

    @abstractmethod
    def warn(self, msg: str) -> None:
        ...

    @abstractmethod
    def error(self, msg: str) -> None:
        ...

import logging

class StdLogger(Logger):
    def __init__(self, name: str = "ascii_pipeline") -> None:
        self._log = logging.getLogger(name)

    def info(self, msg: str)  -> None: self._log.info(msg)
    def warn(self, msg: str)  -> None: self._log.warning(msg)
    def error(self, msg: str, exc: Optional[Exception] = None) -> None:
        self._log.error(msg, exc_info=exc)
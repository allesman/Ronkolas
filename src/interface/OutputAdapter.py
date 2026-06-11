from abc import ABC, abstractmethod
from pathlib import Path
from type.ASCII import ASCII

class OutputAdapter(ABC):
    @abstractmethod
    def save_to_file(self, ascii: ASCII) -> bool:
        ...

    @abstractmethod
    def serialize(self, ascii: ASCII) -> bytes:
        ...

    @abstractmethod
    def send(self, data: bytes, port: str, baud_rate: int = 9600) -> bool:
        """Transmits serialized bytes to the MCU over UART/Serial.
        Args:
            data:      Raw bytes from serialize().
            port:      Serial port identifier, e.g. "/dev/ttyAMA0" on the Pi.
            baud_rate: Bits per second — must match MCU firmware setting.

        Returns:
            True:  all bytes were written without error.
            False: port was unavailable or write failed (no raise, sopipeline can log and decide what to do).
        """
        ...
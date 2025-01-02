from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class EventChannel(IntEnum):
    ...


@dataclass
class Event:
    model_ref: str
    channel: EventChannel
    payload: Any


class ModelConnector(ABC):

    @abstractmethod
    def get_value(self, model_ref: str) -> Any:
        ...

    @abstractmethod
    def set_value(self, model_ref: str, value: Any) -> None:
        ...

    @abstractmethod
    def send_event(self, event: Event) -> None:
        ...

    @abstractmethod
    def receive_event(self) -> Event:
        ...

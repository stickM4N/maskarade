from typing import Any, Callable, TypeVar, final

from .connector import Event, EventChannel
from .log import ModelLogger


class ModelRef:
    ...


MRef = TypeVar('MRef', bound=ModelRef)


class ModelRef:

    @staticmethod
    def _has_connector(func):
        def _wrapper(self, *args, **kwargs):
            if self._connector is None:
                raise RuntimeError(f"A connector is required to operate on `{self.model_ref}` model reference.")

            return func(self, *args, **kwargs)

        return _wrapper

    def __init__(self, value_type: type, model_ref: str, *, model_ref_fmt_args: dict = None):
        model_ref_fmt_args = model_ref_fmt_args or {}

        self._value_type = value_type
        self._model_ref = model_ref.format(**model_ref_fmt_args)
        self._connector = None
        self._on_event_cb = None

        self._logger = ModelLogger()

    @property
    @_has_connector
    def value(self) -> Any:
        value = self._connector.get_value(self._model_ref)
        if not isinstance(value, self.value_type):
            self._logger.warning(f'Getting wrong type value {value} [{type(value).__name__}] '
                                 f'from `{self.model_ref}` of type {self.value_type}.')

        return value

    @value.setter
    @_has_connector
    def value(self, value) -> None:
        if not isinstance(value, self.value_type):
            self._logger.warning(f'Setting wrong type value {value} [{type(value).__name__}] '
                                 f'to `{self.model_ref}` of type {self.value_type}.')

        self._connector.set_value(self.model_ref, value)

    @property
    def value_type(self) -> type:
        return self._value_type

    @property
    def model_ref(self) -> str:
        return self._model_ref

    @final
    @_has_connector
    def generate_event(self, channel: EventChannel, payload: Any) -> None:
        event = Event(self.model_ref, channel, payload)
        self._connector.send_event(event)

    @final
    def set_event_callback(self, callback: Callable[[Event], None]) -> None:
        self._on_event_cb = callback

    @final
    def handle_event(self, event: Event) -> None:
        if self._on_event_cb is None:
            self._logger.warning(f'Cannot handle event for `{self.model_ref}` without an associated callback.')
            return

        self._on_event_cb(event)

from .connector import ModelConnector
from .model import MB_t
from .utils import final_models


class ModelsManager:

    def __init__(self, models: list[MB_t], connector: ModelConnector):
        if not isinstance(connector, ModelConnector):
            raise ValueError(f'Connector must be of type ModelConnector, not {type(connector).__name__}.')

        for model in models:
            if model not in final_models():
                raise RuntimeError(f"Cannot initialize model {type(model).__name__} if it is not marked as final.")

            model._inject_connector(connector)

        self._models = models

    @property
    def models(self):
        return self._models

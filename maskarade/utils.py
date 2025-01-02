from copy import copy
from types import NoneType, new_class

from .model import MB_t, ModelBase, model_ref_associations
from .reference import MRef, ModelRef


def final_models(filter_type: MB_t = None) -> list[MB_t]:
    filter_type = filter_type or ModelBase

    models = []
    for model, _ in model_ref_associations().values():
        if model not in models and issubclass(model, filter_type):
            models.append(model)

    return models


def model_from_ref(model_ref: str) -> MB_t | NoneType:
    association = model_ref_associations(model_ref)
    return association[0]


def model_ref_from_ref(model_ref: str) -> MRef | None:
    association = model_ref_associations(model_ref)
    return association[1]


def make_model_class(name: str, base: MB_t, is_final: bool = True, **fmt_params) -> MB_t:
    def _gen_body(ns: dict):
        for attr, value in vars(base).items():
            if attr == '__annotations__':
                continue
            if isinstance(value, ModelRef):
                value = copy(value)
                value._model_ref = value.model_ref.format(**fmt_params)
            ns[attr] = value
        return ns

    cls_name = name.format(**fmt_params)
    new_cls = new_class(cls_name, (base,), {'final': is_final}, _gen_body)

    return new_cls

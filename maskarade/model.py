from contextlib import contextmanager
from copy import copy
from inspect import get_annotations
from types import NoneType
from typing import TypeVar, final, overload

from .connector import ModelConnector
from .log import ModelLogger
from .reference import MRef, ModelRef


class ModelBase:
    ...


MB = TypeVar('MB', bound=ModelBase)
MB_t = type[MB]

_ref_model_associations: dict[str, tuple[MB_t, MRef]] = {}


@overload
def model_ref_associations() -> dict[str, tuple[MB_t, MRef]]: ...


@overload
def model_ref_associations(model_ref: str) -> tuple[MB_t, MRef] | tuple[NoneType, None]: ...


def model_ref_associations(model_ref=None):
    return copy(_ref_model_associations) \
        if model_ref is None \
        else _ref_model_associations.get(model_ref, (NoneType, None))


class __ModelBaseMeta(type):

    @staticmethod
    def __validate_implementation(model_cls):
        annotations = {}
        repeated_annotations: dict[str, list[str]] = {}
        skipped_annotations = []

        for cls in model_cls.mro():
            annot = get_annotations(cls)

            for ann, val in annot.items():
                if not issubclass(val, ModelRef):
                    skipped_annotations.append(ann)
                if ann in annotations and ann in repeated_annotations:
                    repeated_annotations[ann].append(cls.__name__)
                    continue
                repeated_annotations[ann] = [cls.__name__]

            annotations.update(annot)

        repeated_annotations = {
            ann: clss
            for ann, clss in repeated_annotations.items()
            if len(clss) > 1
        }
        if len(repeated_annotations) != 0:
            data = "\n\t-> ".join([f'{ann} @ {clss}' for ann, clss in repeated_annotations.items()])
            raise AssertionError(f'Some annotations defined multiple times:\n\t-> {data}')

        non_init_annotations = [
            a for a in annotations
            if a not in dir(model_cls) and a not in skipped_annotations
        ]
        if len(non_init_annotations) != 0:
            data = "\n\t-> ".join(non_init_annotations)
            raise AssertionError(f'Some annotations are not initialized:\n\t-> {data}')

    @contextmanager
    @staticmethod
    def __validate_duplication(model_cls):
        repeated_attrs: list[tuple[str, MB_t, MRef]] = []
        yield repeated_attrs

        if len(repeated_attrs) != 0:
            data = "\n\t-> ".join([f'{attr} (`{ref.model_ref}`) @ {model.__name__}'
                                   for attr, model, ref in repeated_attrs])

            raise AssertionError(f'Some attributes from {model_cls.__name__} '
                                 f'are referenced multiple times:\n\t-> {data}')

    def __new__(mcs, name, bases, namespace, **kwargs):
        __model_cls: MB_t = super().__new__(mcs, name, bases, namespace)

        if kwargs.get('final', False):
            mcs.__validate_implementation(__model_cls)

            with mcs.__validate_duplication(__model_cls) as repeated_attrs:
                for attr, value in vars(__model_cls).items():
                    if isinstance(value, ModelRef):
                        model, ref = model_ref_associations(value.model_ref)
                        if ref is not None:
                            repeated_attrs.append((attr, model, ref))
                            continue

                        _ref_model_associations[value.model_ref] = (__model_cls, value)

        return __model_cls


class ModelBase(metaclass=__ModelBaseMeta):

    def __init__(self):
        assert False, "This is not meant to be instantiated"

    @final
    @classmethod
    def _inject_connector(cls, connector: ModelConnector):
        logger = ModelLogger()
        for attr in vars(cls).values():
            if isinstance(attr, ModelRef):
                if attr._connector is not None:
                    logger.warning(f"Reference for `{attr.model_ref}` already has a connector, switching instances.")
                attr._connector = connector

    @final
    @classmethod
    def as_type(cls, target_type: MB_t) -> MB_t | None:
        if not issubclass(cls, target_type):
            return None
        return cls

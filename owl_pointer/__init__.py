"""Owl Pointer: a small, Owlready2-based pointer package for OWL individuals.

Owl Pointer：一个基于 Owlready2、用于操作 OWL 本体的“个体指针”轻量软件包。
"""

from __future__ import annotations

from .creators import create_class, create_individual
from .exceptions import (
    ClassNotFoundError,
    IndexOutOfRangeError,
    IndividualNotFoundError,
    OwlPointerError,
    PointerEmptyError,
    PropertyNotFoundError,
    ValueTypeError,
)
from .pointer import IndividualPointer

__all__ = [
    "IndividualPointer",
    "create_class",
    "create_individual",
    "OwlPointerError",
    "PointerEmptyError",
    "IndividualNotFoundError",
    "PropertyNotFoundError",
    "IndexOutOfRangeError",
    "ValueTypeError",
    "ClassNotFoundError",
]

__version__ = "0.1.0"

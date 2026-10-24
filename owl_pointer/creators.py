"""Global creation helpers / 全局创建辅助函数.

These functions create ontology entities without the indirection of an
``IndividualPointer`` instance.

这些函数可直接创建本体实体，无需先构造 ``IndividualPointer`` 实例。
"""

from __future__ import annotations

from typing import Optional, Tuple

import owlready2
from owlready2 import Thing, types

from .exceptions import ClassNotFoundError


def create_individual(
    onto: owlready2.Ontology,
    class_name: str,
    individual_name: Optional[str] = None,
) -> owlready2.Thing:
    """Create a new individual of ``class_name`` and return it.

    为指定类创建一个新个体并返回。

    If the class does not exist in ``onto``, :class:`ClassNotFoundError` is
    raised. If ``individual_name`` is omitted, Owlready2 generates a name.

    若 ``onto`` 中不存在该类则抛出 :class:`ClassNotFoundError`；省略名称时由
    Owlready2 自动生成。
    """
    cls = getattr(onto, class_name, None)
    if cls is None:
        try:
            cls = onto[class_name]
        except Exception:
            cls = None
    if cls is None or not isinstance(cls, owlready2.ThingClass):
        raise ClassNotFoundError(
            f"Class '{class_name}' does not exist in ontology '{onto.base_iri}'."
        )

    with onto:
        return cls() if individual_name is None else cls(individual_name)


def create_class(
    onto: owlready2.Ontology,
    class_name: str,
    parent_classes: Tuple[owlready2.ThingClass, ...] = (Thing,),
) -> owlready2.ThingClass:
    """Dynamically create a new class bound to ``onto``.

    在目标本体命名空间中动态创建一个新类。

    ``parent_classes`` must be a tuple. The class is created inside a
    ``with onto:`` block so it belongs to ``onto`` rather than the default
    ontology.

    ``parent_classes`` 必须是元组；类在 ``with onto:`` 上下文中创建，确保绑定到
    目标本体而非默认本体。
    """
    if not isinstance(parent_classes, tuple):
        raise TypeError("parent_classes must be a tuple, not a list or other type.")

    with onto:
        cls = types.new_class(class_name, parent_classes)
    return cls

"""Core ``IndividualPointer`` implementation / ``IndividualPointer`` 核心实现.

``IndividualPointer`` holds a reference (the "pointer") to one individual in an
OWL ontology and exposes navigation, reading, and assertion-editing methods.
Reading methods always return a Python ``list``, which keeps callers from having
to distinguish functional properties from non-functional ones.

``IndividualPointer`` 持有本体中某个个体（即“指针”），并提供移动、读取和
属性断言的增删方法。读取方法一律返回 ``list``，调用方无需区分 Functional
与非 Functional 属性。
"""

from __future__ import annotations

import os
from typing import Any, List, Optional

import owlready2
from owlready2 import Thing, get_ontology

from .exceptions import (
    ClassNotFoundError,
    IndexOutOfRangeError,
    IndividualNotFoundError,
    PointerEmptyError,
    PropertyNotFoundError,
    ValueTypeError,
)


class IndividualPointer:
    """A pointer over an individual in an Owlready2 ontology.

    指向 Owlready2 本体中某个个体的“指针”封装。

    Parameters
    ----------
    owl_path:
        Path to the ``.owl`` file. It is loaded through
        ``file:// + absolute path`` so a relative path is never mistaken for the
        ontology base IRI.

        ``.owl`` 文件路径。加载时使用 ``file:// + 绝对路径``，避免相对路径被
        解析成本体 base IRI。
    """

    def __init__(self, owl_path: str) -> None:
        self.owl_path: str = os.path.abspath(owl_path)
        self.onto: owlready2.Ontology = get_ontology(
            "file://" + self.owl_path
        ).load()
        self.p: Optional[owlready2.Thing] = None

    # ------------------------------------------------------------------ #
    # Navigation / 移动与定位
    # ------------------------------------------------------------------ #
    def goto_by_name(self, name: str) -> None:
        """Point to the individual whose name is ``name``.

        将指针移动到名称为 ``name`` 的个体。

        It first tries exact lookup with ``onto[name]`` and then falls back to a
        partial IRI search ``search_one(iri="*<name>")``.

        先尝试 ``onto[name]`` 精确查找，失败后使用 ``search_one(iri="*<name>")``
        做部分 IRI 匹配。
        """
        entity: Optional[Any] = None

        try:
            entity = self.onto[name]
        except Exception:
            entity = None

        if entity is None:
            try:
                entity = self.onto.search_one(iri=f"*{name}")
            except Exception:
                entity = None

        if entity is None or not isinstance(entity, Thing):
            raise IndividualNotFoundError(
                f"Individual '{name}' was not found in ontology "
                f"'{self.owl_path}'."
            )

        self.p = entity

    def goto_by_object_property(self, prop_name: str, n: int = 0) -> None:
        """Move the pointer to the ``n``-th value of an object property.

        将指针移动到当前个体对象属性 ``prop_name`` 的第 ``n`` 个值（0-based）。

        The current individual is not changed by :meth:`get_object_property`;
        only this method mutates the pointer.

        读取方法 :meth:`get_object_property` 不会移动指针，只有本方法会修改指针。
        """
        values: List[Any] = self.get_object_property(prop_name)
        if n < 0 or n >= len(values):
            raise IndexOutOfRangeError(
                f"Index {n} is out of range for object property '{prop_name}' "
                f"which has {len(values)} value(s)."
            )
        self.p = values[n]

    # ------------------------------------------------------------------ #
    # Pointer information / 读取指针信息
    # ------------------------------------------------------------------ #
    def get(self) -> owlready2.Thing:
        """Return the individual currently pointed to by ``p``.

        返回指针 ``p`` 当前指向的个体对象。
        """
        if self.p is None:
            raise PointerEmptyError("Pointer p is empty; move it before reading.")
        return self.p

    def get_name(self) -> str:
        """Return the name of the individual currently pointed to.

        返回当前指针指向个体的名称。
        """
        return self.get().name

    def get_iri(self) -> str:
        """Return the IRI of the individual currently pointed to.

        返回当前指针指向个体的 IRI。
        """
        return self.get().iri

    # ------------------------------------------------------------------ #
    # Uniform list reading / 统一返回 list 的读取方法
    # ------------------------------------------------------------------ #
    def _read_as_list(self, prop_name: str) -> List[Any]:
        if self.p is None:
            raise PointerEmptyError("Pointer p is empty; move it before reading.")
        values = getattr(self.p, prop_name, None)
        if values is None:
            return []
        if not isinstance(values, list):
            return [values]
        return values

    def get_data_property(self, prop_name: str) -> List[Any]:
        """Return a data property's values, always as a ``list``.

        以 ``list`` 形式返回数据属性的全部值。

        Missing assertions yield ``[]``; a single functional value is wrapped as
        ``[value]``. The pointer is not moved.

        无断言返回 ``[]``；Functional 单值被包装为 ``[value]``。本方法只读、
        不移动指针。
        """
        self._require_property(prop_name)
        return self._read_as_list(prop_name)

    def get_object_property(self, prop_name: str) -> List[Any]:
        """Return an object property's values, always as a ``list``.

        以 ``list`` 形式返回对象属性的全部值（元素为个体对象）。

        Missing assertions yield ``[]``; a single functional value is wrapped as
        ``[value]``. The pointer is not moved.

        无断言返回 ``[]``；Functional 单值被包装为 ``[value]``。本方法只读、
        不移动指针。
        """
        self._require_property(prop_name)
        return self._read_as_list(prop_name)

    # ------------------------------------------------------------------ #
    # Assertion editing / 增删属性断言
    # ------------------------------------------------------------------ #
    def add_value(self, prop_name: str, value: Any) -> None:
        """Add one value to the current individual's property assertion.

        为当前个体添加一个属性断言值。

        Non-functional properties use ``append``; functional properties use
        ``setattr``. Object-property values must be :class:`owlready2.Thing`
        instances and data-property values must not be.

        非 Functional 属性使用 ``append``，Functional 属性使用 ``setattr``。
        对象属性值必须是 :class:`owlready2.Thing` 实例，数据属性值不能是。
        """
        if self.p is None:
            raise PointerEmptyError("Pointer p is empty; move it before editing.")
        prop = self._require_property(prop_name)
        is_object_property = isinstance(prop, owlready2.ObjectPropertyClass)

        if is_object_property and not isinstance(value, Thing):
            raise ValueTypeError(
                f"Object property '{prop_name}' requires a Thing instance, "
                f"got {type(value).__name__}."
            )
        if not is_object_property and isinstance(value, Thing):
            raise ValueTypeError(
                f"Data property '{prop_name}' cannot take a Thing instance "
                f"as its value."
            )

        if self._is_functional(prop):
            setattr(self.p, prop_name, value)
        else:
            current = getattr(self.p, prop_name, None)
            if not isinstance(current, list):
                current = []
            current.append(value)

    def remove_value(self, prop_name: str, value: Any) -> None:
        """Remove one value from the current individual's property assertion.

        从当前个体的属性断言中移除一个值。

        Non-functional properties remove the matching list element; functional
        properties are cleared with ``prop[self.p] = []``.

        非 Functional 属性从 list 中移除匹配元素；Functional 属性使用
        ``prop[self.p] = []`` 清空。
        """
        if self.p is None:
            raise PointerEmptyError("Pointer p is empty; move it before editing.")
        prop = self._require_property(prop_name)

        if self._is_functional(prop):
            prop[self.p] = []
            return

        current = getattr(self.p, prop_name, None)
        if isinstance(current, list):
            try:
                current.remove(value)
            except ValueError:
                pass

    def clear_property(self, prop_name: str) -> None:
        """Clear all assertions for ``prop_name`` on the current individual.

        清空当前个体在 ``prop_name`` 下的所有属性断言。
        """
        if self.p is None:
            raise PointerEmptyError("Pointer p is empty; move it before editing.")
        prop = self._require_property(prop_name)
        prop[self.p] = []

    # ------------------------------------------------------------------ #
    # Individual creation / 创建新个体
    # ------------------------------------------------------------------ #
    def create_and_point(
        self, class_name: str, individual_name: Optional[str] = None
    ) -> owlready2.Thing:
        """Create a new individual of ``class_name`` and point to it.

        为指定类创建一个新个体，并让指针指向它。

        The new individual is returned as a convenience. If
        ``individual_name`` is omitted, Owlready2 generates a name.

        返回新建的个体以方便使用。若省略 ``individual_name``，Owlready2 会自动
        生成名称。
        """
        cls = self._require_class(class_name)
        with self.onto:
            individual = cls() if individual_name is None else cls(individual_name)
        self.p = individual
        return individual

    # ------------------------------------------------------------------ #
    # Persistence / 持久化
    # ------------------------------------------------------------------ #
    def save(self, path: Optional[str] = None) -> None:
        """Persist in-memory changes back to disk as RDF/XML.

        将内存中的修改以 RDF/XML 格式写回磁盘。

        If ``path`` is ``None`` the original file is overwritten; otherwise the
        ontology is written to ``path``.

        ``path`` 为 ``None`` 时覆盖原文件，否则另存到 ``path``。
        """
        if path is None:
            self.onto.save(format="rdfxml")
        else:
            self.onto.save(file=path, format="rdfxml")

    # ------------------------------------------------------------------ #
    # Internal helpers / 内部辅助方法
    # ------------------------------------------------------------------ #
    def _require_property(self, prop_name: str) -> Any:
        """Return the property object or raise :class:`PropertyNotFoundError`.

        返回属性对象；属性不存在时抛出 :class:`PropertyNotFoundError`。
        """
        prop = getattr(self.onto, prop_name, None)
        if prop is None:
            try:
                prop = self.onto[prop_name]
            except Exception:
                prop = None
        if prop is None:
            raise PropertyNotFoundError(
                f"Property '{prop_name}' does not exist in ontology "
                f"'{self.owl_path}'."
            )
        return prop

    def _require_class(self, class_name: str) -> owlready2.ThingClass:
        """Return the class object or raise :class:`ClassNotFoundError`.

        返回类对象；类不存在时抛出 :class:`ClassNotFoundError`。
        """
        cls = getattr(self.onto, class_name, None)
        if cls is None:
            try:
                cls = self.onto[class_name]
            except Exception:
                cls = None
        if cls is None or not isinstance(cls, owlready2.ThingClass):
            raise ClassNotFoundError(
                f"Class '{class_name}' does not exist in ontology "
                f"'{self.owl_path}'."
            )
        return cls

    def _is_functional(self, prop: Any) -> bool:
        """Best-effort functional detection across Owlready2 versions.

        尽量兼容不同 Owlready2 版本的 Functional 属性判断。
        """
        checker = getattr(prop, "is_functional_for", None)
        if checker is not None:
            try:
                return bool(checker(self.p))
            except Exception:
                pass
        value = getattr(prop, "is_functional", None)
        if value is None:
            value = getattr(prop, "functional", None)
        return bool(value)

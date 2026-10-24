"""Package-level exception hierarchy / 包级异常体系.

Every error raised by this package is a subclass of :class:`OwlPointerError`.
Callers can therefore catch the single base class, or the precise subclass that
matches a particular failure.

本包抛出的所有异常都派生自 :class:`OwlPointerError`。调用方既可以只捕获这个
基类，也可以捕获与具体失败原因对应的子类。
"""

from __future__ import annotations


class OwlPointerError(Exception):
    """Base exception for all errors raised by ``owl_pointer``.

    本包所有异常的公共基类。
    """


class PointerEmptyError(OwlPointerError):
    """Raised when an operation requires a non-empty pointer ``p``.

    当操作需要一个非空指针 ``p``、而当前指针为空时抛出。
    """


class IndividualNotFoundError(OwlPointerError):
    """Raised when an individual cannot be located by name.

    按名称无法在目标本体中找到个体时抛出。
    """


class PropertyNotFoundError(OwlPointerError):
    """Raised when a property does not exist in the ontology.

    目标本体中不存在指定属性时抛出。
    """


class IndexOutOfRangeError(OwlPointerError):
    """Raised when an object-property value index is out of range.

    读取对象属性的第 ``n`` 个值时下标越界抛出。
    """


class ValueTypeError(OwlPointerError):
    """Raised when a value has the wrong type for an object/data property.

    为对象属性或数据属性提供类型不匹配的值时抛出。
    """


class ClassNotFoundError(OwlPointerError):
    """Raised when the requested class does not exist in the ontology.

    目标本体中不存在指定类时抛出。
    """

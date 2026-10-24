"""Runnable demo for the ``owl_pointer`` package.

``owl_pointer`` 软件包的可运行演示。

Run from the repository root after ``pip install -e .``:

    python examples/demo.py

The demo works against the bundled ``mini_wine.owl`` and writes its edited copy
to ``owl_pointer_demo_output.owl`` in the system temporary directory.

演示基于内置的 ``mini_wine.owl``，并把修改后的副本保存到系统临时目录下的
``owl_pointer_demo_output.owl``。
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Make the repository root importable even if the package was not pip-installed
# yet. 即使尚未执行 pip install，也先让仓库根目录可被 import。
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from owl_pointer import (  # noqa: E402
    ClassNotFoundError,
    IndividualNotFoundError,
    IndividualPointer,
    IndexOutOfRangeError,
    OwlPointerError,
    PointerEmptyError,
    PropertyNotFoundError,
    ValueTypeError,
    create_class,
    create_individual,
)


def main() -> None:
    here = Path(__file__).resolve().parent
    owl_path = str(here / "mini_wine.owl")
    out_path = str(Path(tempfile.gettempdir()) / "owl_pointer_demo_output.owl")

    # 1. Load the ontology and locate an individual by name.
    # 加载本体并按名称定位个体。
    pointer = IndividualPointer(owl_path)
    pointer.goto_by_name("chateau_margaux")
    print("located:", pointer.get_name(), pointer.get_iri())

    # 2. Data properties always return a list.
    # 数据属性一律返回 list。
    print("hasName (functional, wrapped):", pointer.get_data_property("hasName"))
    print("hasFlavor (multi-valued):", pointer.get_data_property("hasFlavor"))
    print("hasYear (no assertion):", pointer.get_data_property("hasYear"))

    # 3. Object properties always return a list of individuals.
    # 对象属性一律返回 list（元素为个体）。
    grapes = pointer.get_object_property("madeFromGrape")
    print("madeFromGrape:", [g.name for g in grapes])

    # 4. Move the pointer through an object property without losing read safety.
    # 通过对象属性移动指针（读取方法本身不移动）。
    pointer.goto_by_object_property("madeFromGrape", 1)
    print("after move:", pointer.get_name())

    # Move back and exercise an out-of-range index exception.
    # 移回原个体，并演示越界异常。
    pointer.goto_by_name("chateau_margaux")
    try:
        pointer.goto_by_object_property("madeFromGrape", 99)
    except IndexOutOfRangeError as exc:
        print("caught index error:", exc)

    # 5. Create a new class and point to a new individual.
    # 创建新类，并为该类创建新个体。
    reserve_wine = create_class(pointer.onto, "ReserveWine", (pointer.onto.Wine,))
    new_wine = pointer.create_and_point("ReserveWine", "reserve_2024")
    print("created class:", reserve_wine.name, "| created individual:", new_wine.name)

    # 6. Add data/object assertions.
    # 添加数据属性与对象属性断言。
    pointer.add_value("hasName", "Reserve 2024")
    pointer.add_value("hasYear", 2024)
    pointer.add_value("madeFromGrape", pointer.onto.merlot)
    print("after add:", pointer.get_data_property("hasName"),
          pointer.get_data_property("hasYear"),
          [g.name for g in pointer.get_object_property("madeFromGrape")])

    # Demonstrate the global individual creator as well.
    # 同时演示全局的个体创建函数。
    second = create_individual(pointer.onto, "ReserveWine", "reserve_2025")
    print("global creator made:", second.name)

    # 7. Remove one value and clear another property.
    # 移除单个属性值，并清空另一个属性。
    pointer.goto_by_name("chateau_margaux")
    pointer.remove_value("hasFlavor", "cedar")
    print("flavors after remove:", pointer.get_data_property("hasFlavor"))
    pointer.clear_property("madeFromGrape")
    print("grapes after clear:", pointer.get_object_property("madeFromGrape"))

    # 8. Type validation for object properties.
    # 对象属性值的类型校验。
    try:
        pointer.add_value("madeFromGrape", "not-a-thing")
    except ValueTypeError as exc:
        print("caught type error:", exc)

    # 9. Save to a new file.
    # 保存到新文件。
    pointer.save(out_path)
    print("saved:", out_path)

    # 10. Exception demo: locating a missing individual.
    # 异常演示：按名称找不到个体。
    try:
        pointer.goto_by_name("does_not_exist")
    except IndividualNotFoundError as exc:
        print("caught not-found error:", exc)

    print("demo finished successfully")


if __name__ == "__main__":
    main()

"""Basic unit tests for the ``owl_pointer`` package.

``owl_pointer`` 软件包的基础单元测试。

Run with:

    python -m unittest discover -s tests

or, if pytest is installed:

    pytest
"""

from __future__ import annotations

import os
import tempfile
import unittest
import uuid
from pathlib import Path

from owlready2 import Thing

from owl_pointer import (
    ClassNotFoundError,
    IndexOutOfRangeError,
    IndividualNotFoundError,
    IndividualPointer,
    PointerEmptyError,
    PropertyNotFoundError,
    ValueTypeError,
    create_class,
    create_individual,
)


class IndividualPointerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.owl_path = os.path.join(self.tmpdir.name, "mini_wine.owl")
        source = Path(__file__).resolve().parent.parent / "examples" / "mini_wine.owl"
        text = source.read_text(encoding="utf-8")
        # Give each test its own entity IRIs so tests do not share cached
        # entities in owlready2's global default world.
        # 为每个测试生成独立的实体 IRI，避免 default_world 缓存造成测试互相影响。
        unique_base = "http://example.org/wine-test-%s" % uuid.uuid4().hex
        text = text.replace("http://example.org/wine", unique_base)
        with open(self.owl_path, "w", encoding="utf-8") as handle:
            handle.write(text)
        self.pointer = IndividualPointer(self.owl_path)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_empty_pointer_raises(self) -> None:
        with self.assertRaises(PointerEmptyError):
            self.pointer.get_name()
        with self.assertRaises(PointerEmptyError):
            self.pointer.get_data_property("hasName")

    def test_goto_by_name_and_missing_individual(self) -> None:
        self.pointer.goto_by_name("chateau_margaux")
        self.assertEqual(self.pointer.get_name(), "chateau_margaux")
        with self.assertRaises(IndividualNotFoundError):
            self.pointer.goto_by_name("does_not_exist")

    def test_data_property_always_list(self) -> None:
        self.pointer.goto_by_name("chateau_margaux")
        self.assertEqual(self.pointer.get_data_property("hasName"), ["Chateau Margaux"])
        self.assertEqual(
            sorted(self.pointer.get_data_property("hasFlavor")),
            ["blackcurrant", "cedar"],
        )
        self.assertEqual(self.pointer.get_data_property("hasYear"), [])

    def test_object_property_always_list_and_move(self) -> None:
        self.pointer.goto_by_name("chateau_margaux")
        grapes = self.pointer.get_object_property("madeFromGrape")
        self.assertEqual([g.name for g in grapes], ["cabernet_sauvignon", "merlot"])

        self.pointer.goto_by_object_property("madeFromGrape", 1)
        self.assertEqual(self.pointer.get_name(), "merlot")
        with self.assertRaises(IndexOutOfRangeError):
            self.pointer.goto_by_object_property("madeFromGrape", 10)

    def test_add_and_remove_values(self) -> None:
        self.pointer.goto_by_name("chateau_margaux")
        self.pointer.add_value("hasYear", 2019)
        self.assertEqual(self.pointer.get_data_property("hasYear"), [2019])

        merlot = self.pointer.onto.merlot
        self.assertIsInstance(merlot, Thing)
        self.pointer.add_value("madeFromGrape", merlot)
        self.assertIn(
            "merlot",
            [g.name for g in self.pointer.get_object_property("madeFromGrape")],
        )

        with self.assertRaises(ValueTypeError):
            self.pointer.add_value("madeFromGrape", "not-a-thing")
        with self.assertRaises(ValueTypeError):
            self.pointer.add_value("hasName", merlot)

        self.pointer.remove_value("hasFlavor", "cedar")
        self.assertEqual(self.pointer.get_data_property("hasFlavor"), ["blackcurrant"])

    def test_clear_property(self) -> None:
        self.pointer.goto_by_name("chateau_margaux")
        self.pointer.clear_property("madeFromGrape")
        self.assertEqual(self.pointer.get_object_property("madeFromGrape"), [])

    def test_create_class_and_individual(self) -> None:
        cls = create_class(self.pointer.onto, "ReserveWine", (self.pointer.onto.Wine,))
        self.assertEqual(cls.name, "ReserveWine")

        ind = self.pointer.create_and_point("ReserveWine", "reserve_2024")
        self.assertEqual(self.pointer.get_name(), "reserve_2024")
        self.assertEqual(ind.name, "reserve_2024")

        ind2 = create_individual(self.pointer.onto, "ReserveWine", "reserve_2025")
        self.assertEqual(ind2.name, "reserve_2025")

        with self.assertRaises(ClassNotFoundError):
            self.pointer.create_and_point("MissingClass", "x")

    def test_property_not_found(self) -> None:
        self.pointer.goto_by_name("chateau_margaux")
        with self.assertRaises(PropertyNotFoundError):
            self.pointer.get_data_property("missingProperty")

    def test_save(self) -> None:
        self.pointer.goto_by_name("chateau_margaux")
        self.pointer.add_value("hasYear", 2020)
        out = os.path.join(self.tmpdir.name, "saved.owl")
        self.pointer.save(out)
        self.assertTrue(os.path.exists(out))


if __name__ == "__main__":
    unittest.main()

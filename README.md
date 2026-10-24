# Owl Pointer / 本体个体指针

English · [中文](#owl-pointer-中文)

Owl Pointer is a small Python package built on top of
[Owlready2](https://owlready2.readthedocs.io/) for working with individuals in
OWL ontology files (for example files saved by Protégé). The central object is
`IndividualPointer`, which keeps a reference (the pointer `p`) to one individual
in the ontology.

## Features / 功能

- Load a `.owl` file using `file://` plus an absolute path.
- Locate an individual by name (`goto_by_name`).
- Move the pointer along an object property (`goto_by_object_property`).
- Read data and object properties uniformly as Python `list`s.
- Add, remove, and clear property assertions.
- Create new individuals and new classes.
- Persist in-memory edits back to disk.
- A dedicated exception hierarchy (no bare `ValueError` / `RuntimeError`).

## Installation / 安装

Requirements: Python `>= 3.8` and `owlready2 >= 0.40`.

依赖：Python `>= 3.8`，`owlready2 >= 0.40`。

```bash
git clone <this-repository-url>
cd owl_pointer
pip install -e .
```

For a normal (non-editable) install, use `pip install .` instead of
`pip install -e .`.

如需普通安装（非开发模式），把 `pip install -e .` 换成 `pip install .`。

## Quick start / 快速开始

```python
from owl_pointer import IndividualPointer

# Load a Protégé-generated .owl file.
pointer = IndividualPointer("examples/mini_wine.owl")

# Locate an individual by name.
pointer.goto_by_name("chateau_margaux")
print(pointer.get_name())

# Reading always returns a list: [] for no value, [value] for functional.
print(pointer.get_data_property("hasName"))      # ['Chateau Margaux']
print(pointer.get_data_property("hasFlavor"))    # ['blackcurrant', 'cedar']
print(pointer.get_object_property("madeFromGrape"))

# Move along an object property (0-based index).
pointer.goto_by_object_property("madeFromGrape", 1)
print(pointer.get_name())  # 'merlot'

# Changes are in memory only; save to persist.
pointer.save()  # overwrite the original file
# or pointer.save("new.owl")
```

Run the full demo:

```bash
python examples/demo.py
```

## API reference / API 参考

### Constructors / 构造函数

| Callable / 可调用对象 | Signature / 签名 | Parameters / 参数 | Returns / 返回值 | Raises / 可能抛出的异常 |
| --- | --- | --- | --- | --- |
| `IndividualPointer` | `IndividualPointer(owl_path: str)` | `owl_path`: `.owl` file path | instance | loading errors from Owlready2 |

### `IndividualPointer` methods / 方法

| Method / 方法 | Signature / 签名 | Parameters / 参数 | Returns / 返回值 | Raises / 可能抛出的异常 |
| --- | --- | --- | --- | --- |
| `goto_by_name` | `goto_by_name(name: str) -> None` | `name`: individual name | `None` | `IndividualNotFoundError` |
| `goto_by_object_property` | `goto_by_object_property(prop_name: str, n: int = 0) -> None` | `prop_name`: object property; `n`: 0-based index | `None` | `PropertyNotFoundError`, `PointerEmptyError`, `IndexOutOfRangeError` |
| `get` | `get() -> owlready2.Thing` | none | the individual | `PointerEmptyError` |
| `get_name` | `get_name() -> str` | none | the individual name | `PointerEmptyError` |
| `get_iri` | `get_iri() -> str` | none | the individual IRI | `PointerEmptyError` |
| `get_data_property` | `get_data_property(prop_name: str) -> list` | `prop_name`: data property | values as a list (`[]` when empty) | `PropertyNotFoundError`, `PointerEmptyError` |
| `get_object_property` | `get_object_property(prop_name: str) -> list` | `prop_name`: object property | values as a list of individuals | `PropertyNotFoundError`, `PointerEmptyError` |
| `add_value` | `add_value(prop_name: str, value: Any) -> None` | `prop_name`: property; `value`: literal or `Thing` | `None` | `PropertyNotFoundError`, `PointerEmptyError`, `ValueTypeError` |
| `remove_value` | `remove_value(prop_name: str, value: Any) -> None` | `prop_name`: property; `value`: value to remove | `None` | `PropertyNotFoundError`, `PointerEmptyError` |
| `clear_property` | `clear_property(prop_name: str) -> None` | `prop_name`: property | `None` | `PropertyNotFoundError`, `PointerEmptyError` |
| `create_and_point` | `create_and_point(class_name: str, individual_name: str | None = None) -> owlready2.Thing` | `class_name`: existing class; `individual_name`: optional name | the new individual | `ClassNotFoundError` |
| `save` | `save(path: str | None = None) -> None` | `path`: optional output file | `None` | Owlready2 IO errors |

### Module-level functions / 全局函数

| Function / 函数 | Signature / 签名 | Parameters / 参数 | Returns / 返回值 | Raises / 可能抛出的异常 |
| --- | --- | --- | --- | --- |
| `create_individual` | `create_individual(onto, class_name, individual_name=None)` | `onto`: ontology; `class_name`: existing class; `individual_name`: optional name | the new individual | `ClassNotFoundError` |
| `create_class` | `create_class(onto, class_name, parent_classes=(Thing,))` | `onto`: ontology; `class_name`: new class name; `parent_classes`: tuple of parent classes | the new class | `TypeError` if `parent_classes` is not a tuple |

### Exceptions / 异常

| Exception / 异常 | Meaning / 含义 |
| --- | --- |
| `OwlPointerError` | Base class for all package errors |
| `PointerEmptyError` | The pointer `p` is empty when an operation needs it |
| `IndividualNotFoundError` | No individual matches the given name |
| `PropertyNotFoundError` | The ontology has no such property |
| `IndexOutOfRangeError` | Object-property value index is out of range |
| `ValueTypeError` | Object/data property value type mismatch |
| `ClassNotFoundError` | The ontology has no such class |

## Constraints / 约束说明

- **Uniform list return.** `get_data_property` and `get_object_property` always
  return a `list`: `[]` for no assertion and `[value]` for a functional single
  value. Callers never need to check whether a property is functional.
  **统一返回 list。** 两个读取方法永远返回 `list`：无断言返回 `[]`，Functional
  单值返回 `[value]`，调用方无需判断属性是否 Functional。

- **Order is not guaranteed.** OWL property assertions are unordered, so the
  order of the returned list must not be relied upon. If order matters, model it
  explicitly (for example with an `hasOrder` data property); this package does
  not handle ordering.
  **顺序不可依赖。** OWL 属性断言无序，返回 list 的顺序不应作为业务依据；需要
  顺序时请显式建模（如 `hasOrder`），本包不负责顺序。

- **Edits are in memory only.** Use `save()` (or `save(path)`) to write changes
  back to disk in RDF/XML format.
  **修改仅内存生效。** 需调用 `save()`（或 `save(path)`）以 RDF/XML 写回磁盘。

- **Same-name individuals are reused.** Owlready2 returns the existing
  individual for a repeated name; it does not create a duplicate. Call
  `search_one` before creation if you truly need a fresh individual.
  **同名个体不重复创建。** Owlready2 对同名个体返回已存在对象；确需新建时请先
  调用 `search_one` 检查。

- **Functional conflict semantics.** Conflicting values on a functional data
  property make the ontology inconsistent; conflicting object-property values
  imply `owl:sameAs`. The package performs only light type validation and does
  not run a reasoner.
  **Functional 冲突语义。** Functional 数据属性值冲突会导致本体不一致；对象属性
  值冲突会被推断为 `owl:sameAs`。本包只做粗粒度类型校验，不执行推理。

- **Ontology path.** Loading always uses `file://` plus the absolute path so a
  relative path is never interpreted as the ontology base IRI.
  **本体路径。** 加载时一律使用 `file:// + 绝对路径`，避免相对路径被解析为本体
  base IRI。

## Repository layout / 仓库结构

```text
owl_pointer/
├── pyproject.toml
├── README.md
├── owl_pointer/
│   ├── __init__.py
│   ├── pointer.py
│   ├── creators.py
│   └── exceptions.py
├── examples/
│   ├── demo.py
│   └── mini_wine.owl
└── tests/
    └── test_pointer.py
```

## Tests / 测试

```bash
python -m unittest discover -s tests
```

or with pytest:

```bash
pytest
```

---

# Owl Pointer 中文

Owl Pointer 是一个基于 [Owlready2](https://owlready2.readthedocs.io/) 的轻量
Python 包，用于操作 OWL 本体文件（例如 Protégé 生成的 `.owl`）中的个体。核心
对象是 `IndividualPointer`，它持有指向本体中某个个体的引用（指针 `p`）。

## 功能

- 使用 `file://` 加绝对路径加载 `.owl` 文件。
- 按名称定位个体（`goto_by_name`）。
- 沿对象属性移动指针（`goto_by_object_property`）。
- 以统一 `list` 形式读取数据属性与对象属性。
- 增删与清空属性断言。
- 创建新个体与新类。
- 将内存修改写回磁盘。
- 专属异常体系，不使用裸 `ValueError` / `RuntimeError`。

## 安装

依赖：Python `>= 3.8`，`owlready2 >= 0.40`。

```bash
cd owl_pointer
pip install -e .      # 开发模式
# 或 pip install .    # 普通安装
```

## 快速开始

```python
from owl_pointer import IndividualPointer

pointer = IndividualPointer("examples/mini_wine.owl")
pointer.goto_by_name("chateau_margaux")
print(pointer.get_name())

# 读取永远返回 list；无值返回 []，Functional 单值返回 [value]。
print(pointer.get_data_property("hasName"))
print(pointer.get_data_property("hasFlavor"))
print(pointer.get_object_property("madeFromGrape"))

# 沿对象属性移动指针（0-based）。
pointer.goto_by_object_property("madeFromGrape", 1)
print(pointer.get_name())

# 修改仅在内存中生效，调用 save() 才写回磁盘。
pointer.save()  # 覆盖原文件；或 pointer.save("new.owl")
```

运行完整示例：

```bash
python examples/demo.py
```

其余 API 参考、约束说明与测试方式见上文英文部分。

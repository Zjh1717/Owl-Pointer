# Examples / 示例

This directory contains the runnable demo for the `owl_pointer` package.

本目录包含 `owl_pointer` 软件包的可运行示例。

## demo.py

`demo.py` uses `IndividualPointer` to do the following:

1. load `state_machine_ontology.owl`;
2. walk the `Success` chain from `Step1_MoveAboveObject` to `IDLE`, printing
   each state's `Actions`;
3. insert a new `States` individual `Step3b_CustomAction` between
   `Step3_CloseGripper` and `Step4_LiftObject`;
4. save the result to `state_machine_ontology_modified.owl`;
5. reload the modified copy and walk it again to verify the insertion.

`demo.py` 使用 `IndividualPointer` 完成以下操作：

1. 加载 `state_machine_ontology.owl`；
2. 沿 `Success` 链从 `Step1_MoveAboveObject` 遍历到 `IDLE`，打印每一步的
   `Actions`；
3. 在 `Step3_CloseGripper` 与 `Step4_LiftObject` 之间插入新的 `States` 个体
   `Step3b_CustomAction`；
4. 把修改结果保存到 `state_machine_ontology_modified.owl`；
5. 重新加载修改后的副本并再次遍历，验证插入结果。

## Run / 运行

```bash
cd /path/to/owl_pointer
pip install -e .
python examples/demo.py
```

Requirements: Python >= 3.8 and `owlready2 >= 0.40`.

依赖：Python >= 3.8，`owlready2 >= 0.40`。

## Notes / 说明

- The demo only reads `examples/state_machine_ontology.owl` and never modifies
  it; edits are written to `examples/state_machine_ontology_modified.owl`.
- 示例只读取 `examples/state_machine_ontology.owl`，不会修改该文件；所有改动
  写入 `examples/state_machine_ontology_modified.owl`。
- The generated output file is ignored by git via the root `.gitignore`.
- 输出文件是运行生成物，已被根目录的 `.gitignore` 忽略。

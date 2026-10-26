"""
Walks the ``Success`` chain of ``state_machine_ontology.owl``, prints each
state's ``Actions``, inserts a new ``States`` individual between
``Step3_CloseGripper`` and ``Step4_LiftObject``, saves a modified copy, and
walks the chain again to verify the insertion.

Run from the repository root after ``pip install -e .``:
    python examples/demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from owl_pointer import IndividualPointer  # noqa: E402


def main() -> None:
    # 初始化要求添加.owl文件绝对路径
    here = Path(__file__).resolve().parent
    owl_path = str(here / "state_machine_ontology.owl")
    out_path = str(here / "state_machine_ontology_modified.owl")

    # 1. Load the ontology and point at the first state.
    # 加载本体并指向第一个状态。
    pointer = IndividualPointer(owl_path)
    pointer.goto_by_name("Step1_MoveAboveObject")

    print("initial individual:", pointer.get_name())

    # 2. Walk the Success chain until IDLE, printing Actions.
    # 沿 Success 链遍历到 IDLE，并打印 Actions。
    visited = set()
    while True:
        name = pointer.get_name()

        if name in visited:
            print("cycle detected at:", name)
            break
        visited.add(name)

        print("state:", name)
        for action in pointer.get_data_property("Actions"):
            print("    action:", action)

        # Read the next Success target without moving the pointer.
        # 读取下一个 Success 目标，但不移动指针。
        next_individuals = pointer.get_object_property("Success")
        if not next_individuals:
            print("    no Success target; walk ends")
            break

        # Move to the next state.
        # 移动到下一个状态。
        pointer.goto_by_object_property("Success", 0)
        if pointer.get_name() == "IDLE":
            # IDLE is the terminal state: print it and stop.
            # IDLE 是终点：打印后结束。
            print("state: IDLE")
            for action in pointer.get_data_property("Actions"):
                print("    action:", action)
            print("    back to IDLE; walk ends")
            break

    # 3. Insert a new individual between Step3_CloseGripper and Step4_LiftObject.
    # 在 Step3_CloseGripper 与 Step4_LiftObject 之间插入新个体。
    insert_before = "Step3_CloseGripper"
    original_next = "Step4_LiftObject"

    # 3.1 Create the new States individual and point to it.
    # 创建新的 States 个体，并让指针指向它。
    new_individual = pointer.create_and_point("States", "Step3b_CustomAction")
    print("created individual:", new_individual.name)

    # 3.2 Give it Actions and Success pointing to the original next state.
    # 为新个体设置 Actions，并让 Success 指向原下一步。
    pointer.add_value(
        "Actions",
        "/rizon4s/pick_place_waypoint_command : neo4j_msgs/Actions"
        "{type=CUSTOM, pose=(0.380,0.020,0.090,0.0,1.0,0.0,0.0), "
        "grasp_state=CLOSE, action_state=RUNNING}",
    )
    step4 = pointer.onto[original_next]
    pointer.add_value("Success", step4)
    print("new individual Success ->", original_next)

    # 3.3 Point Step3_CloseGripper at the new individual.
    # 将 Step3_CloseGripper 的 Success 改指向新个体。
    pointer.goto_by_name(insert_before)
    pointer.clear_property("Success")
    pointer.add_value("Success", new_individual)
    print(insert_before, "Success ->", new_individual.name)

    # 4. Save the modified ontology to a copy, leaving the source untouched.
    # 保存到副本，不覆盖原文件。
    pointer.save(out_path)
    print("saved:", out_path)

    # 5. Reload the copy and walk again to verify the insertion.
    # 重新加载副本并遍历验证插入结果。
    pointer2 = IndividualPointer(out_path)
    pointer2.goto_by_name("Step1_MoveAboveObject")
    seen = set()
    while True:
        name = pointer2.get_name()
        if name in seen:
            print("cycle detected at:", name)
            break
        seen.add(name)
        print("state:", name)
        next_individuals = pointer2.get_object_property("Success")
        if not next_individuals:
            break
        pointer2.goto_by_object_property("Success", 0)
        if pointer2.get_name() == "IDLE":
            print("state: IDLE (walk ends)")
            break

    print("demo finished successfully")


if __name__ == "__main__":
    main()

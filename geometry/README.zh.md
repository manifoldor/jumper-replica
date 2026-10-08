<!-- tracks: README.md @ sha256:b691f00b86fc3756b70f0423f2803edf5410a26fe0efb72b1744bb458e3c1279 -->

# 几何清单

此处衍生 STL / STEP 为毫米制，`assembly_home.glb` 为米制。原始米制网格保存在 `../upstream_snapshot/`。组件坐标仍为源 link 局部坐标，不是打印床摆放坐标。

- `links_mm/`：41 个完整 visual link，其中不少为复合总成。
- `components_mm/`：1,364 个边连通组件，保持面数；很多只是小细节，不能据此统计制造件数量。
- `seam_recovered_mm/`：13 个仅通过顶点合并闭合的实体，未补面或删面。
- `step_trials/`：46 个有效 AP214 分面 B-rep（33 个原始候选 / 经检查的安装板，加 13 个恢复实体）。转换验证不代表制造放行。
- `pilot_fit_set/`：首轮试装所选六个原件。
- `parts_manifest.csv`：源哈希、尺寸、质量与 HOME 世界坐标矩阵。
- `components_manifest.csv`：组件用途判断、状态、包络、局部坐标文件与哈希。
- `trial_candidates.csv`：32 个闭合源候选，标准文件均在 `components_mm/`。
- `joint_schedule.csv`：40 个关节的 HOME 值、轴和限位。
- `circular_rim_reference.csv`：741 条圆沿观测，不代表独立孔或螺纹。
- `upper_shell_mounting_reference.json`：源局部坐标安装观测，包括约 70 × 135 mm 主孔位。

原 visual 提取、顶点接缝恢复与 STEP 转换报告分别保存。提取报告中的“未切片”是历史阶段状态，后续六件参考切片见 `../printing/`。仍开口的主要几何在 `../catalog/annotated_groups.json` 中明确标记。

完整 link 与整机 STL 用于检查。实际打印应选择独立候选，并核对材料、工艺与设备；复合 link 可能包含舵机参考或其他内部件，不能整体照印。

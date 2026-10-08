<!-- tracks: LABELS.md @ sha256:285d7a364f242390b4a2af745f316b7e2bbc3bf41e50597592202d76f1b1c468 -->

# Jumper 结构爆炸图标注

基于仿真源几何与反推组件 · 装配展开示意

源中尚未闭合的曲面仅作为几何参考，不等于可打印成品。A/B 表示拆分出的组件，不指定内外位置；左、右以机器人自身为准。本表标识渲染分组，不是经过确认的制造物料清单。

| ID | Source ID | Label |
|---|---|---|
| 01A | `base_link__C001` | 下壳 / 周向框架 |
| 01B | `base_link__C002` | 内部承载安装板 |
| 01C | `base_link__C003` | 内部托架（功能待确认） |
| 01R | `base_link__remaining` | 其他内部组件参考 |
| 02 | `upper_shell_link` | 上壳 |
| 03 | `display_module_link` | 显示模块参考 |
| 04 | `tof_sensor_link` | ToF 传感模块参考 |
| 05 | `camera_link` | 摄像头模块参考 |
| 06A | `LF_shoulder_link__C001` | 左前 · 肩部壳体 A |
| 06B | `LF_shoulder_link__C002` | 左前 · 肩部壳体 B |
| 07A | `LF_upper_arm_link__C001` | 左前 · 上臂壳体 A |
| 07B | `LF_upper_arm_link__C002` | 左前 · 上臂壳体 B |
| 08A | `LF_forearm_link__C001` | 左前 · 前臂连接结构 A |
| 08B | `LF_forearm_link__C002` | 左前 · 前臂连接结构 B |
| 09A | `LF_palm_link__C001` | 左前 · 掌部壳体 A |
| 09B | `LF_palm_link__C002` | 左前 · 掌部壳体 B |
| 10 | `LF_palm_pad_f_link` | 左前 · 掌部垫块 f |
| 11 | `LF_palm_pad_b_link` | 左前 · 掌部垫块 b |
| 12A | `LF_finger_link__C001` | 左前 · 活动指结构 A |
| 12B | `LF_finger_link__C002` | 左前 · 活动指结构 B |
| 13 | `LF_finger_tip_link` | 左前 · 指尖 |
| 14 | `LF_finger_grip_insert_link` | 左前 · 活动指夹持嵌件 |
| 15 | `LF_palm_grip_insert_link` | 左前 · 掌部夹持嵌件 |
| 16A | `RF_shoulder_link__C001` | 右前 · 肩部壳体 A |
| 16B | `RF_shoulder_link__C002` | 右前 · 肩部壳体 B |
| 17A | `RF_upper_arm_link__C001` | 右前 · 上臂壳体 A |
| 17B | `RF_upper_arm_link__C002` | 右前 · 上臂壳体 B |
| 18A | `RF_forearm_link__C001` | 右前 · 前臂连接结构 A |
| 18B | `RF_forearm_link__C002` | 右前 · 前臂连接结构 B |
| 19A | `RF_palm_link__C001` | 右前 · 掌部壳体 A |
| 19B | `RF_palm_link__C002` | 右前 · 掌部壳体 B |
| 20 | `RF_palm_pad_f_link` | 右前 · 掌部垫块 f |
| 21 | `RF_palm_pad_b_link` | 右前 · 掌部垫块 b |
| 22 | `RF_palm_grip_insert_link` | 右前 · 掌部夹持嵌件 |
| 23A | `RF_finger_link__C001` | 右前 · 活动指结构 A |
| 23B | `RF_finger_link__C002` | 右前 · 活动指结构 B |
| 24 | `RF_finger_grip_insert_link` | 右前 · 活动指夹持嵌件 |
| 25 | `RF_finger_tip_link` | 右前 · 指尖 |
| 26A | `LM_hip_link__C001` | 左中 · 髋部壳体 A |
| 26B | `LM_hip_link__C002` | 左中 · 髋部壳体 B |
| 27A | `LM_thigh_link__C001` | 左中 · 大腿连接结构 A |
| 27B | `LM_thigh_link__C002` | 左中 · 大腿连接结构 B |
| 28A | `LM_calf_link__C001` | 左中 · 小腿壳体 A |
| 28B | `LM_calf_link__C002` | 左中 · 小腿壳体 B |
| 29 | `LM_foot_tip_link` | 左中 · 足端垫 |
| 30A | `RM_hip_link__C001` | 右中 · 髋部壳体 A |
| 30B | `RM_hip_link__C002` | 右中 · 髋部壳体 B |
| 31A | `RM_thigh_link__C001` | 右中 · 大腿连接结构 A |
| 31B | `RM_thigh_link__C002` | 右中 · 大腿连接结构 B |
| 32A | `RM_calf_link__C001` | 右中 · 小腿壳体 A |
| 32B | `RM_calf_link__C002` | 右中 · 小腿壳体 B |
| 33 | `RM_foot_tip_link` | 右中 · 足端垫 |
| 34A | `LR_hip_link__C001` | 左后 · 髋部壳体 A |
| 34B | `LR_hip_link__C002` | 左后 · 髋部壳体 B |
| 35A | `LR_thigh_link__C001` | 左后 · 大腿连接结构 A |
| 35B | `LR_thigh_link__C002` | 左后 · 大腿连接结构 B |
| 36A | `LR_calf_link__C001` | 左后 · 小腿壳体 A |
| 36B | `LR_calf_link__C002` | 左后 · 小腿壳体 B |
| 37 | `LR_foot_tip_link` | 左后 · 足端垫 |
| 38A | `RR_hip_link__C001` | 右后 · 髋部壳体 A |
| 38B | `RR_hip_link__C002` | 右后 · 髋部壳体 B |
| 39A | `RR_thigh_link__C001` | 右后 · 大腿连接结构 A |
| 39B | `RR_thigh_link__C002` | 右后 · 大腿连接结构 B |
| 40A | `RR_calf_link__C001` | 右后 · 小腿壳体 A |
| 40B | `RR_calf_link__C002` | 右后 · 小腿壳体 B |
| 41 | `RR_foot_tip_link` | 右后 · 足端垫 |

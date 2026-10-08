<!-- tracks: REPRODUCTION.md @ sha256:14101751dffefaf82f6f8bf9283707d19488caffdb487a2108ee368e75be26a9 -->

# 独立复现

所附精选快照已满足这些几何脚本，不需要导入训练包，也不依赖原仓库所在目录。Python 3.12 配合 `requirements-geometry.txt` 对应分析环境；离线验证器只使用标准库。

```sh
python3 tools/validate_release.py
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-geometry.txt
.venv/bin/python tools/reverse_engineer_jumper.py
.venv/bin/python tools/recover_mesh_seams.py
.venv/bin/python tools/reverse_engineer_step.py
.venv/bin/python tools/reverse_engineer_step.py --seams-only
.venv/bin/python tools/render_reverse_geometry.py
```

首条命令不修改参考成果，仅写入验证报告，其余生成命令会写入各自目录并替换衍生成果；实验时使用目录副本或 Git 分支。设置 `JUMPER_GEOMETRY_DIR=/tmp/jumper-probe` 可将提取脚本输出隔离，和已有快照比较。STEP 回读需要 OpenCascade，可选依赖已固定其版本。

## 样件与切片

```sh
.venv/bin/python tools/prepare_pilot_prints.py
.venv/bin/python tools/slice_pilot_reference.py /path/to/PrusaSlicer
.venv/bin/python tools/embed_pilot_configs.py
.venv/bin/python tools/validate_pilot_projects.py
.venv/bin/python tools/inspect_pilot_toolpaths.py
.venv/bin/python tools/render_pilot_prints.py
```

参考切片器为 PrusaSlicer 2.9.6，脚本接受可执行文件路径，不安装或打包切片器。项目写入 `printing/slicer/`，仅供检查的 G-code 写入 `experiments/reference_gcode/`；原始 G-code 与运行日志是本地产物，被 Git 和公开清单忽略；公开包仅保留切片证据和哈希。采用通用参考配置，实际设备起止程序留待设置。

## 爆炸场景与标注

```sh
.venv/bin/python tools/prepare_exploded_scene.py
/path/to/Blender --background --factory-startup --python tools/render_exploded_blender.py
.venv/bin/python tools/compose_exploded_poster.py
```

参考渲染器为 Blender 4.5.9 LTS / Cycles / 48 次采样，已在 Apple M4 Metal GPU 验证；可以退回 CPU，但不同后端不保证逐像素一致。加 `-- --draft` 可输出快速草图。`.blend` 使用相对渲染路径，不依赖外部纹理。

排版默认读取双语 Markdown 名录和 macOS 字体；其他平台请通过 `JUMPER_CJK_FONT`、`JUMPER_SANS_FONT`、`JUMPER_MONO_FONT` 指定有权使用的字体，本包不分发字体。必要时设置 `MPLCONFIGDIR`、`XDG_CACHE_HOME` 到可写缓存目录。

不得静默修改上游快照。更换源版本需要同步更新哈希、几何证据、目录及说明。重新生成会使成果清单失效；审阅变更后运行 `tools/refresh_manifest.py`，再运行 `tools/validate_release.py`。哈希通过不能代替几何或实体验证。

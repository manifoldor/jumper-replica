<!-- tracks: LICENSING.md @ sha256:51bbdee81b9aa6e59f5fb3a8f0a2d6bb52f11f80f4f48eeb7187dbfa6567f872 -->

# 许可与来源

顶层 Apache-2.0 明确用于 Jumper Replica 新增脚本、文档、图注与渲染成果。这是本项目的许可选择，不是假定生成成果自动继承上游许可证。

上游声明维护者拥有的材料采用 Apache-2.0，第三方材料保留各自条款。精选源文件在 `upstream_snapshot/` 中保持原哈希与声明；`source_manifest.json` 逐项链接至固定提交。精选机器人网格 / URDF 快照中未发现单独许可覆盖条款。衍生几何保留适用的仓库署名，并在 `NOTICE` 和 `provenance/artifact_manifest.json` 中显著说明变更。

变更包括连通组件拆分、米转毫米、仅顶点焊接、分面 STEP 转换、打印刚体摆放、爆炸平移与标注渲染，不是原厂 CAD。完整上游 NOTICE 作为来源记录归档；其中训练依赖的声明不表示本包包含那些库。

厂商 TS20 STEP 曾用于独立尺寸调查，但再分发条款未确认，因此不纳入公开准备包，只保留 `external_references/TS20-50-TS20-100.json` 的链接、校验值与测量包络。场景未使用该厂商 CAD 替换源执行器。独立 jumper-design 的 LFS CAD 包未下载，也不分发。

不打包 Blender、PrusaSlicer、Python 库、系统字体、固件镜像或第三方程序；版本声明仅用于用户自己的安装，各依赖保留其许可。图片含渲染文字，不含字体文件。项目不声明厂商背书、商标授权、原厂制造放行或硬件认证。

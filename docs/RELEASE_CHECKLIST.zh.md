<!-- tracks: RELEASE_CHECKLIST.md @ sha256:427de90c692adeb735ba7e78bb5365f03cb6831ccb7aeb6ded138cd0c4ba2b10 -->

# 公开发布准备

发布目标：https://github.com/manifoldor/jumper-replica。每次公开推送前，应审阅实际文件并运行标准库验证器。

- 保留 `LICENSE`、`NOTICE`、精选源哈希及显著衍生变更说明。
- 确认没有厂商 STEP、切片器 / 渲染器程序、字体、缓存、本地环境或凭据。
- 核验标准几何哈希、STEP 证据、66 个标注对应、六个 3MF、译文哈希与相对 Markdown 链接。
- 主 README 保持突出展示初步实体状态与未解决接口。
- 检查 Blender 渲染路径为相对路径，脚本只依赖当前目录。
- 推送前检查文件大小报告。本次采用普通 Git；是否使用 LFS 以实际托管要求决定。
- 修改后重新运行 `python3 tools/validate_release.py`，CI 使用同一完整性检查。

建议发布描述为“首版几何反推与试装参考”，不要称为完整制造套件。公开仓库 / 远程和上传应在得到发布授权后进行；项目所有者已明确授权首次公开推送。

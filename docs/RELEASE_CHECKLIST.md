# Public-release preparation

Publication target: https://github.com/manifoldor/jumper-replica. Review the concrete files and run the standard-library validator before each public push.

- Keep `LICENSE`, `NOTICE`, selected source hashes and prominent derivative change notices.
- Confirm that vendor STEP, slicer/renderer binaries, fonts, caches, local environments and credentials are absent.
- Verify canonical geometry hashes, STEP evidence, 66 annotation mappings, six 3MF archives, translation digests and relative Markdown links.
- Keep the preliminary physical status and unresolved interfaces visible in the main README.
- Check that the Blender render path is relative and the scripts operate from this directory alone.
- Review the file-size report before pushing; binary assets use ordinary Git in this preparation. Decide on Git LFS only if the actual hosting requirements justify it.
- Re-run `python3 tools/validate_release.py` after changes. CI runs the same integrity checks.

Use a release description such as "Initial geometry-recovery and fit-reference release". Do not market it as a complete manufacturing kit. Create the public repository/remote and upload only when publication is authorized. The initial public push was explicitly authorized by the project owner.

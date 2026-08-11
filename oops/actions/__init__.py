"""
OOPS 动作子命令包(mirror / sync / self-update)

与 detectors/ 平级,承载会改变仓库或文件状态的「写操作」。
默认无参运行 oops 仍是只读预检;这些命令仅在被显式调用时执行,
不破坏 OOPS 既有的「只读」承诺。
"""

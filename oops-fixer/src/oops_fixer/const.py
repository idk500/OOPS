"""OneDragon-Oops 急救器常量

所有可调整的配置集中在这里,方便后续维护。
"""

from __future__ import annotations

from pathlib import Path

# 项目标识文件:兜底修复器要求必须放在项目根目录执行
PROJECT_MARKER_FILES: tuple[str, ...] = ('OneDragon-Launcher.exe', 'OneDragon-RuntimeLauncher.exe')
PROJECT_MARKER_DIRS: tuple[str, ...] = ('config', 'assets', '.git')

# 主仓库(CNB 是国内源,内地可直连;GitHub 需要代理不稳定)
CNB_CLONE_URL: str = 'https://cnb.cool/OneDragon-Anything/ZenlessZoneZero-OneDragon.git'
CNB_RELEASE_DOWNLOAD_BASE: str = (
    'https://cnb.cool/OneDragon-Anything/ZenlessZoneZero-OneDragon/-/releases/download'
)

# 主分支名:兜底修复器固定切到主分支
PRIMARY_BRANCH: str = 'main'

# 启动器相关文件:两种形态,按 .venv 是否存在选择更新目标
# - 原始启动器:依赖项目 .venv(外部 Python 环境)
# - 集成启动器:自带 Python 运行时,不需要 .venv
LAUNCHER_EXE_NAME: str = 'OneDragon-Launcher.exe'
LAUNCHER_ZIP_NAME: str = 'ZenlessZoneZero-OneDragon-Launcher.zip'
RUNTIME_LAUNCHER_EXE_NAME: str = 'OneDragon-RuntimeLauncher.exe'
RUNTIME_LAUNCHER_ZIP_NAME: str = 'ZenlessZoneZero-OneDragon-RuntimeLauncher.zip'
# 旧启动器的备份后缀(与主程序「资源下载」页备份逻辑一致)
LAUNCHER_BACKUP_SUFFIX: str = '.bak'

# oops 图标(窗口图标和 exe 图标都使用它)
OOPS_ICON_RELATIVE_PATH: tuple[str, ...] = ('assets', 'ui', 'oops.ico')

# 日志文件名(持久记录,远程排查用)
LOG_FILE_NAME: str = 'OneDragon-Oops.log'

# 日志「结果协议」:每轮运行结束写一行结果;成功后整个日志会被删除,
# 因此「日志存在且末轮没有 RESULT: OK」= 上次失败 = 下次启动进入完全重置模式。
# 横幅带协议版本标记:旧版工具留下的日志(无此横幅)不触发重置,避免升级用户误重置。
RUN_BANNER: str = '======== OneDragon-Oops 启动 [protocol-v2] ========'
RESULT_OK_LINE: str = 'RESULT: OK'
RESULT_FAILED_LINE: str = 'RESULT: FAILED'

# 完全重置:全量环境包名模板(CNB release 资产,tag 形如 v2.5.1)
FULL_ENV_ZIP_TEMPLATE: str = 'ZenlessZoneZero-OneDragon-{tag}-Full-Environment.zip'
# 重置新目录后缀格式:D:\ZZZ1D -> D:\ZZZ1D_0819
RESET_DIR_SUFFIX_FORMAT: str = '%m%d'
# 重置前磁盘空间预检:目标盘剩余空间至少为压缩包体积的该倍数(解压+环境膨胀)
RESET_DISK_SPACE_FACTOR: float = 3.0

# 重置时迁移的用户配置(config 根下、非 git 跟踪的用户数据;env.yml 会做路径改写)
USER_CONFIG_FILES: tuple[str, ...] = (
    'env.yml',
    'one_dragon.yml',
    'pip.yml',
    'push.yml',
    'telemetry.yml',
    'custom.yml',
    'model.yml',
)
# 重置时最多迁移的账户目录数(config/01、config/02...),其余不迁移
USER_ACCOUNT_DIR_PATTERN: str = r'^\d{2}$'
USER_ACCOUNT_MAX: int = 2

# 完成后打开的页面(完整版 oops 工具)
DONE_URL: str = 'https://cnb.cool/zzz1d/oops'

# 网络超时(秒)
NETWORK_TIMEOUT: float = 30.0
DOWNLOAD_TIMEOUT: float = 300.0
GIT_OPERATION_TIMEOUT: float = 300.0
# 虚拟环境创建/依赖安装单命令超时(秒);pip 源兜底(读不到用户配置时用)
VENV_OPERATION_TIMEOUT: float = 900.0
DEFAULT_PIP_SOURCE: str = 'https://mirrors.aliyun.com/pypi/simple'

# 倒计时秒数:双击运行后等待这么久才真正开始执行
COUNTDOWN_SECONDS: int = 5

# 项目根目录(兜底修复器所在目录,由 main 启动时设置)
PROJECT_ROOT: Path | None = None

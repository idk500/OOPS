# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# 获取项目根目录（spec 文件在 build/config/ 下）
spec_root = os.path.abspath(os.path.join(SPECPATH, '..', '..'))
sys.path.insert(0, spec_root)

block_cipher = None

# 收集所有需要的数据文件
datas = [
    (os.path.join(spec_root, 'configs'), 'configs'),
    (os.path.join(spec_root, 'docs', 'knowledge_base'), 'docs/knowledge_base'),
]

# 收集所有隐藏导入
hiddenimports = [
    'oops.core.config',
    'oops.core.diagnostics',
    'oops.core.report',
    'oops.core.report_modules',
    'oops.core.data_models',
    'oops.core.html_renderer',
    'oops.core.project_detector',
    'oops.detectors.network',
    'oops.detectors.environment',
    'oops.detectors.system_info',
    'oops.detectors.paths',
    'oops.validators.path_validator',
    'oops.knowledge.issue_matcher',
    'aiohttp',
    'yaml',
    'psutil',
    'requests',
    'urllib3',
    'colorama',
]

a = Analysis(
    [os.path.join(spec_root, 'oops.py')],
    pathex=[spec_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
        'PyQt5',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='oops',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(spec_root, 'oops.ico'),  # OOPS 图标
    version_file=None,
)

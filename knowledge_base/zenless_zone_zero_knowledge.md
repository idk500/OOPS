# 绝区零一条龙知识库

基于历史客服问题总结和网络连通性测试数据，整理的系统性知识库。

## 📋 项目基本信息

### 项目标识
- **项目ID**: `zenless_zone_zero`
- **项目名称**: 绝区零一条龙
- **项目类型**: `game_script`
- **描述**: 绝区零游戏的自动化脚本工具

### 仓库信息
- **GitHub主仓库**: https://github.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git
- **Gitee镜像**: https://gitee.com/xxx/ZenlessZoneZero-OneDragon.git
- **相关项目**: 
  - 千机链: https://github.com/OneDragon-Anything/StarRailOneDragon
  - 项目主页: https://one-dragon.com/sr/zh/home.html

## 🌐 网络连通性配置

### PyPI源配置
```yaml
pypi_sources:
  - name: "默认PyPI源"
    url: "https://pypi.org/simple/"
    timeout: 10
    recommended: true
    
  - name: "清华大学PyPI镜像源" 
    url: "https://pypi.tuna.tsinghua.edu.cn/simple/"
    timeout: 10
    fallback: true
    
  - name: "阿里云PyPI镜像源"
    url: "https://mirrors.aliyun.com/pypi/simple/"
    timeout: 10
    fallback: true
```

### 项目相关URL
```yaml
project_urls:
  - name: "米哈游游戏信息API"
    url: "https://api-takumi.mihoyo.com/"
    timeout: 5
    
  - name: "米哈游基础信息API" 
    url: "https://api-os-takumi.mihoyo.com/"
    timeout: 5
    
  - name: "公告通知URL"
    url: "https://one-dragon.com/zzz/zh/docs/feat_one_dragon.html"
    timeout: 10
    
  - name: "快速开始文档"
    url: "https://docs.qq.com/doc/p/7add96a4600d363b75d2df83bb2635a7c6a969b5"
    timeout: 10
    
  - name: "项目主页"
    url: "https://one-dragon.com/"
    timeout: 10
    
  - name: "腾讯文档"
    url: "https://docs.qq.com/"
    timeout: 10
```

### GitHub代理配置
```yaml
github_proxies:
  - name: "ghproxy"
    url: "https://ghproxy.com/"
    timeout: 30
    
  - name: "github.moeyy.xyz"
    url: "https://github.moeyy.xyz/"
    timeout: 15
    
  - name: "ghfast.top"
    url: "https://ghfast.top/"
    timeout: 15
    
  - name: "ghfile.geekertao.top"
    url: "https://ghfile.geekertao.top/"
    timeout: 15
```

## ⚠️ 安装路径要求

### 路径规范
```yaml
path_requirements:
  allowed_chars: "a-zA-Z0-9_-"
  max_length: 100
  recommended_paths:
    - "D:\\ZZZ-OD"
    - "C:\\Games\\ZZZ-OD"
  
  restrictions:
    - type: "no_chinese_chars"
      description: "路径不能包含中文字符"
      
    - type: "no_spaces" 
      description: "路径不能包含空格"
      
    - type: "not_too_long"
      description: "路径不能过长"
      
    - type: "no_admin_required"
      description: "不要放在需要管理员权限的目录"
```

## 🔧 环境依赖检测

### Python环境要求
```yaml
python_requirements:
  min_version: "3.8"
  recommended_version: "3.9+"
  virtual_env_types:
    - "venv"
    - "virtualenv"
    - "conda"
    
  required_packages:
    - "PySide6"
    - "onnxruntime==1.18.0"
    - "opencv-python"
    - "requests"
```

### 系统依赖
```yaml
system_dependencies:
  windows:
    - name: "Microsoft Visual C++"
      description: "动态链接库依赖"
      download_url: "https://aka.ms/vs/17/release/vc_redist.x64.exe"
      
    - name: "PowerShell"
      description: "脚本执行环境"
      required: true
      
    - name: "Git"
      description: "代码版本管理"
      required: true
```

### 网络代理配置
```yaml
proxy_settings:
  options:
    - name: "无代理"
      description: "适合海外用户或选择gitee的用户"
      recommended: true
      
    - name: "个人代理"
      description: "适合有计算机能力的用户"
      
    - name: "Github代理"
      description: "适合能通过代理顺利连接Github的用户"
      config_example: "http://127.0.0.1:8080"
```

## 🎮 游戏设置检测

### 分辨率要求
```yaml
resolution_requirements:
  aspect_ratio: "16:9"
  recommended_resolutions:
    - "1920x1080"
    - "2560x1440"
    
  window_mode: "窗口模式"
  fullscreen_requirements:
    - "屏幕分辨率和游戏分辨率必须都是16:9"
    - "多屏幕需要将游戏窗口放在1号屏"
```

### 显示设置限制
```yaml
display_restrictions:
  system_level:
    - "windows系统的颜色配置文件"
    - "校准显示器颜色"
    - "颜色管理"
    - "HDR"
    
  driver_level:
    - "显卡驱动控制面板里的游戏滤镜"
    
  device_level:
    - "显示器的夜间模式"
    - "护眼模式"
    - "色彩模式"
    - "色温调节"
    - "HDR"
```

### 游戏配置
```yaml
game_configuration:
  frame_rate:
    recommendation: "不要设置无限帧"
    
  mods:
    allowed: false
    description: "不要使用MOD"
    
  international_server:
    requirement: "需要在【账户设置】中更改区服后使用"
    
  controller_support:
    required_drivers: ["XBOX", "DS4"]
    installation: "在安装器里安装手柄驱动依赖"
```

## 🐛 常见问题知识库

### 安装问题
```yaml
installation_issues:
  - error_code: "WinError 10060"
    description: "连接时间超时"
    solutions:
      - "返回安装过程的上一步，卸载所选文件夹中安装的所有文件，重新安装"
      
  - error_code: "404/程序已退出，状态码: 1"
    description: "版本过老"
    solutions:
      - "去换新版本脚本"
      
  - error_code: "WinError 10061/403"
    description: "连接服务器被拒绝"
    solutions:
      - "使用管理员权限运行安装程序"
      - "关闭个人代理（如steam++，UU加速器, 雷神加速器等）"
      - "更换手机热点再试"
      - "用最新版的 FULL-ENV.zip 再次安装"
      
  - error_code: "WinError 87"
    description: "参数错误"
    solutions:
      - "关闭杀毒软件后使用安装器检查Python文件完整性"
      - "使用管理员权限启动启动器"
      - "检查Windows版本是否支持（Win10+）"
      
  - error_code: "os error 3"
    description: "路径问题"
    solutions:
      - "安装路径应为纯英文字符，且不含有空格"
      
  - error_code: "onnxruntime"
    description: "ONNX运行时错误"
    solutions:
      - "打开debug.bat，修复onnxruntime"
      
  - error_code: "file name too long"
    description: "文件路径过长"
    solutions:
      - "另寻文件夹安装"
      
  - error_code: "ssl"
    description: "SSL证书错误"
    solutions:
      - "启动debug.bat修复ssl证书"
      - "删除program files/Git整个文件夹"
      
  - error_code: "Darwin"
    description: "兼容性错误"
    solutions:
      - "更换个人热点解决校园网问题"
      
  - error_code: "WinError 2"
    description: "系统找不到指定的文件"
    solutions:
      - "检查Powershell权限和环境是否完整"
      - "添加环境变量 C:\\Windows\\System32\\WindowsPowerShell\\v1.0"
      
  - error_code: "PySide6"
    description: "界面库错误"
    solutions:
      - "删除.env文件夹之后重新进行安装流程"
      
  - error_code: "DLL初始化例程失败"
    description: "依赖库缺失"
    solutions:
      - "安装最新版的 Microsoft Visual C++"
```

### 使用问题
```yaml
usage_issues:
  - issue: "未找到 按键-普通攻击"
    cause: "游戏画面还在加载"
    solution: "等待游戏加载完成"
    
  - issue: "报错关键词'items'"
    solution: "打开设置-脚本环境-ocr缓存，关闭缓存"
    
  - issue: "报错关键词no attribute data"
    solution: "重启脚本"
    
  - issue: "Python路径错误"
    solution: "安装完成后，绝对路径固定，不可移动脚本内容"
    
  - issue: "运行时切换 全屏/窗口 (Alt+Enter) 后不能识别"
    solution: "还原设置,重新运行一条龙即可"
    
  - issue: "闪避助手的闪避反击操作不正常"
    cause: "脚本优先执行键鼠操作，键鼠的操作可能会把脚本的操作给覆盖掉"
    
  - issue: "体力计划，计划无法执行/执行报错"
    solution: "配置好体力计划后，重启一条龙脚本"
    
  - issue: "自动战斗只会闪避/不攻击只挨打"
    solution: "使用通用战斗配置"
    
  - issue: "自动战斗不会切人"
    solutions:
      - "尝试全屏模式开启自动战斗"
      - "保证绝区零游戏界面在前台，并关闭弹窗等遮挡"
      - "移除mod"
      - "新角色和新皮肤可能未适配，请耐心等待"
    
  - issue: "自动空洞内交互时冲刺"
    solutions:
      - "提高自动截图频率"
      - "换用低速/小个头角色"
      - "调高游戏分辨率"
      - "换个性能好的电脑"
```

## 💻 硬件配置要求

### 最低配置
```yaml
minimum_requirements:
  pc:
    cpu: "第七代英特尔酷睿i5"
    memory: "8G内存"
    gpu: "英伟达GeForce GTX970及以上"
    
  script_requirements:
    desktop:
      cpu: "第八代英特尔酷睿i5及以上"
      memory: "8G内存及以上"
      gpu: "英伟达GeForce GTX1060及以上"
      
    laptop:
      cpu: "第十二代英特尔酷睿i5及以上"
      memory: "8G内存及以上"
      gpu: "英伟达GeForce GTX1060及以上"
      
  storage:
    recommendation: "使用固态硬盘(SSD)"
    restrictions: "机械硬盘(HDD)可能会发生运行异常"
```

### 性能优化建议
```yaml
performance_optimization:
  - "游戏画质越好，脚本出错的几率越低"
  - "确保游戏画面完整在屏幕内，且游戏画面没有任何遮挡"
  - "不要开启会改变画面像素值的功能或设置"
  - "E3等更低的配置算力不够/缺少指令集，无法保证逻辑流畅运行"
```

## 🔄 更新和维护

### 更新配置
```yaml
update_configuration:
  git_options:
    - name: "Github"
      description: "适合有个人网络代理的用户"
      
    - name: "gitee"
      description: "适合国内用户"
      recommended: true
      
  launcher_update:
    steps:
      - "打开设置，找到资源下载，更新启动器"
      - "前往Github下载单独的Launcher.zip替换原根目录启动器"
      
  forced_update:
    method: "使用最新版安装器覆盖安装"
    limitation: "仅适用于同一大版本"
```

## 🛠️ 调试和故障排除

### 调试指令
```yaml
debug_commands:
  - command: "conda config --set auto_activate_base false"
    description: "关闭自动激活base环境"
    
  - command: "conda deactivate"
    description: "退出base环境"
    
  - command: "git clone https://github.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git"
    description: "克隆git仓库"
    
  - command: "C:\\ZenlessZoneZero-OneDragon\\.env\\venv\\scripts\\python.exe -m pip install --upgrade pip"
    description: "更新pip"
    
  - command: "git config --global --add safe.directory C:/ZenlessZoneZero-OneDragon"
    description: "授权目录权限"
    
  - command: "ssh-keygen -t rsa"
    description: "创建ssh密钥"
    
  - command: "ssh -T git@github.com"
    description: "添加ssh信任"
    
  - command: "git config --global http.postBuffer 2147483648"
    description: "重新设置缓存区"
    
  - command: "pip install onnxruntime==1.18.0"
    description: "修复onnxruntime报错"
    
  - command: "path环境变量添加C:\\Windows\\System32"
    description: "修复缺失cmd"
```

### 日志和诊断
```yaml
diagnostic_information:
  log_files:
    - path: ".log/log.txt"
      description: "脚本运行日志"
      
    - path: ".debug/images/"
      description: "游戏截图保存位置"
      
  screenshot_shortcut: "F11"
  required_info_for_support:
    - "安装器截图"
    - "命令行截图"
    - "已进行的操作"
    - "脚本日志"
    - "游戏截图"
```

## 📁 文件结构参考

### 脚本位置
```yaml
file_structure:
  config_directory: "ZZZ-OneDragon\\config\\"
  config_subdirectories:
    - "auto_battle\\ - 通用战斗脚本"
    - "auto_battle_operation\\ - 角色攻击模板"
    - "auto_battle_state_handler\\ - 角色战斗模板"
    - "dodge\\ - 闪避模板"
    - "hollow_zero_challenge\\ - 空洞模板"
    
  assets_directory: "ZZZ-OneDragon\\assets\\models\\"
  assets_subdirectories:
    - "flash_classifier\\ - 闪光识别"
    - "hollow_zero_event\\ - 空洞格子识别"
    - "lost_void_det\\ - 迷失之地识别"
    - "onnx_ocr\\ - OCR识别"
```

---

**最后更新**: 基于历史客服问题总结和网络连通性测试数据整理

**数据来源**: 
- `dev/ref/sample.txt` - 客服问题总结
- `dev/ref/connectivity_test_report.json` - 网络连通性测试报告
- `dev/ref/debug.bat` - 调试脚本参考
# 游戏设置检测YAML配置模板

## 概述

基于历史经验和项目需求，提供完整的游戏设置检测YAML配置模板，支持多种检测策略和验证规则。

## 🎯 配置结构

### 完整配置模板
```yaml
# projects/zenless_zone_zero.yaml - 游戏设置检测部分
game_settings:
  enabled: true
  config:
    # 检测策略配置
    detection_strategies:
      yolo:
        enabled: true
        model_path: "assets/models/yolo/game_ui_detector.pt"
        confidence_threshold: 0.6
        target_classes:
          - "settings_icon"
          - "resolution_option"
          - "frame_rate_option"
          - "window_mode_option"
          
      image_recognition:
        enabled: true
        similarity_threshold: 0.8
        templates:
          settings_icon: "assets/templates/settings_icon.png"
          resolution_1080p: "assets/templates/resolution_1080p.png"
          resolution_1440p: "assets/templates/resolution_1440p.png"
          frame_rate_60: "assets/templates/frame_rate_60.png"
          frame_rate_120: "assets/templates/frame_rate_120.png"
          window_mode: "assets/templates/window_mode.png"
          fullscreen_mode: "assets/templates/fullscreen_mode.png"
          
      coordinate_fallback:
        enabled: true
        fallback_coordinates:
          settings_icon:
            click_point: [100, 200]
            verify_point: [100, 200]
          resolution_setting:
            click_point: [500, 300]
            dropdown_point: [600, 350]
          frame_rate_setting:
            click_point: [500, 400]
            dropdown_point: [600, 450]
          window_mode_setting:
            click_point: [500, 500]
            dropdown_point: [600, 550]
    
    # 导航步骤定义
    navigation_steps:
      - name: "打开设置菜单"
        description: "点击游戏主界面的设置图标"
        action: "click"
        target:
          type: "icon"
          description: "设置图标"
          # 多策略检测配置
          detection:
            yolo:
              target_class: "settings_icon"
            image_recognition:
              template_name: "settings_icon"
            coordinate_fallback:
              click_point: [100, 200]
          validation:
            type: "screen_change"
            expected_change: "settings_menu_opened"
        timeout: 10
        retry: 3
        retry_delay: 2
        
      - name: "选择显示设置"
        description: "在设置菜单中选择显示选项"
        action: "click"
        target:
          type: "text"
          description: "显示选项"
          detection:
            yolo:
              target_class: "display_option"
            image_recognition:
              template_name: "display_option"
            coordinate_fallback:
              click_point: [300, 250]
          validation:
            type: "text_detection"
            expected_text: ["显示", "Display"]
        timeout: 5
        retry: 2
        retry_delay: 1
        
      - name: "检查分辨率设置"
        description: "验证当前分辨率设置"
        action: "verify"
        target:
          type: "text"
          description: "分辨率显示区域"
          location: [100, 200, 300, 50]  # [x, y, width, height]
          detection:
            ocr:
              language: "chinese_simplified"
              confidence: 0.7
          validation:
            type: "value_match"
            expected_values: ["1920x1080", "2560x1440"]
            recommended: "1920x1080"
            case_sensitive: false
        timeout: 5
        retry: 1
        
      - name: "检查帧率设置"
        description: "验证当前帧率限制"
        action: "verify"
        target:
          type: "text"
          description: "帧率显示区域"
          location: [100, 300, 200, 50]
          detection:
            ocr:
              language: "chinese_simplified"
              confidence: 0.7
          validation:
            type: "value_match"
            expected_values: ["60", "120", "144"]
            not_allowed: ["无限", "Unlimited"]
            recommended: "60"
        timeout: 5
        retry: 1
        
      - name: "检查窗口模式"
        description: "验证当前窗口模式"
        action: "verify"
        target:
          type: "text"
          description: "窗口模式显示区域"
          location: [100, 400, 200, 50]
          detection:
            ocr:
              language: "chinese_simplified"
              confidence: 0.7
          validation:
            type: "value_match"
            expected_values: ["窗口模式", "全屏模式", "Windowed", "Fullscreen"]
            recommended: "窗口模式"
        timeout: 5
        retry: 1
    
    # 设置验证规则
    validation_rules:
      resolution:
        name: "分辨率"
        type: "text_detection"
        importance: "high"
        expected_values: ["1920x1080", "2560x1440"]
        recommended: "1920x1080"
        validation:
          type: "exact_match"
          case_sensitive: false
        fix_actions:
          - name: "切换到推荐分辨率"
            action: "click"
            target:
              coordinate_fallback:
                click_point: [600, 350]
            validation:
              type: "value_change"
              expected_value: "1920x1080"
              
      frame_rate:
        name: "帧率限制"
        type: "text_detection"
        importance: "high"
        expected_values: ["60", "120", "144"]
        not_allowed: ["无限", "Unlimited"]
        recommended: "60"
        validation:
          type: "exact_match"
        fix_actions:
          - name: "设置帧率限制"
            action: "click"
            target:
              coordinate_fallback:
                click_point: [600, 450]
            validation:
              type: "value_change"
              expected_value: "60"
              
      window_mode:
        name: "窗口模式"
        type: "text_detection"
        importance: "medium"
        expected_values: ["窗口模式", "全屏模式", "Windowed", "Fullscreen"]
        recommended: "窗口模式"
        validation:
          type: "exact_match"
        fix_actions:
          - name: "切换到窗口模式"
            action: "click"
            target:
              coordinate_fallback:
                click_point: [600, 550]
            validation:
              type: "value_change"
              expected_value: "窗口模式"
              
      graphics_quality:
        name: "画质设置"
        type: "text_detection"
        importance: "low"
        expected_values: ["低", "中", "高", "极高", "Low", "Medium", "High", "Ultra"]
        recommended: "高"
        validation:
          type: "range_match"
          allowed_range: ["中", "高", "极高"]
    
    # 性能配置
    performance:
      screenshot_interval: 0.5  # 截图间隔(秒)
      detection_timeout: 30     # 检测超时(秒)
      cache_duration: 300       # 缓存持续时间(秒)
      parallel_processing: false # 是否并行处理
      
    # 错误处理配置
    error_handling:
      max_retries: 3
      retry_delay: 2
      fallback_strategy: "coordinate"  # 回退策略
      log_level: "info"
      screenshot_on_error: true
```

## 🔧 配置详解

### 检测策略配置

#### YOLO检测配置
```yaml
yolo:
  enabled: true
  model_path: "assets/models/yolo/game_ui_detector.pt"
  confidence_threshold: 0.6
  target_classes:
    - "settings_icon"      # 设置图标
    - "resolution_option"  # 分辨率选项
    - "frame_rate_option"  # 帧率选项
    - "window_mode_option" # 窗口模式选项
    - "graphics_option"    # 画质选项
    - "audio_option"       # 音频选项
    - "controls_option"    # 控制选项
```

#### 图像识别配置
```yaml
image_recognition:
  enabled: true
  similarity_threshold: 0.8
  templates:
    # 设置相关模板
    settings_icon: "assets/templates/settings_icon.png"
    back_button: "assets/templates/back_button.png"
    apply_button: "assets/templates/apply_button.png"
    
    # 分辨率模板
    resolution_1080p: "assets/templates/resolution_1080p.png"
    resolution_1440p: "assets/templates/resolution_1440p.png"
    resolution_4k: "assets/templates/resolution_4k.png"
    
    # 帧率模板
    frame_rate_30: "assets/templates/frame_rate_30.png"
    frame_rate_60: "assets/templates/frame_rate_60.png"
    frame_rate_120: "assets/templates/frame_rate_120.png"
    frame_rate_144: "assets/templates/frame_rate_144.png"
    
    # 窗口模式模板
    window_mode: "assets/templates/window_mode.png"
    fullscreen_mode: "assets/templates/fullscreen_mode.png"
    borderless_mode: "assets/templates/borderless_mode.png"
    
    # 画质模板
    graphics_low: "assets/templates/graphics_low.png"
    graphics_medium: "assets/templates/graphics_medium.png"
    graphics_high: "assets/templates/graphics_high.png"
    graphics_ultra: "assets/templates/graphics_ultra.png"
```

#### 坐标回退配置
```yaml
coordinate_fallback:
  enabled: true
  # 基于1920x1080分辨率的坐标
  base_resolution: [1920, 1080]
  fallback_coordinates:
    # 主界面坐标
    main_menu:
      settings_icon: [100, 200]
      start_game: [960, 800]
      
    # 设置菜单坐标
    settings_menu:
      display_option: [300, 250]
      audio_option: [300, 350]
      controls_option: [300, 450]
      graphics_option: [300, 550]
      
    # 显示设置坐标
    display_settings:
      resolution_dropdown: [600, 350]
      resolution_1080p: [600, 380]
      resolution_1440p: [600, 410]
      frame_rate_dropdown: [600, 450]
      frame_rate_60: [600, 480]
      frame_rate_120: [600, 510]
      window_mode_dropdown: [600, 550]
      window_mode: [600, 580]
      fullscreen_mode: [600, 610]
      apply_button: [800, 700]
      back_button: [200, 700]
```

### 导航步骤详细配置

#### 基本步骤结构
```yaml
- name: "步骤名称"
  description: "步骤描述"
  action: "click|verify|wait|input"  # 操作类型
  target:
    type: "icon|text|button|dropdown"
    description: "目标描述"
    
    # 多策略检测
    detection:
      yolo:
        target_class: "class_name"
      image_recognition:
        template_name: "template_name"
      coordinate_fallback:
        click_point: [x, y]
        
    # 验证规则
    validation:
      type: "screen_change|text_detection|value_match"
      expected_value: "期望值"
      
  # 执行配置
  timeout: 10      # 超时时间(秒)
  retry: 3         # 重试次数
  retry_delay: 2   # 重试延迟(秒)
```

#### 操作类型详解

**点击操作 (click)**
```yaml
- name: "点击设置图标"
  action: "click"
  target:
    type: "icon"
    detection:
      yolo:
        target_class: "settings_icon"
    validation:
      type: "screen_change"
      expected_change: "settings_menu_opened"
```

**验证操作 (verify)**
```yaml
- name: "验证分辨率"
  action: "verify"
  target:
    type: "text"
    location: [100, 200, 300, 50]
    detection:
      ocr:
        language: "chinese_simplified"
    validation:
      type: "value_match"
      expected_values: ["1920x1080", "2560x1440"]
```

**等待操作 (wait)**
```yaml
- name: "等待加载完成"
  action: "wait"
  duration: 3  # 等待时间(秒)
  condition:
    type: "screen_stable"
    timeout: 10
```

**输入操作 (input)**
```yaml
- name: "输入搜索内容"
  action: "input"
  target:
    type: "text_input"
    detection:
      image_recognition:
        template_name: "search_box"
    value: "搜索内容"
  validation:
    type: "text_input"
    expected_value: "搜索内容"
```

### 验证规则配置

#### 文本检测验证
```yaml
validation:
  type: "text_detection"
  expected_values: ["1920x1080", "2560x1440"]
  recommended: "1920x1080"
  match_type: "exact|contains|regex"
  case_sensitive: false
  confidence: 0.7
```

#### 屏幕变化验证
```yaml
validation:
  type: "screen_change"
  expected_change: "menu_opened|dialog_closed|loading_completed"
  reference_image: "assets/references/menu_opened.png"
  similarity_threshold: 0.8
```

#### 值匹配验证
```yaml
validation:
  type: "value_match"
  expected_values: ["60", "120", "144"]
  not_allowed: ["无限", "Unlimited"]
  recommended: "60"
  tolerance: 0  # 容差范围
```

### 修复动作配置

#### 自动修复配置
```yaml
fix_actions:
  - name: "切换到推荐分辨率"
    action: "click"
    target:
      coordinate_fallback:
        click_point: [600, 350]
    pre_conditions:
      - "settings_menu_opened"
      - "display_settings_active"
    validation:
      type: "value_change"
      expected_value: "1920x1080"
    fallback:
      - name: "手动选择分辨率"
        action: "complex_click"
        steps:
          - click: [600, 350]  # 点击下拉菜单
          - wait: 1
          - click: [600, 380]  # 选择1080p
          - wait: 1
          - click: [800, 700]  # 点击应用
```

## 🎮 游戏特定配置

### 绝区零配置示例
```yaml
# projects/zenless_zone_zero.yaml
game_settings:
  enabled: true
  config:
    game_specific:
      name: "绝区零"
      resolution: "1920x1080"
      aspect_ratio: "16:9"
      window_mode: "窗口模式"
      
    detection_strategies:
      yolo:
        model_path: "assets/models/yolo/zzz_ui_detector.pt"
        target_classes:
          - "zzz_settings_icon"
          - "zzz_display_option"
          - "zzz_graphics_option"
          
      image_recognition:
        templates:
          zzz_settings_icon: "assets/templates/zzz/settings_icon.png"
          zzz_display_tab: "assets/templates/zzz/display_tab.png"
          zzz_1080p_option: "assets/templates/zzz/1080p_option.png"
          
      coordinate_fallback:
        fallback_coordinates:
          zzz_settings_icon: [150, 220]
          zzz_display_tab: [400, 280]
          zzz_resolution_dropdown: [700, 350]
          zzz_1080p_option: [700, 380]
    
    navigation_steps:
      - name: "打开绝区零设置"
        action: "click"
        target:
          type: "icon"
          detection:
            yolo:
              target_class: "zzz_settings_icon"
          validation:
            type: "screen_change"
            expected_change: "zzz_settings_opened"
            
      - name: "选择显示设置"
        action: "click"
        target:
          type: "tab"
          detection:
            image_recognition:
              template_name: "zzz_display_tab"
          validation:
            type: "tab_active"
            expected_tab: "display"
```

### 原神配置示例
```yaml
# projects/genshin_impact.yaml
game_settings:
  enabled: true
  config:
    game_specific:
      name: "原神"
      resolution: "1920x1080"
      aspect_ratio: "16:9"
      
    detection_strategies:
      image_recognition:
        templates:
          gi_settings_icon: "assets/templates/gi/settings_icon.png"
          gi_graphics_tab: "assets/templates/gi/graphics_tab.png"
          gi_1080p_option: "assets/templates/gi/1080p_option.png"
          
      coordinate_fallback:
        fallback_coordinates:
          gi_settings_icon: [1800, 50]    # 右上角设置
          gi_graphics_tab: [400, 200]     # 图形标签
          gi_resolution: [600, 300]       # 分辨率设置
          gi_1080p: [600, 330]            # 1080p选项
```

## 🔧 高级配置选项

### 条件执行配置
```yaml
navigation_steps:
  - name: "条件检查分辨率"
    action: "conditional"
    condition:
      type: "setting_value"
      setting: "resolution"
      expected_value: "1920x1080"
    true_branch:
      - name: "分辨率正确跳过"
        action: "skip"
    false_branch:
      - name: "修复分辨率"
        action: "click"
        target:
          coordinate_fallback:
            click_point: [600, 350]
```

### 循环执行配置
```yaml
navigation_steps:
  - name: "等待加载完成"
    action: "loop"
    max_iterations: 10
    steps:
      - name: "检查加载状态"
        action: "verify"
        target:
          type: "text"
          location: [800, 500, 200, 50]
          detection:
            ocr:
              language: "chinese_simplified"
          validation:
            type: "text_absence"
            unexpected_text: ["加载中", "Loading"]
    break_condition:
      type: "success"
```

### 错误恢复配置
```yaml
error_recovery:
  - error_type: "timeout"
    recovery_actions:
      - name: "返回主菜单"
        action: "key_press"
        key: "esc"
        times: 3
      - name: "重新开始检测"
        action: "restart_from"
        step: "打开设置菜单"
        
  - error_type: "detection_failed"
    recovery_actions:
      - name: "切换检测策略"
        action: "switch_strategy"
        strategy: "coordinate_fallback"
      - name: "重试当前步骤"
        action: "retry"
        max_retries: 2
```

## 📊 配置验证

### 配置验证规则
```yaml
config_validation:
  required_fields:
    - "game_settings.config.detection_strategies"
    - "game_settings.config.navigation_steps"
    
  strategy_validation:
    yolo:
      required: ["model_path", "confidence_threshold"]
    image_recognition:
      required: ["templates"]
    coordinate_fallback:
      required: ["fallback_coordinates"]
      
  step_validation:
    required: ["name", "action", "target"]
    action_types: ["click", "verify", "wait", "input"]
    
  coordinate_validation:
    screen_bounds: [0, 0, 1920, 1080]
    warn_out_of_bounds: true
```

### 配置测试用例
```yaml
test_cases:
  - name: "基本导航测试"
    steps:
      - step: "打开设置菜单"
        expected: "settings_menu_opened"
      - step: "选择显示设置"
        expected: "display_settings_active"
        
  - name: "设置验证测试"
    steps:
      - step: "验证分辨率"
        expected: "1920x1080"
      - step: "验证帧率"
        expected: "60"
        
  - name: "错误处理测试"
    steps:
      - step: "模拟检测失败"
        action: "inject_error"
        error_type: "detection_timeout"
        expected_recovery: "strategy_switch"
```

## 🚀 使用建议

### 最佳实践
1. **分层配置**: 先配置坐标回退确保基本功能，再添加高级检测策略
2. **渐进增强**: 从简单验证开始，逐步添加复杂导航步骤
3. **错误处理**: 为每个步骤配置适当的重试和回退机制
4. **性能优化**: 根据实际环境调整检测超时和重试参数

### 调试配置
```yaml
debug:
  enabled: true
  screenshot_every_step: true
  log_detection_details: true
  save_failed_detections: true
  output_dir: "debug/game_settings"
```

这个YAML配置模板提供了完整的游戏设置检测定义，支持多种检测策略和复杂的导航流程，可以根据具体游戏需求进行定制和扩展。
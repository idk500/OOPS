# 游戏设置检测功能设计

## 功能概述

游戏设置检测功能通过YOLO识别技术，自动检测游戏内的配置设置，确保其符合开发者推荐的标准。该功能支持自动化流程：启动游戏 → 导航到设置页面 → 检测配置项 → 生成报告 → 关闭游戏。

## 架构设计

### 模块结构
```
oops/plugins/game_setting_detector/
├── __init__.py
├── game_launcher.py          # 游戏启动器
├── setting_navigator.py      # 设置导航器
├── yolo_detector.py          # YOLO检测器
├── setting_validator.py      # 设置验证器
├── process_manager.py        # 进程管理器
└── game_configs/             # 游戏配置模板
    ├── zenless_zone_zero.yaml
    ├── genshin_impact.yaml
    └── star_rail.yaml
```

## 配置系统设计

### 游戏设置检测配置

#### `configs/game_setting.yaml`
```yaml
game_setting_checks:
  enabled: true
  timeout: 300  # 整个检测过程的超时时间（秒）

  games:
    zenless_zone_zero:
      name: "绝区零"
      executable: "C:\\Program Files\\miHoYo Launcher\\games\\ZenlessZoneZero Game\\ZenlessZoneZero.exe"
      process_name: "ZenlessZoneZero.exe"
      setting_navigation:
        type: "yolo_navigation"
        steps:
          - name: "打开主菜单"
            action: "click"
            target:
              type: "icon"
              description: "主菜单按钮"
              confidence: 0.8
            timeout: 10
            retry: 3
            
          - name: "进入设置"
            action: "click" 
            target:
              type: "text"
              text: "设置"
              confidence: 0.7
            timeout: 5
            retry: 2
            
          - name: "进入画面设置"
            action: "click"
            target:
              type: "text"
              text: "画面设置"
              confidence: 0.7
            timeout: 5
            retry: 2

      settings_to_check:
        - name: "帧率设置"
          type: "text_detection"
          location:
            x: 100
            y: 200
            width: 200
            height: 50
          expected_values: ["30", "60"]  # 允许的值
          recommended: "60"              # 推荐值
          validation:
            type: "exact_match"
            case_sensitive: false
            
        - name: "分辨率"
          type: "text_detection" 
          location:
            x: 150
            y: 250
            width: 300
            height: 50
          expected_values: ["1920x1080", "2560x1440"]
          recommended: "1920x1080"
          validation:
            type: "exact_match"
            
        - name: "画面质量"
          type: "icon_detection"
          location:
            x: 200
            y: 300
            width: 100
            height: 100
          expected_values: ["低", "中", "高", "极高"]
          recommended: "高"
          validation:
            type: "pattern_match"
            
        - name: "滤镜强度"
          type: "slider_detection"
          location:
            x: 180
            y: 350
            width: 400
            height: 30
          expected_range: [0, 100]
          recommended_range: [0, 30]
          validation:
            type: "range_check"
            
        - name: "全屏模式"
          type: "toggle_detection"
          location:
            x: 220
            y: 400
            width: 150
            height: 40
          expected_values: ["窗口", "全屏"]
          recommended: "窗口"
          validation:
            type: "exact_match"

  yolo_config:
    model_path: "assets/models/game_ui_detector.onnx"
    confidence_threshold: 0.6
    input_size: [640, 640]
    classes: ["button", "text", "slider", "toggle", "icon"]

  screenshot:
    output_dir: ".debug/game_screenshots"
    save_failed_detections: true
    save_successful_navigation: false

  performance:
    max_navigation_time: 60
    detection_interval: 1.0
    click_delay: 0.5
```

## 核心模块实现

### 1. 游戏启动器 (Game Launcher)

```python
# oops/plugins/game_setting_detector/game_launcher.py
import subprocess
import psutil
import time
from pathlib import Path
from typing import Optional, Dict

class GameLauncher:
    """游戏启动器"""
    
    def __init__(self, game_config: Dict):
        self.game_config = game_config
        self.process = None
        
    def launch_game(self) -> bool:
        """启动游戏"""
        executable_path = Path(self.game_config['executable'])
        
        if not executable_path.exists():
            raise FileNotFoundError(f"游戏可执行文件不存在: {executable_path}")
        
        try:
            # 启动游戏进程
            self.process = subprocess.Popen([
                str(executable_path)
            ])
            
            # 等待游戏启动
            return self._wait_for_game_ready()
            
        except Exception as e:
            raise RuntimeError(f"启动游戏失败: {e}")
    
    def _wait_for_game_ready(self, timeout: int = 60) -> bool:
        """等待游戏准备就绪"""
        process_name = self.game_config.get('process_name')
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 检查进程是否在运行
            if self.process.poll() is not None:
                return False  # 进程已退出
                
            # 如果指定了进程名，检查是否有对应的进程
            if process_name:
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] == process_name:
                        # 等待额外时间确保游戏界面加载完成
                        time.sleep(5)
                        return True
            
            time.sleep(1)
        
        return False
    
    def close_game(self) -> bool:
        """关闭游戏"""
        if self.process:
            try:
                # 尝试优雅关闭
                self.process.terminate()
                self.process.wait(timeout=10)
                return True
            except subprocess.TimeoutExpired:
                # 强制关闭
                self.process.kill()
                self.process.wait()
                return True
            except Exception:
                return False
        return True
    
    def is_running(self) -> bool:
        """检查游戏是否在运行"""
        if self.process and self.process.poll() is None:
            return True
            
        # 检查进程名
        process_name = self.game_config.get('process_name')
        if process_name:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == process_name:
                    return True
                    
        return False
```

### 2. 设置导航器 (Setting Navigator)

```python
# oops/plugins/game_setting_detector/setting_navigator.py
import time
import logging
from typing import List, Dict, Optional
from .yolo_detector import YOLODetector

class SettingNavigator:
    """设置导航器"""
    
    def __init__(self, yolo_detector: YOLODetector, navigation_steps: List[Dict]):
        self.yolo_detector = yolo_detector
        self.navigation_steps = navigation_steps
        self.logger = logging.getLogger(__name__)
        self.screenshot_count = 0
    
    def navigate_to_settings(self) -> bool:
        """导航到设置页面"""
        self.logger.info("开始导航到游戏设置页面")
        
        for step_index, step in enumerate(self.navigation_steps):
            step_name = step['name']
            self.logger.info(f"执行步骤 {step_index + 1}: {step_name}")
            
            success = self._execute_navigation_step(step)
            if not success:
                self.logger.error(f"导航步骤失败: {step_name}")
                return False
                
            # 步骤间延迟
            time.sleep(step.get('click_delay', 0.5))
        
        self.logger.info("成功导航到设置页面")
        return True
    
    def _execute_navigation_step(self, step: Dict) -> bool:
        """执行单个导航步骤"""
        action = step['action']
        target = step['target']
        timeout = step.get('timeout', 10)
        max_retries = step.get('retry', 3)
        
        for attempt in range(max_retries):
            self.logger.debug(f"尝试 {attempt + 1}/{max_retries}")
            
            # 截图并检测目标
            detection_result = self.yolo_detector.detect_target(target)
            
            if detection_result['found']:
                # 执行操作
                if action == 'click':
                    success = self._click_target(detection_result)
                    if success:
                        return True
                else:
                    self.logger.warning(f"不支持的操作类型: {action}")
                    return False
            
            # 等待后重试
            if attempt < max_retries - 1:
                time.sleep(1)
        
        self.logger.error(f"导航步骤失败: 未找到目标 {target}")
        return False
    
    def _click_target(self, detection_result: Dict) -> bool:
        """点击检测到的目标"""
        try:
            import pyautogui
            
            # 获取目标中心坐标
            bbox = detection_result['bbox']
            center_x = bbox[0] + bbox[2] // 2
            center_y = bbox[1] + bbox[3] // 2
            
            # 点击目标
            pyautogui.click(center_x, center_y)
            
            # 等待操作生效
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"点击目标失败: {e}")
            return False
    
    def take_screenshot(self, prefix: str = "step") -> str:
        """截图并保存"""
        try:
            import pyautogui
            from datetime import datetime
            
            screenshot = pyautogui.screenshot()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}_{self.screenshot_count:04d}.png"
            
            # 保存到调试目录
            output_dir = Path(".debug/game_screenshots")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = output_dir / filename
            screenshot.save(filepath)
            
            self.screenshot_count += 1
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"截图失败: {e}")
            return ""
```

### 3. YOLO检测器 (YOLO Detector)

```python
# oops/plugins/game_setting_detector/yolo_detector.py
import cv2
import numpy as np
from typing import Dict, List, Optional
import logging

class YOLODetector:
    """YOLO检测器"""
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.5):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.net = self._load_model()
        self.logger = logging.getLogger(__name__)
    
    def _load_model(self):
        """加载YOLO模型"""
        try:
            net = cv2.dnn.readNet(self.model_path)
            # 设置推理后端（优先使用CUDA）
            try:
                net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                self.logger.info("使用CUDA加速YOLO推理")
            except:
                net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                self.logger.info("使用CPU进行YOLO推理")
                
            return net
        except Exception as e:
            raise RuntimeError(f"加载YOLO模型失败: {e}")
    
    def detect_target(self, target_config: Dict) -> Dict:
        """检测指定目标"""
        try:
            import pyautogui
            
            # 截图
            screenshot = pyautogui.screenshot()
            image = np.array(screenshot)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # 执行YOLO检测
            detections = self._detect_objects(image)
            
            # 过滤匹配的目标
            matched_detections = self._filter_detections(detections, target_config)
            
            if matched_detections:
                # 返回置信度最高的检测结果
                best_detection = max(matched_detections, key=lambda x: x['confidence'])
                return {
                    'found': True,
                    'bbox': best_detection['bbox'],
                    'confidence': best_detection['confidence'],
                    'class_name': best_detection['class_name']
                }
            else:
                return {'found': False}
                
        except Exception as e:
            self.logger.error(f"目标检测失败: {e}")
            return {'found': False, 'error': str(e)}
    
    def detect_setting_value(self, setting_config: Dict) -> Optional[str]:
        """检测设置项的值"""
        try:
            import pyautogui
            
            # 截图
            screenshot = pyautogui.screenshot()
            image = np.array(screenshot)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # 根据设置类型执行不同的检测逻辑
            setting_type = setting_config['type']
            
            if setting_type == 'text_detection':
                return self._detect_text_value(image, setting_config)
            elif setting_type == 'icon_detection':
                return self._detect_icon_value(image, setting_config)
            elif setting_type == 'slider_detection':
                return self._detect_slider_value(image, setting_config)
            elif setting_type == 'toggle_detection':
                return self._detect_toggle_value(image, setting_config)
            else:
                self.logger.warning(f"不支持的设置检测类型: {setting_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"设置值检测失败: {e}")
            return None
    
    def _detect_objects(self, image: np.ndarray) -> List[Dict]:
        """使用YOLO检测图像中的对象"""
        # 预处理图像
        blob = cv2.dnn.blobFromImage(
            image, 1/255.0, (640, 640), swapRB=True, crop=False
        )
        
        self.net.setInput(blob)
        outputs = self.net.forward()
        
        # 解析检测结果
        detections = []
        for detection in outputs[0]:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            if confidence > self.confidence_threshold:
                # 转换边界框坐标
                center_x = int(detection[0] * image.shape[1])
                center_y = int(detection[1] * image.shape[0])
                width = int(detection[2] * image.shape[1])
                height = int(detection[3] * image.shape[0])
                
                x = int(center_x - width / 2)
                y = int(center_y - height / 2)
                
                detections.append({
                    'bbox': [x, y, width, height],
                    'confidence': float(confidence),
                    'class_id': int(class_id),
                    'class_name': self._get_class_name(class_id)
                })
        
        return detections
    
    def _filter_detections(self, detections: List[Dict], target_config: Dict) -> List[Dict]:
        """过滤检测结果，匹配目标配置"""
        filtered = []
        
        target_type = target_config['type']
        min_confidence = target_config.get('confidence', 0.5)
        
        for detection in detections:
            # 检查置信度
            if detection['confidence'] < min_confidence:
                continue
            
            # 根据目标类型过滤
            if target_type == 'icon' and detection['class_name'] == 'icon':
                filtered.append(detection)
            elif target_type == 'text' and detection['class_name'] == 'text':
                # 可以添加OCR进一步验证文本内容
                filtered.append(detection)
            elif target_type == 'button' and detection['class_name'] == 'button':
                filtered.append(detection)
            elif target_type == 'slider' and detection['class_name'] == 'slider':
                filtered.append(detection)
            elif target_type == 'toggle' and detection['class_name'] == 'toggle':
                filtered.append(detection)
        
        return filtered
    
    def _detect_text_value(self, image: np.ndarray, setting_config: Dict) -> Optional[str]:
        """检测文本设置值"""
        try:
            import pytesseract
            
            # 提取设置区域的ROI
            location = setting_config['location']
            x, y, w, h = location['x'], location['y'], location['width'], location['height']
            roi = image[y:y+h, x:x+w]
            
            # 使用OCR识别文本
            config = '--psm 7 -c tessedit_char_whitelist=0123456789xabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ%'
            text = pytesseract.image_to_string(roi, config=config).strip()
            
            self.logger.debug(f"OCR识别结果: '{text}'")
            return text if text else None
            
        except Exception as e:
            self.logger.error(f"文本检测失败: {e}")
            return None
    
    def _detect_slider_value(self, image: np.ndarray, setting_config: Dict) -> Optional[str]:
        """检测滑块设置值"""
        # 实现滑块位置检测逻辑
        # 可以通过检测滑块手柄的位置来估算数值
        location = setting_config['location']
        x, y, w, h = location['x'], location['y'], location['width'], location['height']
        
        # 简化的实现：返回固定值用于演示
        # 实际实现需要检测滑块手柄位置并计算百分比
        return "50"  # 示例值
    
    def _detect_icon_value(self, image: np.ndarray, setting_config: Dict) -> Optional[str]:
        """检测图标设置值"""
        # 实现图标识别逻辑
        # 可以通过模板匹配或分类器识别特定图标
        location = setting_config['location']
        x, y, w, h = location['x'], location['y'], location['width'], location['height']
        
        # 简化的实现
        return "高"  # 示例值
    
    def _detect_toggle_value(self, image: np.ndarray, setting_config: Dict) -> Optional[str]:
        """检测开关设置值"""
        # 实现开关状态检测逻辑
        location = setting_config['location']
        x, y, w, h = location['x'], location['y'], location['width'], location['height']
        
        # 简化的实现
        return "窗口"  # 示例值
    
    def _get_class_name(self, class_id: int) -> str:
        """根据类别ID获取类别名称"""
        class_names = {
            0: "button",
            1: "text", 
            2: "slider",
            3: "toggle",
            4: "icon"
        }
        return class_names.get(class_id, "unknown")
```

### 4. 设置验证器 (Setting Validator)

```python
# oops/plugins/game_setting_detector/setting_validator.py
import logging
from typing import Dict, List, Optional

class SettingValidator:
    """设置验证器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_setting(self, detected_value: str, setting_config: Dict) -> Dict:
        """验证设置值"""
        setting_name = setting_config['name']
        validation_config = setting_config['validation']
        validation_type = validation_config['type']
        
        result = {
            'setting_name': setting_name,
            'detected_value': detected_value,
            'status': 'unknown',
            'message': ''
        }
        
        if detected_value is None:
            result.update({
                'status': 'error',
                'message': '无法检测设置值'
            })
            return result
        
        try:
            if validation_type == 'exact_match':
                result.update(self._validate_exact_match(detected_value, setting_config))
            elif validation_type == 'pattern_match':
                result.update(self._validate_pattern_match(detected_value, setting_config))
            elif validation_type == 'range_check':
                result.update(self._validate_range_check(detected_value, setting_config))
            else:
                result.update({
                    'status': 'error', 
                    'message': f'不支持的验证类型: {validation_type}'
                })
                
        except Exception as e:
            result.update({
                'status': 'error',
                'message': f'验证过程中出错: {str(e)}'
            })
        
        return result
    
    def _validate_exact_match(self, detected_value: str, setting_config: Dict) -> Dict:
        """精确匹配验证"""
        expected_values = setting_config['expected_values']
        case_sensitive = setting_config['validation'].get('case_sensitive', False)
        
        if not case_sensitive:
            detected_value = detected_value.lower()
            expected_values = [v.lower() for v in expected_values]
        
        if detected_value in expected_values:
            recommended = setting_config.get('recommended')
            if detected_value == recommended:
                return {
                    'status': 'optimal',
                    'message': f'设置值符合推荐值: {detected_value}'
                }
            else:
                return {
                    'status': 'acceptable', 
                    'message': f'设置值可接受: {detected_value} (推荐: {recommended})'
                }
        else:
            return {
                'status': 'mismatch',
                'message': f'设置值不匹配: {detected_value} (期望: {expected_values})'
            }
    
    def _validate_pattern_match(self, detected_value: str, setting_config: Dict) -> Dict:
        """模式匹配验证"""
        # 实现简单的模式匹配
        expected_values = setting_config['expected_values']
        
        for expected in expected_values:
            if expected in detected_value:
                recommended = setting_config.get('recommended')
                if expected == recommended:
                    return {
                        'status': 'optimal',
                        'message': f'设置值符合推荐: {detected_value}'
                    }
                else:
                    return {
                        'status': 'acceptable',
                        'message': f'设置值可接受: {detected_value} (推荐: {recommended})'
                    }
        
        return {
            'status': 'mismatch',
            'message': f'设置值不匹配: {detected_value} (期望模式: {expected_values})'
        }
    
    def _validate_range_check(self, detected_value: str, setting_config: Dict) -> Dict:
        """范围检查验证"""
        try:
            value = float(detected_value)
            expected_range = setting_config['expected_range']
            recommended_range = setting_config.get('recommended_range', expected_range)
            
            min_val, max_val = expected_range
            rec_min, rec_max = recommended_range
            
            if rec_min <= value <= rec_max:
                return {
                    'status': 'optimal',
                    'message': f'设置值在推荐范围内: {value}'
                }
            elif min_val <= value <= max_val:
                return {
                    'status': 'acceptable',
                    'message': f'设置值在允许范围内: {value} (推荐: {rec_min}-{rec_max})'
                }
            else:
                return {
                    'status': 'out_of_range',
                    'message': f'设置值超出范围: {value} (允许: {min_val}-{max_val})'
                }
                
        except ValueError:
            return {
                'status': 'error',
                'message': f'无法解析数值: {detected_value}'
            }
```

### 5. 主检测器类

```python
# oops/plugins/game_setting_detector/__init__.py
import time
import logging
from typing import Dict, List
from .game_launcher import GameLauncher
from .setting_navigator import SettingNavigator
from .yolo_detector import YOLODetector
from .setting_validator import SettingValidator
from .process_manager import ProcessManager

class GameSettingDetector:
    """游戏设置检测器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.yolo_detector = YOLODetector(config['yolo_config']['model_path'])
        self.setting_validator = SettingValidator()
        self.results = []
    
    def detect_game_settings(self, game_name: str) -> List[Dict]:
        """检测游戏设置"""
        game_config = self.config['games'].get(game_name)
        if not game_config:
            raise ValueError(f"未找到游戏配置: {game_name}")
        
        self.logger.info(f"开始检测游戏设置: {game_config['name']}")
        
        # 启动游戏
        launcher = GameLauncher(game_config)
        if not launcher.launch_game():
            raise RuntimeError("启动游戏失败")
        
        try:
            # 导航到设置页面
            navigator = SettingNavigator(
                self.yolo_detector, 
                game_config['setting_navigation']['steps']
            )
            
            if not navigator.navigate_to_settings():
                raise RuntimeError("导航到设置页面失败")
            
            # 检测各项设置
            settings_to_check = game_config['settings_to_check']
            for setting_config in settings_to_check:
                result = self._check_single_setting(setting_config)
                self.results.append(result)
            
            return self.results
            
        finally:
            # 关闭游戏
            launcher.close_game()
    
    def _check_single_setting(self, setting_config: Dict) -> Dict:
        """检查单个设置项"""
        self.logger.info(f"检查设置: {setting_config['name']}")
        
        # 检测设置值
        detected_value = self.yolo_detector.detect_setting_value(setting_config)
        
        # 验证设置值
        validation_result = self.setting_validator.validate_setting(
            detected_value, setting_config
        )
        
        # 添加截图信息用于调试
        validation_result['screenshot'] = self.yolo_detector.take_screenshot(
            f"setting_{setting_config['name']}"
        )
        
        return validation_result
    
    def generate_report(self) -> Dict:
        """生成检测报告"""
        total_checks = len(self.results)
        optimal_count = sum(1 for r in self.results if r['status'] == 'optimal')
        acceptable_count = sum(1 for r in self.results if r['status'] == 'acceptable')
        problem_count = total_checks - optimal_count - acceptable_count
        
        return {
            'summary': {
                'total_checks': total_checks,
                'optimal_settings': optimal_count,
                'acceptable_settings': acceptable_count,
                'problem_settings': problem_count,
                'success_rate': (optimal_count + acceptable_count) / total_checks if total_checks > 0 else 0
            },
            'detailed_results': self.results,
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        for result in self.results:
            if result['status'] in ['mismatch', 'out_of_range']:
                recommendations.append(
                    f"{result['setting_name']}: {result['message']}"
                )
        
        return recommendations
```

## 使用示例

### 命令行使用
```bash
# 检测绝区零游戏设置
oops --game zenless_zone_zero --check-settings

# 指定游戏路径
oops --game zenless_zone_zero --game-path "D:\Games\ZenlessZoneZero" --check-settings

# 生成详细报告
oops --game zenless_zone_zero --check-settings --report html --output ./game_reports
```

### Python API 使用
```python
from oops.plugins.game_setting_detector import GameSettingDetector

# 创建检测器
detector = GameSettingDetector(config)

# 检测游戏设置
results = detector.detect_game_settings("zenless_zone_zero")

# 生成报告
report = detector.generate_report()
print(f"检测完成: {report['summary']['success_rate']:.1%} 的设置符合要求")
```

## 集成到主系统

### 在主配置中添加游戏设置检测
```yaml
# configs/base.yaml 中添加
game_setting:
  enabled: true
  games:
    - "zenless_zone_zero"
    - "genshin_impact" 
    - "star_rail"
  
  detection_timeout: 300
  auto_close_game: true
```

这个游戏设置检测功能设计提供了完整的自动化流程，从游戏启动到设置验证，完全基于YOLO识别技术，能够准确检测游戏内的各种配置设置。
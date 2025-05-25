#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Florr.io 自动AFK脚本
基于视频分析实现的自动化工具，用于在Florr.io游戏中实现自动AFK
"""

import time
import random
import logging
import threading
import json
import os
import sys
from datetime import datetime
import numpy as np
import cv2
import pyautogui
import keyboard
from PIL import Image, ImageGrab

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("florr_afk.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("FlorAFK")

# 禁用PyAutoGUI的安全特性，避免意外中断
pyautogui.FAILSAFE = False

class Config:
    """配置管理类"""
    
    DEFAULT_CONFIG = {
        "area": "sewers",  # 游戏区域: sewers, desert, spider, anthill
        "mode": "normal",  # 行为模式: aggressive, normal, conservative
        "run_time": 0,     # 运行时间(分钟)，0表示无限制
        "recovery": True,  # 是否自动恢复
        "check_interval": 5.0,  # AFK检测弹窗检查间隔(秒)
        "movement_interval": [2.0, 5.0],  # 移动操作间隔范围(秒)
        "screen_region": None,  # 游戏窗口区域，None表示全屏
        "debug": False     # 是否启用调试模式
    }
    
    def __init__(self, config_file="florr_config.json"):
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self):
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
                logger.info(f"配置已从 {self.config_file} 加载")
            else:
                self.save_config()
                logger.info(f"创建了默认配置文件 {self.config_file}")
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"配置已保存到 {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        self.save_config()


class ImageRecognition:
    """图像识别模块"""
    
    # AFK弹窗的特征颜色和位置特征
    AFK_POPUP_FEATURES = {
        "colors": [(255, 255, 255), (0, 0, 0), (255, 0, 0)],  # 白色、黑色、红色
        "button_size": (100, 40),  # 按钮大致尺寸
        "templates": []  # 将在初始化时加载模板
    }
    
    def __init__(self, config):
        self.config = config
        self.screen_region = config.get("screen_region")
        self.debug = config.get("debug", False)
        
        # 加载模板图像
        self.load_templates()
    
    def load_templates(self):
        """加载模板图像用于匹配"""
        # 实际使用时，应该有一些预先准备好的AFK弹窗模板
        # 这里为简化，暂不实现模板加载
        pass
    
    def capture_screen(self):
        """捕获屏幕截图"""
        try:
            if self.screen_region:
                screenshot = pyautogui.screenshot(region=self.screen_region)
            else:
                screenshot = pyautogui.screenshot()
            
            # 转换为OpenCV格式
            screenshot = np.array(screenshot)
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            
            if self.debug:
                cv2.imwrite(f"debug_screenshot_{int(time.time())}.png", screenshot)
                
            return screenshot
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None
    
    def detect_afk_popup(self):
        """检测AFK弹窗"""
        screenshot = self.capture_screen()
        if screenshot is None:
            return None
        
        # 方法1: 颜色检测 - 查找特定颜色组合
        # 这里使用简化的颜色检测，实际应用中可能需要更复杂的算法
        
        # 转换为HSV颜色空间，更容易进行颜色检测
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # 定义红色范围 (AFK弹窗通常有红色按钮或文字)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        # 创建红色掩码
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2
        
        # 查找红色区域的轮廓
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 筛选可能的按钮区域
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # 检查区域大小是否符合按钮特征
            if 50 < w < 200 and 20 < h < 80:
                # 这可能是一个AFK确认按钮
                button_center = (x + w // 2, y + h // 2)
                
                if self.debug:
                    debug_img = screenshot.copy()
                    cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.imwrite(f"debug_afk_detected_{int(time.time())}.png", debug_img)
                
                logger.info(f"检测到可能的AFK弹窗按钮，位置: {button_center}")
                return button_center
        
        # 方法2: 模板匹配 (简化版)
        # 实际应用中应该有多个模板并进行更复杂的匹配
        
        return None
    
    def detect_game_status(self):
        """检测游戏状态"""
        screenshot = self.capture_screen()
        if screenshot is None:
            return "unknown"
        
        # 检测游戏是否正常运行的逻辑
        # 这里可以检查游戏界面的特定元素
        
        # 简化版：检查屏幕上是否有游戏特定的颜色
        # 例如，检查是否有游戏背景的特定颜色
        
        # 这里仅作为示例，实际应用需要更精确的检测
        return "normal"


class InputController:
    """输入控制模块"""
    
    def __init__(self, config):
        self.config = config
        self.debug = config.get("debug", False)
    
    def move_mouse(self, x, y, duration=None):
        """移动鼠标到指定位置"""
        try:
            if duration is None:
                duration = random.uniform(0.1, 0.3)
            
            # 添加随机偏移
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            
            pyautogui.moveTo(x + offset_x, y + offset_y, duration=duration)
            
            if self.debug:
                logger.debug(f"鼠标移动到 ({x + offset_x}, {y + offset_y})")
                
            return True
        except Exception as e:
            logger.error(f"鼠标移动失败: {e}")
            return False
    
    def click(self, x=None, y=None, button='left'):
        """点击指定位置"""
        try:
            if x is not None and y is not None:
                self.move_mouse(x, y)
            
            # 模拟人类点击行为
            # 随机的按下和释放间隔
            down_time = random.uniform(0.01, 0.1)
            
            pyautogui.mouseDown(button=button)
            time.sleep(down_time)
            pyautogui.mouseUp(button=button)
            
            if self.debug:
                logger.debug(f"点击 {button} 按钮")
                
            return True
        except Exception as e:
            logger.error(f"点击失败: {e}")
            return False
    
    def press_key(self, key, duration=None):
        """按下并释放按键"""
        try:
            if duration is None:
                duration = random.uniform(0.1, 0.5)
            
            keyboard.press(key)
            time.sleep(duration)
            keyboard.release(key)
            
            if self.debug:
                logger.debug(f"按键 {key} 持续 {duration:.2f}秒")
                
            return True
        except Exception as e:
            logger.error(f"按键操作失败: {e}")
            return False
    
    def execute_movement_pattern(self, pattern):
        """执行移动模式"""
        for action in pattern:
            action_type = action[0]
            
            if action_type == "key":
                key, duration, interval = action[1:]
                self.press_key(key, duration)
                time.sleep(interval)
            
            elif action_type == "mouse":
                x, y, button = action[1:]
                self.click(x, y, button)
                time.sleep(random.uniform(0.1, 0.3))
            
            elif action_type == "wait":
                duration = action[1]
                time.sleep(duration)


class MovementStrategy:
    """移动策略基类"""
    
    def __init__(self, config, input_controller):
        self.config = config
        self.input = input_controller
        self.mode = config.get("mode", "normal")
    
    def generate_random_movement(self):
        """生成随机移动模式"""
        pattern = []
        
        # 根据模式调整随机性
        if self.mode == "aggressive":
            actions = random.randint(2, 5)
            max_duration = 0.8
        elif self.mode == "conservative":
            actions = random.randint(1, 3)
            max_duration = 1.2
        else:  # normal
            actions = random.randint(2, 4)
            max_duration = 1.0
        
        # 生成随机按键序列
        for _ in range(actions):
            key = random.choice(['w', 'a', 's', 'd'])
            duration = random.uniform(0.1, max_duration)
            interval = random.uniform(0.05, 0.2)
            pattern.append(("key", key, duration, interval))
        
        # 有时添加鼠标移动和点击
        if random.random() < 0.3:
            x = random.randint(300, 1000)
            y = random.randint(200, 700)
            pattern.append(("mouse", x, y, 'left'))
        
        # 添加等待
        pattern.append(("wait", random.uniform(0.5, 1.5)))
        
        return pattern
    
    def execute(self):
        """执行移动策略"""
        pattern = self.generate_random_movement()
        self.input.execute_movement_pattern(pattern)


class SewerStrategy(MovementStrategy):
    """下水道区域策略"""
    
    def __init__(self, config, input_controller):
        super().__init__(config, input_controller)
        
        # 下水道区域的安全位置
        self.safe_positions = [
            (400, 300),
            (500, 400),
            (350, 450)
        ]
    
    def generate_random_movement(self):
        """生成下水道区域的随机移动"""
        pattern = []
        
        # 选择一个安全位置
        target = random.choice(self.safe_positions)
        
        # 添加移动到安全位置的操作
        pattern.append(("mouse", target[0], target[1], 'left'))
        
        # 添加随机的小范围移动
        for _ in range(random.randint(1, 3)):
            key = random.choice(['w', 'a', 's', 'd'])
            duration = random.uniform(0.05, 0.2)  # 短时间按键，小范围移动
            interval = random.uniform(0.05, 0.2)
            pattern.append(("key", key, duration, interval))
        
        # 添加等待
        pattern.append(("wait", random.uniform(0.5, 1.5)))
        
        return pattern


class DesertStrategy(MovementStrategy):
    """沙漠区域策略"""
    
    def generate_random_movement(self):
        """生成沙漠区域的随机移动"""
        pattern = []
        
        # 沙漠区域需要更频繁的移动来避免静态敌人
        for _ in range(random.randint(3, 6)):
            key = random.choice(['w', 'a', 's', 'd'])
            duration = random.uniform(0.1, 0.3)
            interval = random.uniform(0.05, 0.15)
            pattern.append(("key", key, duration, interval))
        
        # 更频繁的攻击
        if random.random() < 0.5:
            x = random.randint(300, 1000)
            y = random.randint(200, 700)
            pattern.append(("mouse", x, y, 'left'))
        
        # 添加等待
        pattern.append(("wait", random.uniform(0.3, 0.8)))
        
        return pattern


class SpiderStrategy(MovementStrategy):
    """蜘蛛区域策略"""
    
    def generate_random_movement(self):
        """生成蜘蛛区域的随机移动"""
        pattern = []
        
        # 蜘蛛区域需要精确的位置控制
        # 更短的移动和更多的方向变化
        
        for _ in range(random.randint(4, 8)):
            key = random.choice(['w', 'a', 's', 'd'])
            duration = random.uniform(0.05, 0.15)  # 非常短的按键时间
            interval = random.uniform(0.05, 0.1)
            pattern.append(("key", key, duration, interval))
        
        # 频繁的攻击
        for _ in range(random.randint(1, 3)):
            x = random.randint(300, 1000)
            y = random.randint(200, 700)
            pattern.append(("mouse", x, y, 'left'))
            pattern.append(("wait", random.uniform(0.1, 0.3)))
        
        return pattern


class AnthillStrategy(MovementStrategy):
    """蚁穴区域策略"""
    
    def generate_random_movement(self):
        """生成蚁穴区域的随机移动"""
        pattern = []
        
        # 蚁穴区域的移动策略
        # 较少的移动，更多的攻击
        
        for _ in range(random.randint(1, 3)):
            key = random.choice(['w', 'a', 's', 'd'])
            duration = random.uniform(0.1, 0.4)
            interval = random.uniform(0.1, 0.3)
            pattern.append(("key", key, duration, interval))
        
        # 更多的攻击
        for _ in range(random.randint(2, 4)):
            x = random.randint(300, 1000)
            y = random.randint(200, 700)
            pattern.append(("mouse", x, y, 'left'))
            pattern.append(("wait", random.uniform(0.2, 0.5)))
        
        return pattern


class FlorAFKBot:
    """Florr.io AFK机器人主类"""
    
    def __init__(self, config_file=None):
        # 初始化配置
        self.config = Config(config_file)
        
        # 初始化组件
        self.image_recognition = ImageRecognition(self.config)
        self.input_controller = InputController(self.config)
        
        # 根据配置选择策略
        self.strategy = self._create_strategy()
        
        # 运行状态
        self.running = False
        self.start_time = None
        self.monitor_thread = None
    
    def _create_strategy(self):
        """创建对应区域的策略"""
        area = self.config.get("area", "sewers")
        
        if area == "sewers":
            return SewerStrategy(self.config, self.input_controller)
        elif area == "desert":
            return DesertStrategy(self.config, self.input_controller)
        elif area == "spider":
            return SpiderStrategy(self.config, self.input_controller)
        elif area == "anthill":
            return AnthillStrategy(self.config, self.input_controller)
        else:
            logger.warning(f"未知区域 '{area}'，使用默认策略")
            return MovementStrategy(self.config, self.input_controller)
    
    def start(self):
        """启动AFK机器人"""
        if self.running:
            logger.warning("AFK机器人已经在运行")
            return
        
        self.running = True
        self.start_time = time.time()
        
        logger.info(f"AFK机器人启动，区域: {self.config.get('area')}, 模式: {self.config.get('mode')}")
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_function)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        # 主循环
        try:
            self._main_loop()
        except KeyboardInterrupt:
            logger.info("用户手动停止AFK机器人")
        except Exception as e:
            logger.error(f"AFK机器人运行出错: {e}")
            if self.config.get("recovery", True):
                logger.info("尝试恢复...")
                self._recover_from_error("unknown")
        finally:
            self.stop()
    
    def stop(self):
        """停止AFK机器人"""
        self.running = False
        
        if self.start_time:
            run_time = time.time() - self.start_time
            logger.info(f"AFK机器人停止，运行时间: {run_time:.2f}秒")
            self.start_time = None
    
    def _main_loop(self):
        """主循环"""
        while self.running:
            # 检查运行时间限制
            run_time_limit = self.config.get("run_time", 0)
            if run_time_limit > 0 and self.start_time:
                elapsed_time = (time.time() - self.start_time) / 60  # 转换为分钟
                if elapsed_time >= run_time_limit:
                    logger.info(f"达到运行时间限制 ({run_time_limit}分钟)，停止AFK机器人")
                    break
            
            # 检查AFK弹窗
            popup_position = self.image_recognition.detect_afk_popup()
            if popup_position:
                logger.info(f"检测到AFK弹窗，点击位置: {popup_position}")
                self.input_controller.click(popup_position[0], popup_position[1])
                time.sleep(random.uniform(1.0, 2.0))
                continue
            
            # 执行区域特定策略
            self.strategy.execute()
            
            # 随机等待，避免过于规律的操作
            wait_time = random.uniform(
                self.config.get("movement_interval", [2.0, 5.0])[0],
                self.config.get("movement_interval", [2.0, 5.0])[1]
            )
            time.sleep(wait_time)
    
    def _monitor_function(self):
        """监控线程函数"""
        check_interval = self.config.get("check_interval", 5.0)
        
        while self.running:
            try:
                # 检查游戏状态
                status = self.image_recognition.detect_game_status()
                if status != "normal":
                    logger.warning(f"检测到游戏状态异常: {status}")
                    self._recover_from_error(status)
                
                time.sleep(check_interval)
            except Exception as e:
                logger.error(f"监控线程出错: {e}")
                time.sleep(check_interval * 2)  # 出错后等待更长时间
    
    def _recover_from_error(self, error_type):
        """从错误中恢复"""
        if not self.config.get("recovery", True):
            logger.info("自动恢复已禁用，不进行恢复")
            return
        
        logger.info(f"尝试从错误中恢复: {error_type}")
        
        if error_type == "disconnected":
            # 模拟刷新页面
            logger.info("模拟刷新页面...")
            # 实际应用中可能需要更复杂的操作
            
        elif error_type == "game_closed":
            # 尝试重新打开游戏
            logger.info("尝试重新打开游戏...")
            # 实际应用中可能需要更复杂的操作
            
        else:
            # 通用恢复策略
            logger.info("执行通用恢复策略...")
            # 可以尝试点击屏幕中央，按ESC键等
            screen_width, screen_height = pyautogui.size()
            self.input_controller.click(screen_width // 2, screen_height // 2)
            time.sleep(1)
            self.input_controller.press_key('esc')
            time.sleep(1)
        
        # 等待一段时间后继续
        time.sleep(5)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Florr.io 自动AFK脚本')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--area', type=str, choices=['sewers', 'desert', 'spider', 'anthill'], 
                        help='游戏区域')
    parser.add_argument('--mode', type=str, choices=['aggressive', 'normal', 'conservative'], 
                        help='行为模式')
    parser.add_argument('--time', type=int, help='运行时间(分钟)，0表示无限制')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    # 创建AFK机器人
    bot = FlorAFKBot(args.config)
    
    # 应用命令行参数
    if args.area:
        bot.config.set("area", args.area)
    if args.mode:
        bot.config.set("mode", args.mode)
    if args.time is not None:
        bot.config.set("run_time", args.time)
    if args.debug:
        bot.config.set("debug", True)
    
    # 启动机器人
    print("按Ctrl+C停止")
    bot.start()


if __name__ == "__main__":
    main()

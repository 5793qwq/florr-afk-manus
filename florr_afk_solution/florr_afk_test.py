#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Florr.io 自动AFK脚本测试模块
用于验证自动AFK脚本的功能和准确性
"""

import time
import random
import logging
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2
from PIL import Image

# 导入主脚本
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import florr_afk_bot

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("florr_afk_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("FlorAFKTest")


class TestImageRecognition(unittest.TestCase):
    """测试图像识别模块"""
    
    def setUp(self):
        """测试前准备"""
        # 创建模拟配置
        self.mock_config = MagicMock()
        self.mock_config.get.return_value = None
        
        # 创建图像识别对象
        self.image_recognition = florr_afk_bot.ImageRecognition(self.mock_config)
    
    @patch('florr_afk_bot.pyautogui.screenshot')
    def test_capture_screen(self, mock_screenshot):
        """测试屏幕截图功能"""
        # 创建模拟截图
        mock_img = Image.new('RGB', (800, 600), color='white')
        mock_screenshot.return_value = mock_img
        
        # 调用截图方法
        screenshot = self.image_recognition.capture_screen()
        
        # 验证结果
        self.assertIsNotNone(screenshot)
        self.assertEqual(screenshot.shape[0], 600)  # 高度
        self.assertEqual(screenshot.shape[1], 800)  # 宽度
        self.assertEqual(screenshot.shape[2], 3)    # 通道数
    
    @patch('florr_afk_bot.ImageRecognition.capture_screen')
    def test_detect_afk_popup_with_popup(self, mock_capture):
        """测试AFK弹窗检测 - 有弹窗的情况"""
        # 创建一个模拟的带有红色按钮的截图
        img = np.zeros((600, 800, 3), dtype=np.uint8)
        # 添加一个红色矩形模拟按钮
        cv2.rectangle(img, (350, 280), (450, 320), (0, 0, 255), -1)
        mock_capture.return_value = img
        
        # 调用检测方法
        result = self.image_recognition.detect_afk_popup()
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        # 按钮中心应该在(400, 300)附近
        self.assertTrue(380 <= result[0] <= 420)
        self.assertTrue(290 <= result[1] <= 310)
    
    @patch('florr_afk_bot.ImageRecognition.capture_screen')
    def test_detect_afk_popup_without_popup(self, mock_capture):
        """测试AFK弹窗检测 - 无弹窗的情况"""
        # 创建一个没有红色按钮的截图
        img = np.zeros((600, 800, 3), dtype=np.uint8)
        # 添加一些其他颜色的元素
        cv2.rectangle(img, (100, 100), (200, 150), (0, 255, 0), -1)  # 绿色矩形
        mock_capture.return_value = img
        
        # 调用检测方法
        result = self.image_recognition.detect_afk_popup()
        
        # 验证结果
        self.assertIsNone(result)
    
    @patch('florr_afk_bot.ImageRecognition.capture_screen')
    def test_detect_game_status_normal(self, mock_capture):
        """测试游戏状态检测 - 正常状态"""
        # 创建一个模拟的游戏截图
        img = np.zeros((600, 800, 3), dtype=np.uint8)
        # 添加一些游戏元素
        cv2.rectangle(img, (100, 100), (700, 500), (50, 100, 150), -1)  # 游戏背景
        mock_capture.return_value = img
        
        # 调用检测方法
        result = self.image_recognition.detect_game_status()
        
        # 验证结果
        self.assertEqual(result, "normal")


class TestInputController(unittest.TestCase):
    """测试输入控制模块"""
    
    def setUp(self):
        """测试前准备"""
        # 创建模拟配置
        self.mock_config = MagicMock()
        self.mock_config.get.return_value = False  # 禁用调试模式
        
        # 创建输入控制对象
        self.input_controller = florr_afk_bot.InputController(self.mock_config)
    
    @patch('florr_afk_bot.pyautogui.moveTo')
    def test_move_mouse(self, mock_moveTo):
        """测试鼠标移动功能"""
        # 调用移动方法
        result = self.input_controller.move_mouse(400, 300, 0.2)
        
        # 验证结果
        self.assertTrue(result)
        mock_moveTo.assert_called_once()
        # 检查参数 - 由于有随机偏移，只能检查大致范围
        args, kwargs = mock_moveTo.call_args
        self.assertTrue(395 <= args[0] <= 405)
        self.assertTrue(295 <= args[1] <= 305)
        self.assertEqual(kwargs['duration'], 0.2)
    
    @patch('florr_afk_bot.pyautogui.moveTo')
    @patch('florr_afk_bot.pyautogui.mouseDown')
    @patch('florr_afk_bot.pyautogui.mouseUp')
    @patch('florr_afk_bot.time.sleep')
    def test_click(self, mock_sleep, mock_mouseUp, mock_mouseDown, mock_moveTo):
        """测试鼠标点击功能"""
        # 调用点击方法
        result = self.input_controller.click(400, 300)
        
        # 验证结果
        self.assertTrue(result)
        mock_moveTo.assert_called_once()
        mock_mouseDown.assert_called_once_with(button='left')
        mock_mouseUp.assert_called_once_with(button='left')
        self.assertEqual(mock_sleep.call_count, 1)
    
    @patch('florr_afk_bot.keyboard.press')
    @patch('florr_afk_bot.keyboard.release')
    @patch('florr_afk_bot.time.sleep')
    def test_press_key(self, mock_sleep, mock_release, mock_press):
        """测试按键功能"""
        # 调用按键方法
        result = self.input_controller.press_key('w', 0.5)
        
        # 验证结果
        self.assertTrue(result)
        mock_press.assert_called_once_with('w')
        mock_release.assert_called_once_with('w')
        self.assertEqual(mock_sleep.call_count, 1)
        mock_sleep.assert_called_once_with(0.5)
    
    @patch('florr_afk_bot.InputController.press_key')
    @patch('florr_afk_bot.InputController.click')
    @patch('florr_afk_bot.time.sleep')
    def test_execute_movement_pattern(self, mock_sleep, mock_click, mock_press_key):
        """测试执行移动模式功能"""
        # 创建测试模式
        pattern = [
            ("key", "w", 0.5, 0.1),
            ("mouse", 400, 300, 'left'),
            ("wait", 1.0)
        ]
        
        # 调用执行方法
        self.input_controller.execute_movement_pattern(pattern)
        
        # 验证结果
        mock_press_key.assert_called_once_with("w", 0.5)
        mock_click.assert_called_once_with(400, 300, 'left')
        self.assertEqual(mock_sleep.call_count, 3)  # 按键间隔 + 点击后等待 + wait指令


class TestMovementStrategy(unittest.TestCase):
    """测试移动策略模块"""
    
    def setUp(self):
        """测试前准备"""
        # 创建模拟配置
        self.mock_config = MagicMock()
        self.mock_config.get.side_effect = lambda key, default=None: {
            "mode": "normal",
            "area": "sewers"
        }.get(key, default)
        
        # 创建模拟输入控制器
        self.mock_input = MagicMock()
        
        # 创建各种策略对象
        self.base_strategy = florr_afk_bot.MovementStrategy(self.mock_config, self.mock_input)
        self.sewer_strategy = florr_afk_bot.SewerStrategy(self.mock_config, self.mock_input)
        self.desert_strategy = florr_afk_bot.DesertStrategy(self.mock_config, self.mock_input)
        self.spider_strategy = florr_afk_bot.SpiderStrategy(self.mock_config, self.mock_input)
        self.anthill_strategy = florr_afk_bot.AnthillStrategy(self.mock_config, self.mock_input)
    
    def test_base_strategy_generate_movement(self):
        """测试基础策略生成移动模式"""
        pattern = self.base_strategy.generate_random_movement()
        
        # 验证结果
        self.assertIsInstance(pattern, list)
        self.assertTrue(len(pattern) > 0)
        
        # 检查模式格式
        for action in pattern:
            self.assertIsInstance(action, tuple)
            self.assertIn(action[0], ["key", "mouse", "wait"])
    
    def test_sewer_strategy_generate_movement(self):
        """测试下水道策略生成移动模式"""
        pattern = self.sewer_strategy.generate_random_movement()
        
        # 验证结果
        self.assertIsInstance(pattern, list)
        self.assertTrue(len(pattern) > 0)
        
        # 检查是否包含移动到安全位置的操作
        has_mouse_action = False
        for action in pattern:
            if action[0] == "mouse":
                has_mouse_action = True
                break
        
        self.assertTrue(has_mouse_action)
    
    def test_strategy_execute(self):
        """测试策略执行功能"""
        # 模拟generate_random_movement方法
        self.base_strategy.generate_random_movement = MagicMock(return_value=[
            ("key", "w", 0.5, 0.1),
            ("wait", 1.0)
        ])
        
        # 调用执行方法
        self.base_strategy.execute()
        
        # 验证结果
        self.mock_input.execute_movement_pattern.assert_called_once()
        args = self.mock_input.execute_movement_pattern.call_args[0]
        self.assertEqual(args[0], [("key", "w", 0.5, 0.1), ("wait", 1.0)])


class TestFlorAFKBot(unittest.TestCase):
    """测试AFK机器人主类"""
    
    def setUp(self):
        """测试前准备"""
        # 模拟配置类
        with patch('florr_afk_bot.Config') as mock_config_class:
            mock_config = MagicMock()
            mock_config.get.side_effect = lambda key, default=None: {
                "area": "sewers",
                "mode": "normal",
                "run_time": 0,
                "recovery": True,
                "check_interval": 5.0,
                "movement_interval": [2.0, 5.0]
            }.get(key, default)
            mock_config_class.return_value = mock_config
            
            # 创建AFK机器人对象
            self.bot = florr_afk_bot.FlorAFKBot()
            
            # 保存模拟对象引用
            self.mock_config = mock_config
        
        # 模拟组件
        self.bot.image_recognition = MagicMock()
        self.bot.input_controller = MagicMock()
        self.bot.strategy = MagicMock()
    
    def test_create_strategy(self):
        """测试创建策略功能"""
        # 测试不同区域的策略创建
        areas = ["sewers", "desert", "spider", "anthill", "unknown"]
        strategy_classes = [
            florr_afk_bot.SewerStrategy,
            florr_afk_bot.DesertStrategy,
            florr_afk_bot.SpiderStrategy,
            florr_afk_bot.AnthillStrategy,
            florr_afk_bot.MovementStrategy
        ]
        
        for area, expected_class in zip(areas, strategy_classes):
            # 设置区域
            self.mock_config.get.side_effect = lambda key, default=None: area if key == "area" else {
                "mode": "normal",
                "run_time": 0,
                "recovery": True
            }.get(key, default)
            
            # 创建策略
            with patch.object(florr_afk_bot, 'SewerStrategy', return_value="SewerStrategy"), \
                 patch.object(florr_afk_bot, 'DesertStrategy', return_value="DesertStrategy"), \
                 patch.object(florr_afk_bot, 'SpiderStrategy', return_value="SpiderStrategy"), \
                 patch.object(florr_afk_bot, 'AnthillStrategy', return_value="AnthillStrategy"), \
                 patch.object(florr_afk_bot, 'MovementStrategy', return_value="MovementStrategy"):
                
                strategy = self.bot._create_strategy()
                
                # 验证结果
                if area == "sewers":
                    self.assertEqual(strategy, "SewerStrategy")
                elif area == "desert":
                    self.assertEqual(strategy, "DesertStrategy")
                elif area == "spider":
                    self.assertEqual(strategy, "SpiderStrategy")
                elif area == "anthill":
                    self.assertEqual(strategy, "AnthillStrategy")
                else:
                    self.assertEqual(strategy, "MovementStrategy")
    
    @patch('florr_afk_bot.time.time')
    @patch('florr_afk_bot.time.sleep')
    def test_main_loop_with_afk_popup(self, mock_sleep, mock_time):
        """测试主循环 - 有AFK弹窗的情况"""
        # 设置模拟时间
        mock_time.return_value = 1000
        
        # 设置AFK弹窗检测结果
        self.bot.image_recognition.detect_afk_popup.side_effect = [
            (400, 300),  # 第一次检测到弹窗
            None,        # 第二次没有弹窗
            None,        # 第三次没有弹窗
            KeyboardInterrupt  # 第四次抛出异常，结束循环
        ]
        
        # 运行主循环
        self.bot.running = True
        self.bot.start_time = 1000
        
        try:
            self.bot._main_loop()
        except KeyboardInterrupt:
            pass
        
        # 验证结果
        self.assertEqual(self.bot.image_recognition.detect_afk_popup.call_count, 4)
        self.bot.input_controller.click.assert_called_once_with(400, 300)
        self.assertEqual(self.bot.strategy.execute.call_count, 2)  # 第二次和第三次循环
    
    @patch('florr_afk_bot.time.sleep')
    def test_recover_from_error(self, mock_sleep):
        """测试从错误中恢复功能"""
        # 测试不同类型的错误
        error_types = ["disconnected", "game_closed", "unknown"]
        
        for error_type in error_types:
            # 重置模拟对象
            self.bot.input_controller.reset_mock()
            
            # 调用恢复方法
            self.bot._recover_from_error(error_type)
            
            # 验证结果
            if error_type == "unknown":
                # 通用恢复策略应该点击屏幕中央并按ESC键
                self.bot.input_controller.click.assert_called_once()
                self.bot.input_controller.press_key.assert_called_once_with('esc')
            
            # 所有情况都应该等待
            mock_sleep.assert_called()


def main():
    """运行所有测试"""
    unittest.main()


if __name__ == "__main__":
    main()

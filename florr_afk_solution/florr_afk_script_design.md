# Florr.io 自动AFK Python脚本设计方案

## 整体架构

基于对Florr.io新版AFK机制的分析，我设计了一个模块化的Python自动化脚本架构，包含以下核心组件：

1. **图像识别模块**：负责识别游戏界面元素，包括AFK检测弹窗、敌人、花瓣等
2. **输入控制模块**：负责模拟鼠标和键盘操作，实现角色移动和交互
3. **行为策略模块**：根据不同区域实现特定的AFK策略
4. **监控与恢复模块**：处理异常情况，确保脚本长时间稳定运行
5. **配置管理模块**：允许用户自定义脚本参数和行为

## 技术选型

1. **图像处理库**：
   - OpenCV：用于屏幕截图分析和图像识别
   - PyAutoGUI：用于屏幕截图获取
   - Pillow：用于基础图像处理

2. **输入模拟库**：
   - PyAutoGUI：用于鼠标移动和点击
   - PyDirectInput：用于更底层的输入模拟，减少被检测风险
   - Keyboard：用于键盘按键模拟

3. **辅助工具**：
   - NumPy：用于数学计算和随机数生成
   - Threading：用于多线程管理
   - Logging：用于日志记录

## 核心功能实现方案

### 1. AFK检测弹窗自动响应

```python
def detect_afk_popup():
    """检测屏幕上是否出现AFK检测弹窗"""
    screenshot = pyautogui.screenshot()
    # 转换为OpenCV格式
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    
    # 使用模板匹配或特征识别查找AFK弹窗
    # 返回弹窗位置和置信度
    
def respond_to_afk_popup(position):
    """对AFK弹窗进行响应点击"""
    # 添加随机偏移，模拟人类点击的不精确性
    offset_x = random.randint(-5, 5)
    offset_y = random.randint(-5, 5)
    
    # 模拟人类点击行为，包括移动和点击
    pyautogui.moveTo(position[0] + offset_x, position[1] + offset_y, 
                    duration=random.uniform(0.1, 0.3))
    pyautogui.click()
```

### 2. 随机化移动轨迹

```python
def generate_random_movement_pattern():
    """生成随机的移动模式"""
    # 生成一系列随机但平滑的移动指令
    movement_pattern = []
    
    # 添加随机的方向键按压序列
    for _ in range(random.randint(3, 8)):
        key = random.choice(['w', 'a', 's', 'd'])
        duration = random.uniform(0.1, 1.5)  # 按键持续时间
        interval = random.uniform(0.05, 0.3)  # 按键间隔
        movement_pattern.append((key, duration, interval))
    
    return movement_pattern

def execute_movement_pattern(pattern):
    """执行移动模式"""
    for key, duration, interval in pattern:
        # 按下按键
        keyboard.press(key)
        # 等待指定时间
        time.sleep(duration)
        # 释放按键
        keyboard.release(key)
        # 按键间隔
        time.sleep(interval)
        
    # 偶尔添加鼠标移动和点击，模拟攻击行为
    if random.random() < 0.3:  # 30%的概率执行攻击
        mouse_x = random.randint(100, 1000)
        mouse_y = random.randint(100, 700)
        pyautogui.moveTo(mouse_x, mouse_y, duration=random.uniform(0.2, 0.5))
        pyautogui.click()
```

### 3. 区域特定策略实现

```python
class SewerStrategy:
    """下水道区域的AFK策略"""
    def __init__(self):
        self.safe_positions = [
            (400, 300),  # 示例安全位置坐标
            (500, 400),
            (350, 450)
        ]
        
    def execute(self):
        """执行下水道区域的AFK策略"""
        # 选择一个安全位置
        target = random.choice(self.safe_positions)
        
        # 移动到安全位置附近（添加随机偏移）
        offset_x = random.randint(-30, 30)
        offset_y = random.randint(-30, 30)
        
        # 生成移动指令
        # ...
        
        # 定期改变攻击角度
        # ...

class DesertStrategy:
    """沙漠区域的AFK策略"""
    # 类似实现，但针对沙漠区域的特点
    # ...

class SpiderStrategy:
    """蜘蛛区域的AFK策略"""
    # 类似实现，但针对蜘蛛区域的特点
    # ...
```

### 4. 异常处理与恢复机制

```python
def check_game_status():
    """检查游戏是否正常运行"""
    # 截图检查游戏界面特征
    # 检测是否断线、崩溃或其他异常
    
def recover_from_error(error_type):
    """从错误中恢复"""
    if error_type == "disconnected":
        # 重新连接游戏
        # ...
    elif error_type == "game_closed":
        # 重启游戏
        # ...
    elif error_type == "unknown":
        # 尝试重启脚本
        # ...
```

### 5. 主控制循环

```python
def main():
    """主控制循环"""
    # 初始化配置
    config = load_config()
    
    # 选择区域策略
    if config["area"] == "sewers":
        strategy = SewerStrategy()
    elif config["area"] == "desert":
        strategy = DesertStrategy()
    elif config["area"] == "spider":
        strategy = SpiderStrategy()
    else:
        strategy = DefaultStrategy()
    
    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_function)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # 主循环
    try:
        while True:
            # 检查AFK弹窗
            popup = detect_afk_popup()
            if popup:
                respond_to_afk_popup(popup)
                continue
            
            # 执行区域特定策略
            strategy.execute()
            
            # 检查游戏状态
            status = check_game_status()
            if status != "normal":
                recover_from_error(status)
            
            # 随机等待，避免过于规律的操作
            time.sleep(random.uniform(1.0, 3.0))
            
    except KeyboardInterrupt:
        print("脚本已手动停止")
    except Exception as e:
        logging.error(f"发生错误: {e}")
        # 尝试恢复
        recover_from_error("unknown")
```

## 防检测机制

1. **时间随机化**：所有操作间隔和持续时间都添加随机因素
2. **位置随机化**：点击位置添加随机偏移
3. **行为多样化**：混合使用键盘和鼠标操作，模拟真实玩家
4. **模式变化**：定期改变移动和攻击模式，避免被识别为机器人
5. **低频操作**：避免高频率的重复操作，减少被检测风险

## 用户配置选项

脚本将提供以下可配置选项：

1. **游戏区域**：选择要AFK的游戏区域（下水道、沙漠、蜘蛛等）
2. **行为模式**：选择更激进或更保守的AFK策略
3. **运行时间**：设置脚本自动停止的时间
4. **恢复选项**：配置错误恢复的行为
5. **日志级别**：设置日志详细程度

## 实现注意事项

1. 脚本需要在游戏窗口激活的状态下运行
2. 用户需要先手动进入指定的游戏区域
3. 不同的屏幕分辨率可能需要调整参数
4. 游戏更新后可能需要更新图像识别模板
5. 长时间运行可能会因为游戏机制变化而失效

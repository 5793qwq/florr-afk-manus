# Florr.io 自动AFK脚本使用说明

## 项目概述

本项目基于对bilibili上florr.io新版AFK视频的分析，开发了一个完整的Python自动化脚本，用于在Florr.io游戏中实现自动AFK（Away From Keyboard）功能。脚本能够自动识别游戏中的AFK检测弹窗，模拟人类玩家的随机移动和操作，并根据不同游戏区域采用特定的策略，有效避免被游戏系统检测为机器人。

## 文件说明

本项目包含以下文件：

1. `florr_afk_bot.py` - 主脚本文件，包含完整的自动AFK功能实现
2. `florr_afk_test.py` - 测试模块，用于验证脚本的各项功能
3. `florr_afk_patterns.md` - AFK机制分析与规律总结文档
4. `florr_afk_script_design.md` - 脚本设计方案文档
5. `florr_afk_videos.md` - 视频分析清单，记录了用于研究的bilibili视频

## 环境要求

- Python 3.6+
- 依赖库：
  - OpenCV (`pip install opencv-python`)
  - PyAutoGUI (`pip install pyautogui`)
  - Pillow (`pip install pillow`)
  - NumPy (`pip install numpy`)
  - Keyboard (`pip install keyboard`)

## 安装步骤

1. 确保已安装Python 3.6或更高版本
2. 安装所需依赖库：
   ```
   pip install opencv-python pyautogui pillow numpy keyboard
   ```
3. 下载所有项目文件到同一目录

## 使用方法

### 基本用法

1. 打开Florr.io游戏，并手动进入您想要AFK的游戏区域
2. 运行脚本：
   ```
   python florr_afk_bot.py
   ```
3. 脚本将自动开始运行，监控游戏界面并执行AFK策略
4. 按下`Ctrl+C`可随时停止脚本

### 高级选项

脚本支持多种命令行参数，可根据需要进行配置：

```
python florr_afk_bot.py [选项]

选项:
  --config CONFIG       配置文件路径
  --area {sewers,desert,spider,anthill}
                        游戏区域
  --mode {aggressive,normal,conservative}
                        行为模式
  --time TIME           运行时间(分钟)，0表示无限制
  --debug               启用调试模式
```

例如，要在沙漠区域运行30分钟，使用激进模式：
```
python florr_afk_bot.py --area desert --mode aggressive --time 30
```

### 配置文件

脚本首次运行时会在当前目录创建`florr_config.json`配置文件，您可以直接编辑此文件来修改脚本行为：

```json
{
    "area": "sewers",
    "mode": "normal",
    "run_time": 0,
    "recovery": true,
    "check_interval": 5.0,
    "movement_interval": [2.0, 5.0],
    "screen_region": null,
    "debug": false
}
```

配置项说明：
- `area`: 游戏区域 (sewers, desert, spider, anthill)
- `mode`: 行为模式 (aggressive, normal, conservative)
- `run_time`: 运行时间(分钟)，0表示无限制
- `recovery`: 是否自动恢复
- `check_interval`: AFK检测弹窗检查间隔(秒)
- `movement_interval`: 移动操作间隔范围(秒)
- `screen_region`: 游戏窗口区域，null表示全屏
- `debug`: 是否启用调试模式

## 区域策略说明

脚本针对不同游戏区域实现了特定的AFK策略：

1. **下水道区域 (Sewers)**
   - 在安全位置小范围移动
   - 定期改变攻击角度
   - 适合长时间AFK

2. **沙漠区域 (Desert)**
   - 更频繁的移动以避免静态敌人
   - 更多的攻击操作
   - 适合中等难度区域

3. **蜘蛛区域 (Spider)**
   - 精确的位置控制
   - 复杂的攻击模式
   - 适合高难度区域

4. **蚁穴区域 (Anthill)**
   - 较少的移动，更多的攻击
   - 适合特定花瓣组合

## 注意事项

1. 脚本需要在游戏窗口激活的状态下运行
2. 使用前请确保您已手动进入指定的游戏区域
3. 不同的屏幕分辨率可能需要调整参数
4. 游戏更新后可能需要更新脚本
5. 长时间使用可能会因为游戏机制变化而失效
6. 使用脚本可能违反游戏规则，请自行承担风险

## 故障排除

1. **脚本无法检测到AFK弹窗**
   - 检查游戏窗口是否被遮挡
   - 尝试调整屏幕分辨率
   - 启用调试模式查看截图

2. **鼠标或键盘操作不生效**
   - 确保游戏窗口处于激活状态
   - 检查是否有其他程序拦截了输入
   - 尝试以管理员权限运行脚本

3. **脚本频繁崩溃**
   - 检查日志文件了解错误原因
   - 更新依赖库到最新版本
   - 减少其他程序的资源占用

## 测试

运行测试模块以验证脚本功能：
```
python florr_afk_test.py
```

测试模块会验证脚本的各个组件是否正常工作，包括图像识别、输入控制、移动策略等。

## 免责声明

本脚本仅供学习和研究目的使用。使用本脚本可能违反游戏服务条款，可能导致账号被封禁。作者不对因使用本脚本而导致的任何损失负责。

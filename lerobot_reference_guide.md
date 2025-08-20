# LeRobot Reference Guide

## TeleoperatorConfig Class

### Location
- **Main Definition**: `/Users/dong/AV/ros_final/lerobot/src/lerobot/teleoperators/config.py:23`
- **Import Statement**: `from lerobot.teleoperators.config import TeleoperatorConfig`

### Class Structure
```python
@dataclass(kw_only=True)
class TeleoperatorConfig(draccus.ChoiceRegistry, abc.ABC):
    # Allows to distinguish between different teleoperators of the same type
    id: str | None = None
    # Directory to store calibration file
    calibration_dir: Path | None = None
```

### Files That Import TeleoperatorConfig
- `/Users/dong/AV/ros_final/lerobot/src/lerobot/envs/configs.py`
- `/Users/dong/AV/ros_final/lerobot-ros/lerobot_ros/teleoperators/config_gamepad_6dof.py`

## Robot and Teleoperator IDs

### Example IDs Used in Documentation
- **Robot IDs**: 
  - `my_robot_instance` (placeholder in integration guide)
  - `my_awesome_follower_arm`
  - `blue`, `black`, `white`
  - `bimanual_follower`
  - `my_awesome_kiwi`

- **Teleoperator IDs**:
  - `my_teleop` (placeholder in integration guide)
  - `my_awesome_leader_arm`
  - `blue`, `red`, `black`
  - `bimanual_leader`

### Command Line Usage Examples
```bash
# Basic teleoperation
lerobot-teleoperate \
  --robot.id=my_robot_instance \
  --teleop.id=my_teleop \

# With specific robot types
lerobot-teleoperate \
  --robot.id=my_awesome_follower_arm \
  --teleop.id=my_awesome_leader_arm \
```

## Calibration System

### Main Calibration Script
- **Location**: `/Users/dong/AV/ros_final/lerobot/src/lerobot/calibrate.py`
- **Command**: `lerobot-calibrate`

### Calibration Usage Example
```bash
lerobot-calibrate \
    --teleop.type=so100_leader \
    --teleop.port=/dev/tty.usbmodem58760431551 \
    --teleop.id=blue
```

### Calibration Configuration
- The `TeleoperatorConfig` class includes a `calibration_dir` field for storing calibration files
- Calibration is required for most teleoperator devices

## Cross-Package References (lerobot-ros → lerobot)

### How lerobot-ros References lerobot
The `lerobot-ros` package imports from the main `lerobot` package using standard Python imports:

#### In `/Users/dong/AV/ros_final/lerobot-ros/scripts/teleoperate.py`:
```python
from lerobot import teleoperate as lr_tel
from lerobot.robots import Robot, RobotConfig
from lerobot.teleoperators import Teleoperator, TeleoperatorConfig
```

#### In `/Users/dong/AV/ros_final/lerobot-ros/lerobot_ros/teleoperators/config_gamepad_6dof.py`:
```python
from lerobot.teleoperators.config import TeleoperatorConfig
```

### Custom Implementation Pattern
The ROS integration overrides default factory functions:

```python
# Override default creation functions
orig_make_robot_from_config = lr_tel.make_robot_from_config
orig_make_teleoperator_from_config = lr_tel.make_teleoperator_from_config

def make_my_robot_from_config(config: RobotConfig) -> Robot:
    if isinstance(config, ROS2Config):
        return ROS2Robot(config)
    return orig_make_robot_from_config(config)

def make_my_teleoperator_from_config(config: TeleoperatorConfig) -> Teleoperator:
    if isinstance(config, GamepadTeleop6DOFConfig):
        return GamepadTeleop6DOF(config)
    return orig_make_teleoperator_from_config(config)

# Replace the factory functions
lr_tel.make_robot_from_config = make_my_robot_from_config
lr_tel.make_teleoperator_from_config = make_my_teleoperator_from_config
```

## Key Takeaways

1. **IDs are Runtime Identifiers**: Robot and teleop IDs like `my_robot_instance` and `my_teleop` are user-defined runtime identifiers, not hardcoded values.

2. **Calibration is Available**: Use `lerobot-calibrate` with appropriate `--teleop.id` to calibrate devices.

3. **Cross-Package Imports**: The `lerobot-ros` package successfully imports from `lerobot` using standard Python module imports.

4. **Extensible Architecture**: The system allows custom robot and teleoperator implementations through factory function overrides.

---
 How Python Imports Work with Folders

  1. Package Structure

  The lerobot folder becomes a Python package because:
  - It has src/lerobot/__init__.py at
  /Users/dong/AV/ros_final/lerobot/src/lerobot/__init__.py
  - The pyproject.toml at /Users/dong/AV/ros_final/lerobot/pyproject.toml:27 defines it as
  package name "lerobot"

  2. Three Ways This Can Work

  Option A: Installed Package
  # If lerobot was installed with pip install -e ./lerobot
  pip install -e /Users/dong/AV/ros_final/lerobot

  Option B: PYTHONPATH Environment Variable
  export PYTHONPATH="/Users/dong/AV/ros_final/lerobot/src:$PYTHONPATH"

  Option C: Direct sys.path Manipulation
  import sys
  sys.path.append('/Users/dong/AV/ros_final/lerobot/src')
  from lerobot import something  # Now this works

  3. Current Status Check

  The pip list | grep lerobot returned empty, meaning lerobot is not installed as a package.


  This suggests either:
  - PYTHONPATH is set to include the lerobot/src directory
  - The code is run from a specific working directory that makes the import work
  - The import might actually be failing in your current setup

  4. To Make It Work

  You need to either:
  # Install lerobot as editable package
  cd /Users/dong/AV/ros_final/lerobot
  pip install -e .

  # OR set PYTHONPATH
  export PYTHONPATH="/Users/dong/AV/ros_final/lerobot/src:$PYTHONPATH"

  That's why from lerobot.teleoperators.config import TeleoperatorConfig works - Python
  finds the package through one of these mechanisms.

---


  The Two Commands

  1. pip install -e . (inside lerobot folder)

  cd /Users/dong/AV/ros_final/lerobot
  pip install -e .

  2. pip install -e /Users/dong/AV/ros_final/lerobot (from anywhere)

  # From any directory
  pip install -e /Users/dong/AV/ros_final/lerobot

  Key Differences

  | Aspect            | pip install -e .              | pip install -e /path/to/lerobot |
  |-------------------|-------------------------------|---------------------------------|
  | Working Directory | Must be inside lerobot folder | Can run from anywhere           |
  | Path Reference    | . means "current directory"   | Explicit absolute path          |
  | Final Result      | Identical                     | Identical                       |

  What Both Commands Do

  Both create an editable installation that:

  1. Links the package to your Python environment
  2. Creates a .egg-link file pointing to the source code
  3. Allows import lerobot from anywhere
  4. Enables live code changes (no reinstall needed)

  Yes, Both Enable import lerobot

  After either command, you can:

  # From anywhere in your system
  import lerobot
  from lerobot.teleoperators.config import TeleoperatorConfig
  from lerobot.robots import Robot

  How It Works

⏺ Read(lerobot/pyproject.toml)
  ⎿  Read 50 lines (ctrl+r to expand)

⏺ The pyproject.toml defines:
  - Package name: "lerobot" (line 27)
  - Source location: The src/lerobot/ directory contains the actual Python module

  Summary

  Both commands are equivalent and both enable import lerobot:

  1. pip install -e . - Convenience when you're already in the directory
  2. pip install -e /full/path - More explicit, works from anywhere

  After either installation:
  import lerobot  # ✅ Works
  from lerobot.teleoperators.config import TeleoperatorConfig  # ✅ Works

  The "editable" (-e) flag means changes to the source code take effect immediately without
  reinstalling.

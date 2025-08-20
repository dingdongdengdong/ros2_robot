# LeRobot-ROS Integration Guide

## Next Steps After Teleoperation Setup

Once you have teleoperation working with your command:

**Single Arm (SO101):**
```bash
python scripts/teleoperate.py \
  --robot.type=so101_ros \
  --robot.id=my_awesome_follower_arm \
  --teleop.type=gamepad_6dof \
  --teleop.id=my_awesome_leader_arm \
  --display_data=true
```

**Bimanual Arms (SO100) with Single Gamepad:**
```bash
python scripts/teleoperate.py \
  --robot.type=bi_so100_ros \
  --robot.id=my_bimanual_follower_arms \
  --teleop.type=gamepad_6dof \
  --teleop.id=my_awesome_leader_arm \
  --display_data=true
```

**Bimanual Arms (SO100) with Dual Gamepads:**
```bash
python scripts/teleoperate.py \
  --robot.type=bi_so100_ros \
  --robot.id=my_bimanual_follower_arms \
  --teleop.type=dual_gamepad_6dof \
  --teleop.id=my_dual_gamepad_teleop \
  --display_data=true
```

You can use all standard LeRobot features:

### 1. Gamepad Teleoperation

#### Single Gamepad Mode (`gamepad_6dof`)
- **Use Case**: Single arm control or shared control of bimanual robot
- **Control Mapping**:
  - Left joystick: Linear X/Y movement
  - Right joystick: Angular X/Y rotation
  - LR bumpers: Angular Z rotation (yaw)
  - LR triggers: Linear Z movement (up/down)
  - Button: Gripper control

#### Dual Gamepad Mode (`dual_gamepad_6dof`)
- **Use Case**: Independent control of both arms in bimanual robot
- **Setup**: Connect two gamepads to your system
- **Control Mapping** (per gamepad):
  - **Gamepad 0 (Left Arm)**: Controls left arm with same 6DOF mapping
  - **Gamepad 1 (Right Arm)**: Controls right arm with same 6DOF mapping
  - Each gamepad controls its respective arm independently
- **Configuration Options**:
  - `left_gamepad_index: 0` (default)
  - `right_gamepad_index: 1` (default)

### 2. Camera and Sensor Integration
- Add cameras to robot configuration
- Use LeRobot's camera utilities
- Integrate additional sensors as needed

### 3. Data Collection and Training
- **Record demonstrations**: Use `scripts/record.py`
- **Test trajectories**: Use `scripts/replay.py`
- **Train policies**: Use main LeRobot repository tools

---

## Robot Integration Guide

### Arm Control Modes

The system supports three primary arm control modes, each requiring different ROS2 controller setups:

#### Mode 1: Joint Position Control

**Configuration Setting:**
```python
action_type: ActionType = ActionType.JOINT_POSITION
```

**Required ROS2 Controllers:**
- `position_controllers/JointGroupPositionController` for robot arm joints
- `joint_state_broadcaster/JointStateBroadcaster` for joint state feedback

**How it Works:**
- Sends direct joint position targets to each joint
- Uses position controllers from ros2_control package
- Suitable for precise joint-level control

**Example Configuration:**
```python
@RobotConfig.register_subclass("my_position_robot")
@dataclass
class MyPositionRobotConfig(ROS2Config):
    action_type: ActionType = ActionType.JOINT_POSITION
    
    ros2_interface: ROS2InterfaceConfig = field(
        default_factory=lambda: ROS2InterfaceConfig(
            arm_joint_names=["joint_1", "joint_2", "joint_3", "joint_4", "joint_5", "joint_6"],
            min_joint_positions=[-3.14, -1.57, -1.57, -3.14, -1.57, -3.14],
            max_joint_positions=[3.14, 1.57, 1.57, 3.14, 1.57, 3.14],
        )
    )
```

#### Mode 2: Joint Trajectory Control

**Configuration Setting:**
```python
action_type: ActionType = ActionType.JOINT_TRAJECTORY
```

**Required ROS2 Controllers:**
- `joint_trajectory_controller/JointTrajectoryController` for robot arm joints
- `joint_state_broadcaster/JointStateBroadcaster` for joint state feedback

**How it Works:**
- Sends trajectory waypoints with timing information
- Provides smooth motion between points
- More sophisticated than position control

**Example Configuration (SO101 Robot):**
```python
@RobotConfig.register_subclass("so101_ros")
@dataclass
class SO101ROSConfig(ROS2Config):
    action_type: ActionType = ActionType.JOINT_TRAJECTORY
    
    ros2_interface: ROS2InterfaceConfig = field(
        default_factory=lambda: ROS2InterfaceConfig(
            arm_joint_names=["1", "2", "3", "4", "5"],
            gripper_joint_name="6",
            base_link="base",
            min_joint_positions=[-1.91986, -1.74533, -1.74533, -1.65806, -2.79253],
            max_joint_positions=[1.91986, 1.74533, 1.5708, 1.65806, 2.79253],
        )
    )
```

#### Mode 3: End-Effector Cartesian Control

**Configuration Setting:**
```python
action_type: ActionType = ActionType.CARTESIAN_VELOCITY
```

**Required ROS2 Components:**
- `moveit_servo` node for real-time end-effector control
- `joint_trajectory_controller/JointTrajectoryController` for robot arm control
- `joint_state_broadcaster/JointStateBroadcaster` for joint state feedback

**How it Works:**
- Controls end-effector velocity in Cartesian space
- Uses MoveIt Servo for real-time motion
- Provides intuitive spatial control

**Example Configuration (Annin AR4):**
```python
@RobotConfig.register_subclass("annin_ar4_mk1")
@dataclass
class AnninAR4Config(ROS2Config):
    action_type: ActionType = ActionType.CARTESIAN_VELOCITY
    
    ros2_interface: ROS2InterfaceConfig = field(
        default_factory=lambda: ROS2InterfaceConfig(
            base_link="base_link",
            max_linear_velocity=0.10,    # m/s
            max_angular_velocity=0.25,   # rad/s
            min_joint_positions=[-2.9671, -0.7330, -1.5533, -2.8798, -1.8326, -2.7053],
            max_joint_positions=[2.9671, 1.5708, 0.9076, 2.8798, 1.8326, 2.7053],
        )
    )
```

---

### Gripper Control Modes

The system supports two gripper control modes:

#### Mode 1: Trajectory Control (Default)

**Configuration Setting:**
```python
gripper_action_type: GripperActionType = GripperActionType.TRAJECTORY
```

**ROS2 Topic:**
- Publishes to: `/gripper_controller/joint_trajectory`
- Message type: `JointTrajectory`

**How it Works:**
- Uses `JointTrajectoryController` from ros2_control
- Sends trajectory messages with position targets
- Suitable for grippers that accept trajectory commands

**Implementation Details:**
```python
# In ros_interface.py:89-92
self.gripper_traj_pub = self.robot_node.create_publisher(
    JointTrajectory, "/gripper_controller/joint_trajectory", 10
)
```

#### Mode 2: Action Control

**Configuration Setting:**
```python
gripper_action_type: GripperActionType = GripperActionType.ACTION
```

**ROS2 Action:**
- Action server: `/gripper_controller/gripper_cmd`
- Action type: `GripperCommand`

**How it Works:**
- Uses `GripperActionController` from ros2_control
- Sends action goals with position and force parameters
- Provides feedback on goal achievement
- Better for grippers with force feedback

**Implementation Details:**
```python
# In ros_interface.py:94-99
self.gripper_action_client = ActionClient(
    self.robot_node,
    GripperCommand,
    "/gripper_controller/gripper_cmd",
    callback_group=ReentrantCallbackGroup(),
)
```

**Example Configuration (AR4 with Action Control):**
```python
ros2_interface: ROS2InterfaceConfig = field(
    default_factory=lambda: ROS2InterfaceConfig(
        gripper_joint_name="gripper_jaw1_joint",
        gripper_open_position=0.014,
        gripper_close_position=0.0,
        gripper_action_type=GripperActionType.ACTION,
    )
)
```

---

## Complete Robot Configuration Template

Here's a comprehensive template for creating your own robot configuration:

```python
from dataclasses import dataclass, field
from lerobot.robots import RobotConfig
from lerobot_ros.robots.config_ros import (
    ROS2Config, 
    ROS2InterfaceConfig, 
    ActionType, 
    GripperActionType
)

@RobotConfig.register_subclass("my_custom_robot")
@dataclass
class MyCustomRobotConfig(ROS2Config):
    # Choose your arm control mode
    action_type: ActionType = ActionType.JOINT_POSITION  # or JOINT_TRAJECTORY or CARTESIAN_VELOCITY
    
    # Optional: Set relative target limits for safety
    max_relative_target: int | None = None
    
    # Configure ROS2 interface
    ros2_interface: ROS2InterfaceConfig = field(
        default_factory=lambda: ROS2InterfaceConfig(
            # ROS2 namespace (if using one)
            namespace="",
            
            # Joint configuration
            arm_joint_names=[
                "shoulder_joint",
                "upper_arm_joint", 
                "forearm_joint",
                "wrist_1_joint",
                "wrist_2_joint",
                "wrist_3_joint"
            ],
            gripper_joint_name="gripper_joint",
            
            # For cartesian control only
            base_link="base_link",
            max_linear_velocity=0.05,    # m/s
            max_angular_velocity=0.25,   # rad/s
            
            # For position/trajectory control only
            min_joint_positions=[-3.14, -1.57, -1.57, -3.14, -1.57, -3.14],
            max_joint_positions=[3.14, 1.57, 1.57, 3.14, 1.57, 3.14],
            
            # Gripper configuration
            gripper_open_position=0.0,
            gripper_close_position=1.0,
            gripper_action_type=GripperActionType.TRAJECTORY,  # or ACTION
        )
    )
```

## Usage Commands

Once configured, use your robot with these commands:

**Teleoperation (Single Arm):**
```bash
python scripts/teleoperate.py \
  --robot.type=my_custom_robot \
  --robot.id=my_robot_instance \
  --teleop.type=gamepad_6dof \
  --teleop.id=my_teleop \
  --display_data=true
```

**Teleoperation (Bimanual SO100 - Single Gamepad):**
```bash
python scripts/teleoperate.py \
  --robot.type=bi_so100_ros \
  --robot.id=my_bimanual_arms \
  --teleop.type=gamepad_6dof \
  --teleop.id=my_teleop \
  --display_data=true
```

**Teleoperation (Bimanual SO100 - Dual Gamepads):**
```bash
python scripts/teleoperate.py \
  --robot.type=bi_so100_ros \
  --robot.id=my_bimanual_arms \
  --teleop.type=dual_gamepad_6dof \
  --teleop.id=my_dual_teleop \
  --display_data=true
```

**Recording Demonstrations (Dual Gamepads):**
```bash
python scripts/record.py \
  --robot.type=bi_so100_ros \
  --robot.id=my_bimanual_arms \
  --teleop.type=dual_gamepad_6dof \
  --teleop.id=my_dual_teleop \
  --dataset.id=my_dataset \
  --num_episodes=50
```

**Replaying Trajectories:**
```bash
python scripts/replay.py \
  --robot.type=bi_so100_ros \
  --robot.id=my_bimanual_arms \
  --dataset.id=my_dataset \
  --episode_idx=0
```

## Configuration File Locations

- **Main robot configs**: `lerobot_ros/robots/config_ros.py`
- **Teleoperator configs**: `lerobot_ros/teleoperators/config_*.py`
- **Implementation files**: `lerobot_ros/robots/ros.py`, `lerobot_ros/robots/ros_interface.py`

Add your custom configuration class to `config_ros.py` and it will be automatically available for use.
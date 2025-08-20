from dataclasses import dataclass

from lerobot.teleoperators.config import TeleoperatorConfig


@TeleoperatorConfig.register_subclass("dual_gamepad_6dof")
@dataclass
class DualGamepadTeleop6DOFConfig(TeleoperatorConfig):
    """Configuration for dual gamepad teleoperation for bimanual robots.
    
    Uses two gamepads - one for left arm, one for right arm.
    Each gamepad controls 6DOF movement + gripper for its respective arm.
    """
    use_gripper: bool = True
    left_gamepad_index: int = 0  # Gamepad device index for left arm
    right_gamepad_index: int = 1  # Gamepad device index for right arm
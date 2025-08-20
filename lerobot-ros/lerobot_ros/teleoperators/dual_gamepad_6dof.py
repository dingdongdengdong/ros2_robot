from typing import Any

import numpy as np
from lerobot.teleoperators import Teleoperator

from .config_dual_gamepad_6dof import DualGamepadTeleop6DOFConfig
from .gamepad_6dof_utils import GamepadController6DOF


class BimanualGamepadController6DOF(GamepadController6DOF):
    """Extended GamepadController6DOF that supports multiple device indices."""
    
    def __init__(self, device_index=0, x_step_size=1.0, y_step_size=1.0, z_step_size=1.0, rot_step_size=1.0, deadzone=0.1):
        super().__init__(x_step_size, y_step_size, z_step_size, rot_step_size, deadzone)
        self.device_index = device_index
        
    def start(self):
        """Initialize pygame and the specific gamepad by index."""
        import os
        
        # Set SDL environment variable to help with joystick detection
        os.environ['SDL_JOYSTICK_DEVICE'] = f'/dev/input/js{self.device_index}'
        
        import pygame
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() <= self.device_index:
            import logging
            logging.error(f"Gamepad {self.device_index} not found. Only {pygame.joystick.get_count()} gamepads detected.")
            self.running = False
            return

        self.joystick = pygame.joystick.Joystick(self.device_index)
        self.joystick.init()
        import logging
        logging.info(f"Initialized gamepad {self.device_index}: {self.joystick.get_name()}")

        print(f"6DOF Gamepad {self.device_index} controls:")
        print("  Left analog stick: Linear X/Y movement")
        print("  Right analog stick: Angular X/Y rotation (roll/pitch)")
        print("  LB/RB bumpers: Angular Z rotation (yaw)")
        print("  LT/RT triggers: Linear Z movement (up/down)")
        print("  A/X button: Gripper control (open by default, close when pressed)")


class DualGamepadTeleop6DOF(Teleoperator):
    """
    Teleop class for bimanual robot control using two gamepads.
    
    Each gamepad controls one arm with 6-DOF movement:
    - Left joystick: Linear X/Y movement
    - Right joystick: Angular X/Y rotation
    - LR bumpers: Angular Z rotation (yaw)
    - LR triggers: Linear Z movement (up/down)
    - Button: Gripper control (nominally open, close when pressed)
    
    Actions are prefixed with 'left_' and 'right_' for bimanual robots.
    """

    config_class = DualGamepadTeleop6DOFConfig
    name = "dual_gamepad_6dof"

    def __init__(self, config: DualGamepadTeleop6DOFConfig):
        super().__init__(config)
        self.config = config
        self.robot_type = config.type

        self.left_gamepad: BimanualGamepadController6DOF | None = None
        self.right_gamepad: BimanualGamepadController6DOF | None = None

    @property
    def action_features(self) -> dict:
        """Action features for bimanual robot control."""
        base_features = {
            "linear_x.vel": 0,
            "linear_y.vel": 1,
            "linear_z.vel": 2,
            "angular_x.vel": 3,
            "angular_y.vel": 4,
            "angular_z.vel": 5,
        }
        
        # Create left and right arm features
        left_features = {f"left_{key}": val for key, val in base_features.items()}
        right_features = {f"right_{key}": val + 6 for key, val in base_features.items()}
        
        features = {**left_features, **right_features}
        shape_size = 12  # 6 DOF per arm
        
        if self.config.use_gripper:
            features["left_gripper.pos"] = 12
            features["right_gripper.pos"] = 13
            shape_size = 14  # 6 DOF + gripper per arm
            
        return {
            "dtype": "float32",
            "shape": (shape_size,),
            "names": features,
        }

    @property
    def feedback_features(self) -> dict:
        return {}

    def connect(self) -> None:
        """Connect to both gamepads."""
        self.left_gamepad = BimanualGamepadController6DOF(device_index=self.config.left_gamepad_index)
        self.right_gamepad = BimanualGamepadController6DOF(device_index=self.config.right_gamepad_index)
        
        self.left_gamepad.start()
        self.right_gamepad.start()

    def get_action(self) -> dict[str, Any]:
        """Get actions from both gamepads."""
        if self.left_gamepad is None or self.right_gamepad is None:
            raise RuntimeError("Gamepads are not connected. Please call connect() first.")

        # Update both controllers
        self.left_gamepad.update()
        self.right_gamepad.update()

        # Get left arm actions
        left_deltas = self.left_gamepad.get_6dof_deltas()
        left_action = np.array(left_deltas, dtype=np.float32)
        
        # Get right arm actions  
        right_deltas = self.right_gamepad.get_6dof_deltas()
        right_action = np.array(right_deltas, dtype=np.float32)

        # Create action dictionary with prefixed keys
        action_dict = {
            "left_linear_x.vel": left_action[0],
            "left_linear_y.vel": left_action[1], 
            "left_linear_z.vel": left_action[2],
            "left_angular_x.vel": left_action[3],
            "left_angular_y.vel": left_action[4],
            "left_angular_z.vel": left_action[5],
            "right_linear_x.vel": right_action[0],
            "right_linear_y.vel": right_action[1],
            "right_linear_z.vel": right_action[2], 
            "right_angular_x.vel": right_action[3],
            "right_angular_y.vel": right_action[4],
            "right_angular_z.vel": right_action[5],
        }

        # Add gripper controls if enabled
        if self.config.use_gripper:
            left_gripper = self.left_gamepad.gripper_command()
            right_gripper = self.right_gamepad.gripper_command()
            action_dict["left_gripper.pos"] = left_gripper
            action_dict["right_gripper.pos"] = right_gripper

        return action_dict

    def disconnect(self) -> None:
        """Disconnect from both gamepads."""
        if self.left_gamepad is not None:
            self.left_gamepad.stop()
            self.left_gamepad = None
            
        if self.right_gamepad is not None:
            self.right_gamepad.stop() 
            self.right_gamepad = None

    def is_connected(self) -> bool:
        """Check if both gamepads are connected."""
        return (
            self.left_gamepad is not None 
            and self.right_gamepad is not None
        )

    def calibrate(self) -> None:
        """Calibrate both gamepads."""
        # No calibration needed for gamepads
        pass

    def is_calibrated(self) -> bool:
        """Check if gamepads are calibrated."""
        # Gamepads don't require calibration
        return True

    def configure(self) -> None:
        """Configure both gamepads."""
        # No additional configuration needed
        pass

    def send_feedback(self, feedback: dict) -> None:
        """Send feedback to gamepads."""
        # Gamepads don't support feedback
        pass
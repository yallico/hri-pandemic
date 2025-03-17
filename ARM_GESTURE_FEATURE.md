# NAO Robot Arm Gestures During Speech

This document explains the arm gesture feature that has been added to make the NAO robot more expressive when speaking during the pandemic game.

## Feature Overview

When the robot receives a "say:" command, it now:
1. Raises its right arm in a natural gesture
2. Speaks the requested text
3. Lowers its arm back to a neutral position after speaking

This creates a more engaging and human-like interaction during the game.

## Technical Implementation

The feature is implemented through two main methods:

### 1. `raise_arm()` Method

```python
def raise_arm(self):
    """Raise the right arm in a gesture while speaking"""
    try:
        if self.motion:
            # Make sure the robot is stiffened
            self.motion.setStiffnesses("RArm", 1.0)
            
            # Define the arm joints to control
            names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
            
            # Angles for raised arm position (in radians)
            angles = [0.5, -0.2, 1.0, 0.5]  # Raised arm position
            
            # Set arm to raised position with a smooth motion
            self.motion.setAngles(names, angles, 0.2)  # 0.2 is the speed
            
            return True
    except Exception as e:
        return False
```

### 2. `lower_arm()` Method

```python
def lower_arm(self):
    """Return the arm to neutral position"""
    try:
        if self.motion:
            names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
            angles = [1.4, 0.1, 1.5, 0.3]  # More neutral position
            self.motion.setAngles(names, angles, 0.2)
            return True
    except Exception as e:
        return False
```

## Joint Angle Explanation

The arm gesture uses specific angles (in radians) for each joint:

- **RShoulderPitch (0.5)**: Controls vertical arm position
  - Lower values lift the arm higher (0.0 is horizontal)
  
- **RShoulderRoll (-0.2)**: Controls lateral arm position
  - Negative values move the arm outward from the body
  
- **RElbowYaw (1.0)**: Controls rotation of the elbow
  - Different values create different gestures
  
- **RElbowRoll (0.5)**: Controls bending of the elbow
  - Lower values straighten the arm, higher values bend it

## Customization

You can modify the arm gesture by changing the angle values in the `raise_arm()` method. Some examples:

- For a higher arm gesture: `[0.2, -0.3, 1.0, 0.5]`
- For a more bent elbow: `[0.5, -0.2, 1.0, 1.0]`
- For a straighter arm: `[0.5, -0.2, 1.0, 0.3]`

Experiment with different values to find the gesture that best suits your needs.

## Usage Notes

- The arm movement is automatic whenever the robot speaks
- No changes to your Renpy game are needed to use this feature
- If the arm gesture fails for any reason, the robot will still speak
- The robot will always attempt to return to a neutral position after speaking 
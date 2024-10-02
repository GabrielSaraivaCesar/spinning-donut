from enum import Enum, auto as a
# Use this file to change the scenarios. Better than changing it in __main__.py

# Fps counter on the right-bottom side of the render
ENABLE_FPS_COUNTER = True

# Mark a pixel as dirty when it changes, so only the changed pixels need to be updated. Uses more memory. (TODO: Revisit Implementation)
ENABLE_DIRTY_RECTANGLES = False 

# Only project visible faces, ignore faces that are facing away from the camera (TODO: Change the normal face calculation)
ENABLE_BACKFACE_CULLING = True

# Enables object rotation and camera movement 
ENABLE_USER_CONTROL = True

# Rotation speed of the rendered object. If user control is disabled, the object will rotate automatically
ROTATION_SPPEED = 50

ENABLE_SAVE_LOGS = False # Performance logs



CAMERA_SETTINGS = {
    # This is important for the camera because the pixels (in this context, chars) are not really squared, instead the height is usually 2x the width size
    'CHAR_HEIGHT/WIDTH_PROPORTION': 2,
    'RECORDING_SENSOR_SIZE': (1, 1, 1), # X,Y,Zoom - Mimics the camera sensor
    'POSITION': (0, 0, -10),
    'SPEED': 1,
    'ROTATION_SPEED': 30
}

LIGHT_SOURCE = {
    'POSITION': (0, 10, 20),
    'INTENSITY': 1
}


class AvailableMeshes(Enum):
    CUBE = a()
    TOROID = a()
    TOROID_HIGH_POLY = a()
    PYRAMID = a()
    SHUTTLE = a()
    FLOWER = a()
    

ACTIVE_MODEL=AvailableMeshes.FLOWER
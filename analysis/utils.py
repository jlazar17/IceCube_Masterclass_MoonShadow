import numpy as np

def sine(angle):
    # convert to radians
    return np.sin(np.radians(angle))

def is_floatable(v):
    try:
        float(v)
        return True
    except:
        return False

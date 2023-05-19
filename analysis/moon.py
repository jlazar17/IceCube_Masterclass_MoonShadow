import numpy as np
from pyorbital import Moon as POMoon
from datetime import datetime

from .utils import is_floatable
from .jdutil import mjd_to_datetime

class Moon:

    def __init__(self):
        pass

    def position(self, t, lat=-90.0, lon=45.0):
        
        if is_floatable(t):
            t = mjd_to_datetime(t)

        if isinstance(t, str):
            t_split = t.replace(":", "-")
            t_split = [int(x) for x in t.split("-")]
            try:
                t = datetime(*t_split)
            except:
                raise ValueError(
                    f"Cannot convert {t} to datetime"
                )

        moon = POMoon(t)
        _, decl, _, azi = moon.topocentric_position(lon, lat)
        zen = 90 - decl
        azi = azi
        return zen, azi

import numpy as np
import awkward as ak

from tqdm.notebook import tqdm
from typing import Tuple, List
from dataclasses import dataclass

ALLOWED_FIELDS = [
    "direction",
    "energy",
    "zenith",
    "azimuth",
    "time"
]

@dataclass 
class Event:
    direction: Tuple[float, float]
    energy: float
    zenith: float
    azimuth: float
    time: float

    def __getitem__(self, v):
        return getattr(self, v)

class DataReader:
    def __init__(self, filename: str):
        self._filename = filename
        self._energy = None
        self._zenith = None
        self._azimuth = None
        self._direction = None
        self._time = None
        self._photon_info = ak.from_parqet(filename)
        self._events = read_events(filename)
        self._index = 0
        
    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            result = self._events[self._index]
        except IndexError:
            raise StopIteration
        self._index += 1
        return result
    
    def _set_energy(self, v):
        self._energy = v
        
    def _set_zenith(self, v):
        self._zenith = v
        
    def _set_azimuth(self, v):
        self._azimuth = v
        
    def _set_direction(self, v):
        self._direction = v
        
    def _set_time(self, v):
        self._time = v

    @property
    def filename(self):
        return self._filename

    def __len__(self):
        return len(self._events)

    def __getitem__(self, key):

        if isinstance(key, int):
            return self._events[key]
        
        if key not in ALLOWED_FIELDS:
            raise ValueError(
              f"Cannot get the requested field. Allowed fields are {ALLOWED_FIELDS}"
            )
            
        if getattr(self, f"_{key}") is None:
            getattr(self, f"_set_{key}")(np.array([getattr(e, key) for e in self._events]))
            
        return getattr(self, f"_{key}")

def read_events(fname: str) -> DataReader:
    a = ak.from_parquet(fname)
    events = [
        Event(
            (np.degrees(a["reco_quantities", "theta", idx]), np.degrees(a["reco_quantities", "phi", idx])),
            a["mc_truth_initial", "initial_state_energy", idx],
            np.degrees(a["reco_quantities", "theta", idx]),
            np.degrees(a["reco_quantities", "phi", idx]),
            a["times", idx]
        ) for idx in tqdm(range(len(a)))
    ]
    return events

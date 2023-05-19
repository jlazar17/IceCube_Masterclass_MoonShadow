import numpy as np

from moon import Moon
from jdutil import mjd_to_datetime

MOON = Moon()

def new_direction(mjd):
    moon_theta, moon_phi = MOON.position(mjd_to_datetime(mjd))
    new_theta = np.radians(np.random.uniform(-7.5, 7.5)) + moon_theta
    new_phi = np.radians(np.random.uniform(-7.5, 7.5)) / np.sin(new_theta) + moon_phi
    # We need to reverse the direction
    return new_theta, new_phi

def rot_z(theta):
    m = np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0],
        [0, 0, 1]
    ])
    return m

def rot_y(theta):
    m = np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])
    return m

def rotate_particle(particle, init_direction, new_direction):
    m = rot_z(-init_direction[1])
    m = np.matmul(rot_y(-init_direction[0]), m)
    m = np.matmul(rot_y(new_direction[0]), m)
    m = np.matmul(rot_z(new_direction[1]), m)

    init_proj = to_cartesian([1, particle["Direction"][0], particle["Direction"][1]])

    #print(np.dot(particle["Position"], init_proj))
    new_direction = to_spherical(np.matmul(m, init_proj))[1:]
    new_position = np.matmul(m, particle["Position"])
    #print(np.dot(np.matmul(m, init_proj), new_position))
    return new_position, new_direction

def to_spherical(xyz):
    r = np.linalg.norm(xyz)
    theta = np.arccos(xyz[2] / r)
    phi = np.arctan2(xyz[1], xyz[0])
    return np.array([r, theta, phi])

def to_cartesian(rtp):
    x = rtp[0] * np.sin(rtp[1]) * np.cos(rtp[2])
    y = rtp[0] * np.sin(rtp[1]) * np.sin(rtp[2])
    z = rtp[0] * np.cos(rtp[1])
    return np.array([x, y, z])

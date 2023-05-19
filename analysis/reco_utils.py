import numpy as np
from rotation_utils import rot_z, rot_y

def mu(e):
    x = np.log10(e)
    gamma = 3.445
    alpha = 0.0195
    return np.power(x, -gamma) / alpha + 0.3

def sigma(e):
    x = np.log10(e)
    gamma = 3.64
    alpha = 0.0573
    return np.power(x, -gamma) / alpha + 0.15

def mis_reco_angle(e):
    mu_ = mu(e)
    sigma_ = sigma(e)
    mis_reco_angle = max(np.random.normal(loc=mu_, scale=sigma_), 0.05)
    return np.radians(mis_reco_angle)

def fake_reco_direction(mis_reco_angle, true_zenith, true_azimuth):
    phi0 = np.random.rand() * 2 * np.pi
    theta0 = np.arcsin(mis_reco_angle)
    vec = np.array([
        np.sin(theta0) * np.cos(phi0),
        np.sin(theta0) * np.sin(phi0),
        np.cos(theta0)
    ])
    vec = np.matmul(rot_y(true_zenith), vec)
    vec = np.matmul(rot_z(true_azimuth), vec)
    theta = np.arccos(vec[2])
    phi = np.arctan2(vec[1], vec[0])
    return theta, phi

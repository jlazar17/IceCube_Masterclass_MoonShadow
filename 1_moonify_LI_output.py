import numpy as np
import h5py as h5

from moon import Moon
moon = Moon()
from jdutil import mjd_to_jd, jd_to_datetime

ICECUBE_OFFSET = np.array([5.87082946, -2.51860853, -1971.9757655])

def mjd_to_datetime(mjd):
    return jd_to_datetime(mjd_to_jd(mjd))

def new_direction(mjd):
    moon_theta, moon_phi = moon.position(mjd_to_datetime(mjd))
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

def do_it_to_em(events):
    tots = np.zeros((3, 1000, 2))
    tots2 = np.zeros((3, 1000, 3))
    j = 0
    for particle_name in "initial final_1 final_2".split():
        new_dirs = np.zeros(events[particle_name].shape + (2,))
        new_poss = np.zeros(events[particle_name].shape + (3,))
        for idx in range(events[particle_name].shape[0]):
            init_direction = events["initial"]["Direction"][idx]
            init_position = events["initial"]["Position"][idx]
            blah = new_direction(events["times"][idx])
            new_pos, new_dir = rotate_particle(
                events[particle_name][idx],
                init_direction,
                blah
            )
            new_dirs[idx, :] = new_dir
            new_poss[idx, :] = new_pos
        tots[j, :, :] = new_dirs
        tots2[j, :, :] = new_poss
        j += 1
    #return new_dirs, new_poss
    return tots, tots2

def main(h5_fname):
    h5f = h5.File(h5_fname, "r")
    injector = list(h5f.keys())[0]
    outdirs, outposs = do_it_to_em(h5f[injector])

    new_fname = h5_fname.replace(".h5", "_moonify.h5")
    out_h5f = h5.File(new_fname, "w")
    out_h5f.create_group(injector)

    for k, v in h5f[injector].items():
        out_h5f[injector].create_dataset_like(k, v)
        if k=="times":
            out_h5f[injector][k][:] = h5f[f"{injector}/{k}"][:]
            continue
        #if k=="properties":
        #    for name in out_h5f[f"{injector}/{k}"].dtype.names:
        #        if name in "zenith azimuth":
        #            continue
        #        out_h5f[f"{injector}/{k}"][:] = h5f[f"{injector}/{k}"]
        for name in out_h5f[f"{injector}/{k}"].dtype.names:
            out_h5f[f"{injector}/{k}"][:] = h5f[f"{injector}/{k}"]


    # Overwrite important fields
    for idx, k in enumerate("initial final_1 final_2".split()):
        path = f"{injector}/{k}"
        out_h5f[path]["Direction"] = outdirs[idx, :, :]
        out_h5f[path]["Position"] = outposs[idx, :, :]
        out_h5f[path]["Position"] = out_h5f[path]["Position"] + ICECUBE_OFFSET
    out_h5f[injector]["properties"]["zenith"] = outdirs[0, :, 0]
    out_h5f[injector]["properties"]["azimuth"] = outdirs[0, :, 1]
    out_h5f[injector]["properties"]["x"] = out_h5f[injector]["properties"]["x"] + ICECUBE_OFFSET[0]
    out_h5f[injector]["properties"]["y"] = out_h5f[injector]["properties"]["y"] + ICECUBE_OFFSET[1]
    out_h5f[injector]["properties"]["z"] = out_h5f[injector]["properties"]["z"] + ICECUBE_OFFSET[2]
    
    h5f.close()
    out_h5f.close()

if __name__=="__main__":
    import sys
    args = sys.argv
    main(args[1])


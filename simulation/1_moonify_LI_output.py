import numpy as np
import h5py as h5


ICECUBE_OFFSET = np.array([5.87082946, -2.51860853, -1971.9757655])

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


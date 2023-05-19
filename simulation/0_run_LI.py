import numpy as np
import h5py as h5
import LeptonInjector as LI
import EarthModelService as em

ICECUBE_OFFSET = np.array([5.87082946, -2.51860853, -1971.9757655])


def make_xs_paths(final_1):
    nu_str = "nu"
    if "bar" in final_1.lower() or "plus" in final_1.lower():
        nu_str += "bar"

    # Charged outgoing lepton
    if "minus" in final_1.lower() or "plus" in final_1.lower():
        int_str = "CC"
    # Neutral outgoing lepton
    else:
        int_str = "NC"

    xs_dir = "/n/home12/jlazar/prometheus/resources/cross_section_splines"
    diff_xs = f"{xs_dir}/dsdxdy_{nu_str}_{int_str}_iso.fits"
    total_xs = f"{xs_dir}/sigma_{nu_str}_{int_str}_iso.fits"

    return diff_xs, total_xs

def new_injection(final_1, n_event, seed, min_e=5e2, max_e=1e5, gamma=3):

    final_1_LI = getattr(LI.Particle.ParticleType, final_1)
    final_2_LI = LI.Particle.ParticleType.Hadrons

    is_ranged = False
    #if final_1 in "MuMinus MuPlus".split():
    #    is_ranged = True

    diff_xs, total_xs = make_xs_paths(final_1)

    injector = LI.Injector(
        n_event,
        final_1_LI,
        final_2_LI,
        diff_xs,
        total_xs,
        is_ranged
    )

    min_zenith = 0.0
    max_zenith = np.pi
    min_azimuth = 0.0
    max_azimuth = 2 * np.pi

    inject_radius = 1000
    endcap_length = 1000
    cylinder_radius = 900
    cylinder_height = 1200

    if is_ranged:
        controller = LI.Controller(
            injector, min_e, max_e, gamma, min_azimuth,
            max_azimuth, min_zenith, max_zenith, 
        )
    else:
        controller = LI.Controller(
            injector, min_e, max_e, gamma, min_azimuth,
            max_azimuth, min_zenith, max_zenith,
            inject_radius, endcap_length, cylinder_radius, cylinder_height
        )

    earth_model_dir = "/n/home12/jlazar/prometheus/resources/earthparams/"
    earth_model_name = "PREM_south_pole"
    earth = em.EarthModelService(
        "Zorg",
        earth_model_dir,
        [earth_model_name],
        ["Standard"],
        "NoIce",
        0.0,
        ICECUBE_OFFSET[2]
    )
    controller.SetEarthModelService(earth)
    controller.setSeed(seed)

    out_prefix = f"//n/home12/jlazar/IceCube_Masterclass_MoonShadow/output/{final_1}_{seed}"
    outfile = f"{out_prefix}.h5"
    licfile = f"{out_prefix}.lic"
    controller.NameOutfile(outfile)
    controller.NameLicFile(licfile)

    # run the simulation
    controller.Execute()
    # Translate injection to detector coordinate system
    #apply_detector_offset(outfile, ICECUBE_OFFSET)
    np.random.seed(seed)
    add_time(outfile)

def add_time(outfile, tmin=56059.0, tmax=60076.0):
    with h5.File(outfile, "r+") as h5f:
        for v in h5f.values():
            n_event = v["final_1"].shape
            times = np.random.uniform(low=tmin, high=tmax, size=n_event)
            v.create_dataset("times", data=times)

if __name__=="__main__":
    import sys
    args = sys.argv
    final_1 = args[1]
    n_event = int(args[2])
    seed = int(args[3])
    new_injection(final_1, n_event, seed)

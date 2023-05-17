# Authors: Jeffrey Lazar, Stephan Meighen-Berger
# Shows how to generate some simple data sets
# imports

import prometheus
from prometheus import Prometheus, config

RESOURCE_DIR = f"{'/'.join(prometheus.__path__[0].split('/')[:-1])}/resources/"
SOFTWARE_PREFIX = "/n/holylfs05/LABS/arguelles_delgado_lab/Lab/common_software/"

def initialize_args():
    import argparse
    parser =  argparse.ArgumentParser()
    # Meta
    #parser.add_argument(
    #    "-n",
    #    dest="n",
    #    type=int,
    #    required=True,
    #    help="number of events to simulate."
    #)
    #parser.add_argument(
    #   "-s",
    #    "--seed",
    #    dest="seed",
    #    type=int,
    #    required=True,
    #    help="Seed for the random number generator."
    #)
    #parser.add_argument(
    #    "--final_1",
    #    dest="final_1",
    #    type=str,
    #    required=True,
    #    help="Final particle 1 for LeptonInjector. See https://arxiv.org/abs/2012.10449 for more information \
    #    See https://github.com/icecube/LeptonInjector/blob/master/private/LeptonInjector/Particle.cxx#L44 \
    #    for allowed particles."
    #)
    parser.add_argument(
        "--geo_file",
        dest="geo_file",
        type=str,
        #default=f"{RESOURCE_DIR}/geofiles/icecube.geo",
        required=True,
        help="F2k file describing the geometry of the detector"
    )
    parser.add_argument(
        "--emin",
        dest="emin",
        type=float,
        default=5e2,
        help="Minimum energy for the simulation."
    )
    parser.add_argument(
        "--emax",
        dest="emax",
        type=float,
        default=1e5,
        help="Maximum energy for the simulation."
    )
    parser.add_argument(
        "--gamma",
        dest="gamma",
        type=float,
        default=3.0,
        help="Spectral index for sampling"
    )
    parser.add_argument(
        "--force_volume",
        dest="force_volume",
        action="store_true",
        default=False,
        help="Force volume injection."
    )
    # I/O
    parser.add_argument(
        "--output_prefix",
        dest="output_prefix",
        type=str,
        default="/n/home12/jlazar/IceCube_Masterclass_MoonShadow/output/",
        help="Prefix for where the data should be stored. You must have write access"
    )
    parser.add_argument(
        "--injection",
        dest="injection",
        type=str,
        default="",
        help="Path to preexisting injection. If this is not null, we will skip LI"
    )
    parser.add_argument(
        "--ppc_tmpfile",
        dest="ppc_tmpfile",
        type=str,
        default="./.event_hits.ppc.tmp",
        help="Path where you wanna store PPC temporary files"
    )
    parser.add_argument(
        "--f2k_tmpfile",
        dest="f2k_tmpfile",
        type=str,
        default="./.event_losses.f2k.tmp",
        help="Path where you wanna store PROPOSAL temporary files"
    )
    return parser.parse_args()

def is_ranged_injection(final_states) -> bool:
    """Determine whether we should do ranged injection by default.
    We say this should happen if there is a charged mu or tau lepton
    since these can travel pretty far.

    params
    ______
    final_states: LeptonInjector names for all final states

    returns
    _______
    is_ranged: bool saying whether default behavior is to do ranged injection
    """
    ranged_states = "MuMinus MuPlus TauMinus TauPlus".split()
    for final_state in final_states:
        if final_state in ranged_states:
            return True
    return False

def main(args):
    #nevent = args.n
    #seed = args.seed
    #final_2 = "Hadrons"
    detector_name = args.geo_file.split("/")[-1].split(".")[0]
    #prefix = f"{args.final_1}_{detector_name}_{seed:04d}"
    prefix = args.injection.split("/")[-1].split(".")[0]
    seed = prefix.split("_")[-2]
    print(seed)
    #config['run']["nevents"] = nevent
    #config["run"]["random state seed"] = seed
    #config["run"]["run number"] = seed
    #config["run"]["meta_name"] = 'meta_data_%d' % seed
    config['run']['storage prefix'] = (
        f'{args.output_prefix}/'
    )
    config['run']["outfile"] = (
        f"{args.output_prefix}/{prefix}_photons.parquet"
    )
    config["detector"]["geo file"] = args.geo_file
    config["injection"]["LeptonInjector"]["inject"] = False
    config['injection']["LeptonInjector"]['paths']['injection file'] = args.injection
    #is_ranged = is_ranged_injection([args.final_1, final_2])
    #config['injection']["LeptonInjector"]['simulation']['is ranged'] = is_ranged
    #if args.force_volume:
    #    config['injection']["LeptonInjector"]['simulation']['is ranged'] = False
    #config['injection']["LeptonInjector"]['simulation']['final state 1'] = args.final_1
    #config['injection']["LeptonInjector"]['simulation']['final state 2'] = final_2
    #config['injection']["LeptonInjector"]['simulation']['min zenith'] = 0
    #config['injection']["LeptonInjector"]['simulation']['max zenith'] = 180
    #config['injection']["LeptonInjector"]['simulation']['minimal energy'] = args.emin
    #config['injection']["LeptonInjector"]['simulation']['maximal energy'] = args.emax
    #config['injection']["LeptonInjector"]['simulation']["power law"] = args.gamma
    #config['injection']["LeptonInjector"]['paths']['injection file'] = (
    #    f"{args.output_prefix}/{prefix}_LI_output.h5"
    #)
    #config['injection']["LeptonInjector"]['paths']["lic name"] = (
    #    f"{args.output_prefix}/{prefix}_LI_config.lic"
    #)
    #config['injection']["LeptonInjector"]["paths"]['install location'] = (
    #    f"{SOFTWARE_PREFIX}/lib64/"
    #)
    #config['injection']["LeptonInjector"]["paths"]['xsec dir'] = (
    #    f"{RESOURCE_DIR}/cross_section_splines/"
    #)
    if "icecube" in args.geo_file:

        #config["lepton propagator"]['name'] = "old proposal"
        config['photon propagator']['name'] = "PPC_CUDA"
        config['photon propagator']["PPC_CUDA"]["paths"]['outfile'] = (
            f"{args.output_prefix}/{prefix}_photons.parquet"
        )
        config['photon propagator']["PPC_CUDA"]["paths"]['ppc_tmpdir'] = (
            f"/n/holyscratch01/arguelles_delgado_lab/Everyone/jlazar/GraphNeT_simulation/{prefix}_ppc_tmpdir/"
        )
        config['photon propagator']["PPC_CUDA"]["paths"]['ppc_tmpfile'] = args.ppc_tmpfile.replace(".ppc", f"{seed}.ppc")
        config['photon propagator']["PPC_CUDA"]["paths"]['f2k_tmpfile'] = args.f2k_tmpfile.replace(".f2k", f"{seed}.f2k")
        config['photon propagator']["PPC_CUDA"]["paths"]['location'] = "/n/holylfs05/LABS/arguelles_delgado_lab/Lab/common_software/source/PPC_CUDA_new/"
        config['photon propagator']["PPC_CUDA"]["paths"]['ppctables'] = f"/n/home12/jlazar/PPC_tables/south_pole/"
        # Uncomment this line to not use IceCube's angular acceptance
        config['photon propagator']["PPC_CUDA"]["paths"]['ppctables'] = "/n/home12/jlazar/prometheus/resources/PPC_tables/south_pole/"
        config['photon propagator']["PPC_CUDA"]["simulation"]['supress_output'] = False
        config['photon propagator']["PPC_CUDA"]["paths"]['ppc_exe'] = "/n/holylfs05/LABS/arguelles_delgado_lab/Lab/common_software/source/PPC_CUDA_new/ppc"
    prometheus = Prometheus(userconfig=config)
    prometheus.sim()
    del prometheus

if __name__ == "__main__":
    args = initialize_args()
    main(args)

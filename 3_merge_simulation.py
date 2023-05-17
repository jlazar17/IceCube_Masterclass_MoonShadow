import numpy as np
import pyarrow.parquet as pq
import awkward as ak

from tqdm import tqdm
from glob import glob

fs = sorted(glob("./output/*moonify*.parquet"))

n = 0
for f in fs:
    a = ak.from_parquet(f)
    n += len([x for x in a if len(x["photons", "t"]) > 8])


start = 0
initial_truth = {k: np.zeros(n) for k in a["mc_truth_initial"].fields}
final_truth = {k:[] for k in a["mc_truth_final"].fields}
photons = {k:[] for k in a["photons"].fields}
for f in tqdm(fs):
    a = ak.from_parquet(f)
    mask = np.array([len(x["photons", "t"]) > 8 for x in a])
    end = start + int(np.sum(mask))
    for k in a["mc_truth_initial"].fields:
        initial_truth[k][start:end] = a["mc_truth_initial", k, mask]
    for event in a["mc_truth_final", mask]:
        for k in a["mc_truth_final"].fields:
            final_truth[k].append(event[k].to_numpy())
    for event in a["photons", mask]:
        for k in a["photons"].fields:
            photons[k].append(event[k].to_numpy())
    start = end

arr = ak.Array({
    "mc_truth_initial": initial_truth,
    "mc_truth_final": final_truth,
    "photons": photons
})

pq.write_table(ak.to_arrow_table(arr), "./output/MuMinus_icecube_merged.parquet")

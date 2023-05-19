import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import Tuple, List
from ipywidgets import widgets, interact

@dataclass
class PlotHelper:
    position: np.ndarray
    times: List = field(default_factory=lambda: [])

from pyarrow import field


def plot_event(
    event,
    # detector,
    show=True,
    # show_doms=True,
    charge_mult=12,
    cut=1.0,
    loss_threshold=0.1,
    cmap='jet_r',
    # tmethod='mean',
    elevation_angle=0.0,
    azi_angle=None
):

    
    photons = event["photons"]
    # Mask times if cut < 1
    tmin = np.min(photons["t"])
    deltat = np.max(photons["t"]) - tmin
    mask = np.full(len(photons["t"]), True)
    if cut < 1:
        mask = (photons["t"] - tmin) / deltat < cut

    

    om_ids = [
        (int(x[0]), int(x[1])) for x in zip(
            photons["string_id", mask],
            photons["sensor_id", mask]
        )
    ]
    d = {}

    for idx in range(len(photons["t", mask])):
        om_id = (photons["string_id", mask][idx], photons["sensor_id", mask][idx])
        if om_id not in d.keys():
            pos = np.array(
                [
                    photons["sensor_pos_x", mask][idx],
                    photons["sensor_pos_y", mask][idx],
                    photons["sensor_pos_z", mask][idx]
                ]
            )
            d[om_id] = PlotHelper(pos)
        d[om_id].times.append(photons["t", mask][idx])

    positions = np.array([x.position for x in d.values()])
    reduced_times = [np.mean(x.times) for x in d.values()]
    log_charge = np.array([1 + np.log(len(x.times)) for x in d.values()])

    log_charge *= charge_mult
    
    cmap = getattr(plt.cm, cmap)
    c = cmap((reduced_times - tmin) / deltat)

    fig = plt.figure(figsize=(12, 10))
    ax  = fig.add_subplot(111, projection='3d')

    if len(positions) > 0:
        ax.scatter(
            positions[:, 0],
            positions[:, 1],
            positions[:, 2],
            c=c,
            alpha=0.4,
            s=log_charge,
            zorder=10
        )

      # XYZ = np.array([m.pos for m in detector.modules]) + detector.offset
      # # Plot all DOMs
      # px.scatter_3d(
      #     XYZ[:,0],
      #     XYZ[:,1],
      #     XYZ[:,2],
      #     # c='black',
      #     opacity=0.1,
      #     size=0.2
      # )

    # Make the panes transparent
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

    # Make the grid lines transparent TODO make this work ????
    ax.xaxis._axinfo['grid']['color'] =  (1.0, 1.0, 1.0, 0.0)
    ax.yaxis._axinfo['grid']['color'] =  (1.0, 1.0, 1.0, 0.0)
    ax.zaxis._axinfo['grid']['color'] =  (1.0, 1.0, 1.0, 0.0)

    ax.axes.set_xlim3d(left=-500, right=500)
    ax.axes.set_ylim3d(bottom=-500, top=500) 
    ax.axes.set_zlim3d(bottom=-2450, top=-1450) 
    
    # Rotate the axes and update
    if azi_angle is None:
        azi_angle = np.degrees(event["mc_truth_initial", "initial_state_azimuth"]+np.pi/2)
    ax.view_init(elevation_angle, azi_angle)
    # plt.savefig(figname, bbox_inches='tight')

    # Show the plot if interactive view was requested
    # px.show()

    plt.show()


def interactive_plot(event):
    def progressive_plot(cut, event):
        plot_event(event,  cut=cut)

    f = lambda x: progressive_plot(x, event)

    return interact(f, x=(0,1,0.01))
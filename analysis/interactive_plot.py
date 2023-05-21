import numpy as np
import plotly.graph_objs as go
import plotly as plotly
from IPython.display import display

offset_x = -5.87082946
offset_y = 2.51860853
offset_z = 1971.9757655

def plot_interactive_event(event, human_zenith, human_azimuth, field='mc_truth', show_truth=False):

    total_x = event.photons.sensor_pos_x.to_numpy() + offset_x
    total_y = event.photons.sensor_pos_y.to_numpy() + offset_y
    total_z = event.photons.sensor_pos_z.to_numpy() + offset_z
    total_t = event.photons.t.to_numpy()

    pos_t = np.array([
        total_x,
        total_y,
        total_z,
        total_t
    ]).T

    cog_point = pos_t.mean(axis=0)[:3]

    # only plot first hit on unique DOM
    spos_t = pos_t[np.argsort(pos_t[:,-1])]
    _, indices, feats = np.unique(spos_t[:,:3], axis=0, return_index=True, return_counts=True)
    vox = spos_t[indices]

    layout = go.Layout(
    width=1000,
    height=550,
    legend=dict(x=0, y=1),
    hovermode='closest',
    margin=dict(l=0,r=0,b=0,t=0),                                                                                                                                                                                                                                                                          
    uirevision = 'true',
    scene = dict(xaxis = dict(nticks=10, range = (-578,572), showticklabels=True, title='x', visible=True),
                yaxis = dict(nticks=10, range = (-520,514), showticklabels=True, title='y', visible=True),
                zaxis = dict(nticks=10, range = (-490,550), showticklabels=True, title='z', visible=True),
                aspectmode='cube')
    )

    pts = go.Scatter3d(x=vox[:,0], y=vox[:,1], z=vox[:,2], customdata=vox[:,3], mode='markers', opacity=0.8, marker=dict(
            size=3,
            color=vox[:,3],     # set color to an array/list of desired values
            colorscale='Jet',   # choose a colorscale
            reversescale=True,
        ), hoverinfo=['x','y','z','text'], hovertext=['%.2f ns' % v for v in vox[:,3]], 
                    hovertemplate="x: %{x} m, y: %{y} m, z: %{z} m, t: %{customdata} ns")

    # human estimate direction
    human_dir, human_arrows = generate_directional_vector(human_zenith, human_azimuth, cog_point, color='black', name='Your guess')

    # true direction
    if show_truth:
      true_dir, true_arrows_trace = generate_directional_vector(event[field].initial_state_zenith, event[field].initial_state_azimuth, cog_point, color='red', name='Truth')
      fig = go.FigureWidget(data=[pts, true_dir, true_arrows_trace, human_dir, human_arrows], layout=layout)
    else:
      fig = go.FigureWidget(data=[pts, human_dir, human_arrows], layout=layout)
    return fig

def generate_directional_vector(zenith, azimuth, initial_pos, color='black', name='vector'):
    dir_x = np.cos(azimuth) * np.sin(zenith)
    dir_y = np.sin(azimuth) * np.sin(zenith)
    dir_z = np.cos(zenith)

    start_x = (initial_pos[0]) - (dir_x * 1500)
    start_y = (initial_pos[1]) - (dir_y * 1500)
    start_z = (initial_pos[2]) - (dir_z * 1500)

    end_x = (dir_x * 1500) + (initial_pos[0])
    end_y = (dir_y * 1500) + (initial_pos[1])
    end_z = (dir_z * 1500) + (initial_pos[2])

    true_line = np.array([[start_x, start_y, start_z],
                          [end_x, end_y, end_z]])

    true_dir = go.Scatter3d(
        name=name,
        x=true_line[:,0], y=true_line[:,1], z=true_line[:,2],
        marker=dict(
            size=4,
            color=color
        ),
        line=dict(
            color=color,
            width=6
        )
    )

    dir_vec = np.array([dir_x, dir_y, dir_z])

    # Define the number of arrows to add along the line
    num_arrows = int(15)

    # Create a list of positions to place the arrows
    arrow_pos = np.linspace(true_line[0], true_line[1], num_arrows+2)[1:-1]

    # Create a list of arrow directions
    arrow_dir = np.array([dir_vec * 100] * num_arrows)

    # Create the arrows
    arrows_trace = go.Cone(
        x=arrow_pos[:,0],
        y=arrow_pos[:,1],
        z=arrow_pos[:,2],
        u=arrow_dir[:,0],
        v=arrow_dir[:,1],
        w=arrow_dir[:,2],
        anchor='center',
        colorscale='Greys', showscale=False, sizemode='absolute', sizeref=40
    )

    return true_dir, arrows_trace

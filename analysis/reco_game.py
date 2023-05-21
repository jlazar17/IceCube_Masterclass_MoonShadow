# #@title Run me!
import numpy as np
from analysis.interactive_plot import plot_interactive_event


from google.colab import output
output.enable_custom_widget_manager()

from IPython.display import display, clear_output

EVENT_LIST = [24, 18973, 25456, 80336, 18901, 172, 47547, 5717, 831, 696, 82031, 3458, 755, 58125, 385]
TRACK_EVENT_DICT = {str(idx+1): v for idx, v in enumerate(EVENT_LIST)}
CASCADE_EVENT_DICT = {str(idx+1): idx for idx in range(10)}


def calculate_angular_difference(zenith1, azimuth1, zenith2, azimuth2):
    # Convert angles to Cartesian coordinates
    cartesian1 = np.array([
        np.sin(zenith1) * np.cos(azimuth1),
        np.sin(zenith1) * np.sin(azimuth1),
        np.cos(zenith1)
    ])
    cartesian2 = np.array([
        np.sin(zenith2) * np.cos(azimuth2),
        np.sin(zenith2) * np.sin(azimuth2),
        np.cos(zenith2)
    ])

    # Normalize vectors to unit length
    cartesian1 /= np.linalg.norm(cartesian1)
    cartesian2 /= np.linalg.norm(cartesian2)

    # Calculate dot product
    dot_product = np.dot(cartesian1, cartesian2)

    # Calculate angular difference (in radians)
    angular_difference_rad = np.arccos(dot_product)

    # Convert to degrees
    angular_difference_deg = np.degrees(angular_difference_rad)

    return angular_difference_deg

from ipywidgets import interact, interactive, FloatSlider, Dropdown, Button, Layout
from plotly.subplots import make_subplots



def intermediate_plot_fn(events, x, y, z):
    ed = TRACK_EVENT_DICT
    if events._photon_info["mc_truth_initial", "initial_state_type", 0]==12:
        ed = CASCADE_EVENT_DICT
    fig = plot_interactive_event(events._photon_info[ed[x]], y, z, field='mc_truth_initial', show_truth=False)
    display(fig)

def return_to_game(button, event_id, zenith, azimuth, events):
    clear_output()
    submit_button = Button(description='Submit')
    submit_button.on_click(reco_results)
    f = lambda x,y,z: intermediate_plot_fn(events, x, y, z)
    interact(f, x=event_id, y=zenith, z=azimuth, continuous_update=False)
    display(submit_button)

def reco_results(events, button, event_id, zenith, azimuth):
    # global event_id, zenith, azimuth
    x = event_id.value
    y = zenith.value
    z = azimuth.value
    clear_output()
    ed = TRACK_EVENT_DICT
    if events._photon_info["mc_truth_initial", "initial_state_type", 0]==12:
        ed = CASCADE_EVENT_DICT
    fig = plot_interactive_event(events._photon_info[ed[event_id.value]], y, z, field='mc_truth_initial', show_truth=True)
    display(fig)
    true_zenith = events._photon_info[ed[event_id.value]].mc_truth_initial.initial_state_zenith
    true_azimuth = events._photon_info[ed[event_id.value]].mc_truth_initial.initial_state_azimuth
    # true_azimuth = events._photon_info[int(event_id.value)].mc_truth_initial.initial_state_azimuth
    ad = calculate_angular_difference(true_zenith, true_azimuth, zenith.value, azimuth.value)
    print('Your estimate was ' + str(ad) + ' degrees off the true direction.')
    button.close()
    return_button = Button(description='Return')
    f = lambda button: return_to_game(button, event_id, zenith, azimuth, events)
    return_button.on_click(f)
    display(return_button)

def reco_game(events):
    zenith = FloatSlider(min=0, max=3.14, step=0.01, value=0, description='zenith',
                     layout=Layout(width='75%'))
    azimuth = FloatSlider(min=-3.14, max=3.14, step=0.01, value=0, description='azimuth',
                     layout=Layout(width='75%'))
    event_id = Dropdown(value='1', options=[str(x+1) for x in range(10)], description='event_id', disabled=False)
    submit_button = Button(description='Submit')
    g = lambda button: reco_results(events, button, event_id, zenith, azimuth)
    submit_button.on_click(g)
    # submit_button.on_click(reco_results)
    f = lambda x, y, z: intermediate_plot_fn(events, x, y, z)
    interact(f, x=event_id, y=zenith, z=azimuth, continuous_update=False)
    display(submit_button)

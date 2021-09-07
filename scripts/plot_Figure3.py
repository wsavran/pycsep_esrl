# Python imports
import os
import json
import time

# 3rd party impoorts
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# pycsep imports
from csep import load_catalog_forecast, load_catalog, load_json
from csep.models import Event
from csep.core.regions import (
    Polygon,
    generate_aftershock_region,
    california_relm_region,
    masked_region,
    magnitude_bins,
    create_space_magnitude_region
)
from csep.core.forecasts import GriddedDataSet
from csep.utils.constants import SECONDS_PER_WEEK
from csep.utils.plots import plot_spatial_dataset
from csep.utils.scaling_relationships import WellsAndCoppersmith
from csep.utils.time_utils import epoch_time_to_utc_datetime

# local imports
from experiment_utilities import california_experiment, italy_experiment

# file-path for results
simulation_dir = '/Users/wsavran/Research/ridgecrest_evaluation_bssa/2019_09_04-ComCatM7p1_ci38457511_ShakeMapSurfaces'
ucerf3_raw_data = os.path.join(simulation_dir, 'results_complete.bin')
ucerf3_config = os.path.join(simulation_dir, 'config.json')
m71_event = os.path.join(simulation_dir, 'm71_event.json')

# magnitude range
min_mw = 3.95
max_mw = 8.95
dmw = 0.2

# percentiles to plot in figure
perc = [5, 50, 95, 99.9]

# define start and end epoch of the forecast
with open(ucerf3_config, 'r') as config_file:
    config = json.load(config_file)
start_epoch = config['startTimeMillis']
end_epoch = start_epoch + SECONDS_PER_WEEK * 1000

# number of fault radii to use for spatial filtering
num_radii = 3 

# load event
event = load_json(Event(), m71_event)

# define aftershock region and magnitude region
rupture_length = WellsAndCoppersmith.mag_length_strike_slip(event.magnitude) * 1000
aftershock_polygon = Polygon.from_great_circle_radius((event.longitude, event.latitude), num_radii*rupture_length, num_points=100)
aftershock_region = masked_region(california_relm_region(dh_scale=4), aftershock_polygon)
mw_bins = magnitude_bins(min_mw, max_mw, dmw)
smr = create_space_magnitude_region(aftershock_region, mw_bins)

# create forecast object
u3etas_forecast = load_catalog_forecast(
    ucerf3_raw_data,
    start_time = epoch_time_to_utc_datetime(start_epoch),
    end_time = epoch_time_to_utc_datetime(end_epoch),
    region=smr,
    event=event,
    type='ucerf3',
    filter_spatial=True,
    apply_filters=True,
)

# plot forecast; will add catalog to plot, calling first because u3etas is a generator and not subscriptable
_ = u3etas_forecast.get_expected_rates()

# determine catalogs with percentile counts
ecs = u3etas_forecast.get_event_counts()
idxs = []
for p in perc:
    ec = np.percentile(ecs, p)
    idxs.append(np.argwhere(ecs == ec)[0])

# plotting goes here
fig = plt.figure(figsize=(18,10))
axs = []
for i, idx in enumerate(idxs):
    axs.append(fig.add_subplot(2,2,i+1, projection=ccrs.Mercator()))
fig.subplots_adjust(wspace=-0.175, hspace=0.2)
args_dict = {
    'legend': True,
    'legend_loc': 1,
    'frameon': True,
    'mag_ticks': [4.0, 5.0, 6.0, 7.0],
    'mag_scale': 6,
    'markercolor': 'gray',
    'legend_titlesize': 12
}
for ax, idx in zip(axs, idxs):
    args_dict['catalog'] = u3etas_forecast.catalogs[int(idx)]
    h = u3etas_forecast.plot(plot_args=args_dict, ax=ax)
ax.get_figure().savefig('../figures/figure3.png', dpi=300)
plt.show()

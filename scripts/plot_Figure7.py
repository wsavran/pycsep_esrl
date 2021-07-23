# 3rd party impoorts
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# local imports
from experiment_utilities import italy_experiment

# pycsep imports
from csep import load_catalog, load_gridded_forecast
from csep.utils.plots import plot_basemap, plot_catalog, plot_spatial_dataset


def initalize_forecasts(config, **kwargs):
    """ Initialize forecast using experiment configuration """
    out = {}
    for name, path in config.forecasts.items():
        print(f'Loading {name} forecast...')
        fore = load_gridded_forecast(path, **kwargs)
        fore.start_time = config.start_time
        fore.end_time = config.end_time
        fore.name = name
        out[name] = fore
    return out


### Create composite map and customize it


# 1) Basemap

Projection = ccrs.Mercator()   # Uses cartopy to define a projection
extent = [6, 19, 34, 49]          # [min(lon), max(lon), min(lat), max(lat)]

# Basemap can be defined using a predefined str, which can be looked up in the csep.utils.plots.plot_basemap()
# documentation (e.g. stamen_terrain, google-satellite, ESRI_terrain, etc.), or a Tile Map Server URL
# (ESRI Hillshade in here).
basemap = 'https://services.arcgisonline.com/arcgis/rest/services/' \
          'Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}.jpg'

# Create an 'ax' object containing the basemap
ax = plot_basemap(basemap, extent,
                    projection=Projection,
                    coastline=True,
                    borders=True,
                    linewidth=0.4,
                    linecolor='gray',
                    grid=True,
                    grid_labels=True)
ax.get_figure().savefig('../figures/Figure7_a.png', dpi=200, transparent=True)

# 2) Spatial Dataset

print('Loading Italy Forecasts')
# Get forecasts and their properties
ita_fores = initalize_forecasts(italy_experiment, swap_latlon=True)
ita_region = ita_fores['werner'].region
ita_mw_bins = ita_fores['werner'].get_magnitudes()

# Post-process the forecasts into a desired value.
# Here, we want to see the difference between two forecasts within a given magnitude range

# Filter the forecasts into a defined magnitude range
low_bound = 5.55
upper_bound = 5.95
mw_ind = np.where(np.logical_and(ita_mw_bins >= low_bound, ita_mw_bins <= upper_bound))[0]

discrete_rate_werner = ita_fores['werner'].data[:, mw_ind]   # Get the rates per magnitude bin within the range
rate_werner = np.sum(ita_fores['werner'].data[:, mw_ind], axis=1)  # Get the cumulative rate in such range

discrete_rate_meletti = ita_fores['meletti'].data[:, mw_ind]
rate_meletti = np.sum(ita_fores['meletti'].data[:, mw_ind], axis=1)

rate_diff = np.log10(rate_meletti/rate_werner)     # Get the fraction between both forecasts
rate_diff_cartesian = ita_region.get_cartesian(rate_diff)  # Transform the result into a cartesian 2D array

# Define the plot arguments
colormap_title = r'$\mathrm{log}_{10}\,\dfrac{\lambda_{\mathrm{meletti}}}{\lambda_{\mathrm{werner}}},\quad' \
                 r'\forall m\in[5.55,5.95]$'
args = {'cmap': 'coolwarm',
        'alpha': 0.6,
        'clim': (-2, 2),
        'clabel': colormap_title,
        'region_border': False,
        'linewidth': 0.4}
## Plot the spatial dataset, using the previously defined basemap 'ax' as argument.
ax = plot_spatial_dataset(rate_diff_cartesian, ita_region, ax=ax, extent=extent, plot_args=args)
ax.get_figure().savefig('../figures/Figure7_b.png', dpi=200, transparent=True)


# 3) Cata;pg

# Load the observation catalog
ita_cat = load_catalog(italy_experiment.evaluation_catalog, loader=italy_experiment.catalog_loader)
# Filter by the magnitude range
ita_cat.filter([f'magnitude >= {low_bound}',f'magnitude <= {upper_bound}'])
cat_mags = ita_cat.get_magnitudes()
# Plot arguments
args = {'alpha': 0.5,
        'markercolor': 'gray',
        'legend': True,
        'legend_loc': 3,
        'mag_ticks': [min(cat_mags), max(cat_mags)],
        'markersize': 0.01,
        'mag_scale': 14,
        'linewidth': 0.4}
# Plot the catalog, using the previously obtained spatial_dataset 'ax' object as argument
ax = plot_catalog(ita_cat, ax=ax, extent=extent, plot_args=args)
ax.get_figure().savefig('../figures/Figure7_c.png', dpi=200, transparent=True)



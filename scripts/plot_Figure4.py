# Python imports
import time

# 3rd party impoorts
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# pycsep imports
from csep import load_gridded_forecast, load_catalog
from csep import poisson_evaluations as poisson
from csep.utils.plots import plot_poisson_consistency_test

# local imports
from experiment_utilities import california_experiment, italy_experiment

# evaluate california_experiment
california_results = []
cat = load_catalog(
    california_experiment.evaluation_catalog,
    loader=california_experiment.catalog_loader,
)
print(cat)

for name, path in california_experiment.forecasts.items():

    print(f'Loading {name} forecast for California...')
    fore = load_gridded_forecast(path)
    fore.start_time = california_experiment.start_time
    fore.end_time = california_experiment.end_time
    fore.name = name
    cat.region = fore.region
    print(f'Computing N-test results...')
    california_results.append(poisson.number_test(fore, cat))

# evaluate italy_experiment
italy_results = []
seed = italy_experiment.seed
cat = load_catalog(
    italy_experiment.evaluation_catalog,
    loader=italy_experiment.catalog_loader,
)
for name, path in italy_experiment.forecasts.items():

    print(f'Loading {name} forecast for italy...')
    fore = load_gridded_forecast(path, swap_latlon=True)
    fore.start_time = italy_experiment.start_time
    fore.end_time = italy_experiment.end_time
    fore.name = name
    cat.region = fore.region
    cat.filter(f'magnitude >= {fore.min_magnitude}')

    print(f'Computing S-test results...')
    italy_results.append(poisson.spatial_test(fore, cat, seed=seed))


# plotting code below
fig, (ax1, ax2) = plt.subplots(1,2, figsize=(12,5))
args = {'title_fontsize': 18,
        'xticks_fontsize': 9,
        'ylabel_fontsize': 9,
        'linewidth': 0.8,
        'capsize': 3,
        'hbars':True,
        'tight_layout': True}
args['title'] = r'$\mathcal{N}-\mathrm{test}$'
args['xlabel'] = 'Event count'
ax1 = plot_poisson_consistency_test(california_results, plot_args=args, axes=ax1)

args['title'] = r'$\mathcal{S}-\mathrm{test}$'
args['xlabel'] = 'Log-likelihood'
args['percentile'] = 99
ax2 = plot_poisson_consistency_test(italy_results, plot_args=args, one_sided_lower=True, axes=ax2)
fig.savefig('../figures/Figure4.png', dpi=300)
plt.show()



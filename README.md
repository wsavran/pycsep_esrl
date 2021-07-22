# pycsep_esrl
Scripts and data to generate figures for pyCSEP eSRL manuscript 

# Re-create figures
To plot figures, first activate an environment that contains pyCSEP. Individual figures can be re-created 
by running the `plot_Figure?.py` scripts contained in the `./scripts/` folder. Commands are shown below.
```
git clone git@github.com:wsavran/pycsep_esrl.git
cd pycsep_esrl/scripts
python plot_Figure?.py
```
# To-do
- Figure3
- Figure5
- Figure7
- move data files from github to zenodo
- docker container with pycsep installation (will issue release with new hotfixes)
- script to automatically generate figures
  - create environment (using docker)
  - download data (from zenodo)
  - run all plot_Figure?.py scripts
  - if using latex, re-compile paper (this could run on CI as well, so repo always has up-to-date paper, stored in .pdf)

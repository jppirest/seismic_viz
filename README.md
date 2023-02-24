# seismic_viz

Repository to visualize 3D seismic data.

 
 ## Introduction ##
The tool is entirely based on Gael Varoquaux <gael.varoquaux@normalesup.org> Volume Slicer, with adaptations to load the segy file and visualization adaptions to geophysical interpretations.

The goal is to interactively visualize seismic data.


## Requirements ##

Mayavi is an old library, thus many errors are prone to happen. The main challenge is to run the mayavi and other UI api's without any problems.

* `apt-get install libvtk6-dev `
* `pip install pyqt5`
* `pip install vtk`
* `pip install mayavi`
* `pip install segyio`


## Usage ##

It's pretty straight-forward:

* if you have a .segy file, run the segytonpy function to load the data

```python
seismic = segytonpy(file_path)
```

* if you have a .npy file, run the loadnpy function to load the data

```python
seismic = loadnpy(file_path)
```
Worth mentioning that .npy files are muuuuuch faster to load. If possible, on first time opening a .segy file, make sure to save a .npy file and load it, instead of opening as .segy everytime.

On the data_cut variable, you are able to cut the seismic data, in order to load/render faster.

Then, voilà, if no errors associated to mayavi, traits and tvtk appear, you should get a mayavi scene plot. On the mayavi layout, it's possible to change the colormap, the color range and many other graph configurations.

![Example of the plot window](/seismic_viz.png "Window plotting the seismic data")


## To-Do ##

* Label-color the data
* Make it possible to run in a ipynb notebook (for some reason, ipy is unable to render it)

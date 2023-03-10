# Author: João Pedro Pires <jppirest@gmail.com>, based on Gael Varoquaux <gael.varoquaux@normalesup.org> code.

import mayavi.mlab as mlab
import numpy as np
import vtk
import time



#file_path = 'TrainingData_Image.segy'

def segytonpy(file_path:str) -> np.array:
    from segyio.tools import cube as cubesegy
    seismic_data = cubesegy(file_path)
    return seismic_data

def loadnpy(file_path:str) -> np.array:    
    seismic_data = np.load(file_path)
    return seismic_data


s = time.time() 
seismic = loadnpy('seismic.npy')
# labels = segytonpy('TrainingData_Labels.segy')
s = time.time() - s

print(f"Read in {s:.2f}")


################################################################################
# This script is based on Volume Slicer by Gael Varoquaux.

# Author: Gael Varoquaux <gael.varoquaux@normalesup.org>
# Copyright (c) 2009, Enthought, Inc.
# License: BSD Style.


################################################################################
# Loading UI, mayavi and others apis

from traits.api import HasTraits, Instance, Array, Button, \
    on_trait_change
from traitsui.api import View, Item, HGroup, Group

from tvtk.api import tvtk
from tvtk.pyface.scene import Scene

from mayavi.core.api import PipelineBase, Source
from mayavi.core.ui.api import SceneEditor, MayaviScene, \
                                MlabSceneModel


################################################################################
# Create some data

data_cut = seismic[:,:,:200] #### Cutting the seismic on z-axis in order to lower the loading/rendering time
# labels_cut = labels[:,:,0:10]
cut_shapes = data_cut.shape


################################################################################
# The object implementing the dialog
class VolumeSlicer(HasTraits):
    # The data to plot
    data = Array()
    # The 4 views displayed
    scene3d = Instance(MlabSceneModel, ())
    scene_x = Instance(MlabSceneModel, ())
    scene_y = Instance(MlabSceneModel, ())
    scene_z = Instance(MlabSceneModel, ())


    # The data source
    data_src3d = Instance(Source)
    
    # The image plane widgets of the 3D scene
    ipw_3d_x = Instance(PipelineBase)
    ipw_3d_y = Instance(PipelineBase)
    ipw_3d_z = Instance(PipelineBase)

    _axis_names = dict(x=0, y=1, z=2)


    #---------------------------------------------------------------------------
    def __init__(self, **traits):
        super(VolumeSlicer, self).__init__(**traits)
        # Force the creation of the image_plane_widgets:
        self.ipw_3d_x
        self.ipw_3d_y
        self.ipw_3d_z


    #---------------------------------------------------------------------------
    # Default values
    #---------------------------------------------------------------------------
    def _position_default(self):
        return 0.5*np.array(self.data.shape)
    
    def _data_src3d_default(self):
        return mlab.pipeline.scalar_field(self.data,
                            figure=self.scene3d.mayavi_scene)

    def make_ipw_3d(self, axis_name):
        ipw = mlab.pipeline.image_plane_widget(self.data_src3d,
                        figure=self.scene3d.mayavi_scene,
                        plane_orientation='%s_axes' % axis_name, colormap = 'gray')
        return ipw

    def _ipw_3d_x_default(self):
        return self.make_ipw_3d('x')

    def _ipw_3d_y_default(self):
        return self.make_ipw_3d('y')

    def _ipw_3d_z_default(self):
        return self.make_ipw_3d('z')


    #---------------------------------------------------------------------------
    # Scene activation callbaks
    #---------------------------------------------------------------------------
    
    
    @on_trait_change('scene3d.activated')
    def display_scene3d(self):
        outline = mlab.pipeline.outline(self.data_src3d,
                        figure=self.scene3d.mayavi_scene, colormap = 'gray'
                        )
        self.scene3d.mlab.view(75, 60)
        # Interaction properties can only be changed after the scene
        # has been created, and thus the interactor exists
        for ipw in (self.ipw_3d_x, self.ipw_3d_y, self.ipw_3d_z):
            # Turn the interaction off
            ipw.ipw.interaction = 0
        self.scene3d.scene.background = (0, 0, 0)
        # Keep the view always pointing up
        self.scene3d.scene.interactor.interactor_style = \
                                 tvtk.InteractorStyleTerrain()


    def make_side_view(self, axis_name):
        scene = getattr(self, 'scene_%s' % axis_name)

        # To avoid copying the data, we take a reference to the
        # raw VTK dataset, and pass it on to mlab. Mlab will create
        # a Mayavi source from the VTK without copying it.
        # We have to specify the figure so that the data gets
        # added on the figure we are interested in.

        outline = mlab.pipeline.outline(
                            self.data_src3d.mlab_source.dataset,
                            figure=(scene.mayavi_scene)
                            )
        ipw = mlab.pipeline.image_plane_widget(
                            outline,
                            plane_orientation='%s_axes' % axis_name, colormap = 'gray')
        setattr(self, 'ipw_%s' % axis_name, ipw)

        # mlab.axes()
        # mlab.axes.label_format='%.0f'

        # Synchronize positions between the corresponding image plane
        # widgets on different views.
        ipw.ipw.sync_trait('slice_position',
                            getattr(self, 'ipw_3d_%s'% axis_name).ipw)

        # Make left-clicking create a crosshair
        ipw.ipw.left_button_action = 0

        # Add a callback on the image plane widget interaction to
        # move the others
        def move_view(obj, evt):
            position = obj.GetCurrentCursorPosition()
            for other_axis, axis_number in self._axis_names.items():
                if other_axis == axis_name:
                    continue
                ipw3d = getattr(self, 'ipw_3d_%s' % other_axis)
                ipw3d.ipw.slice_position = position[axis_number]

        ipw.ipw.add_observer('InteractionEvent', move_view)
        ipw.ipw.add_observer('StartInteractionEvent', move_view)

        # Center the image plane widget
        ipw.ipw.slice_position = 0.5*self.data.shape[
                    self._axis_names[axis_name]]

        # Position the view for the scene
        views = dict(x=(0, 90),
                     y=(90, 90),
                     z=(180,0),
                     )

        #! Important ! ------------> Side views are hugely impact. In order to make seismic's visualization "right", had to roll along Z-axis.
        #! Yet to understand the x-axis and y-axis orientation.

        # if axis_name == 'z':
        #     scene.mlab.view(azimuth = 0, elevation = 0, roll = 270)
        # else:
        scene.mlab.view(*views[axis_name])

        # 2D interaction: only pan and zoom
        scene.scene.interactor.interactor_style = \
                                tvtk.InteractorStyleImage()

        scene.scene.background = (0, 0, 0)


    @on_trait_change('scene_x.activated')
    def display_scene_x(self):
        return self.make_side_view('x')


    @on_trait_change('scene_y.activated')
    def display_scene_y(self):
        return self.make_side_view('y')

    @on_trait_change('scene_z.activated')
    def display_scene_z(self):
        return self.make_side_view('z')
    

    #---------------------------------------------------------------------------
    # The layout of the dialog created
    #---------------------------------------------------------------------------
    view = View(HGroup(
                  Group(
                       Item('scene3d', label = '3D Seismic',
                            editor=SceneEditor(scene_class=MayaviScene),
                            height=250, width=300),
                       Item('scene_x', label = f'  Z-Y Plane \n  {cut_shapes[2]}x{cut_shapes[1]} ',
                            editor=SceneEditor(scene_class=Scene),
                            height=250, width=300),
                       show_labels=True,
                  ),

                  Group(
                        Item('scene_z', label = f'  X-Y Plane \n  {cut_shapes[0]}x{cut_shapes[1]}',
                            editor=SceneEditor(scene_class=Scene),
                            height=250, width=300),
                       Item('scene_y', label = f'Plane Z-X \n  {cut_shapes[2]}x{cut_shapes[0]}',
                            editor=SceneEditor(scene_class=Scene),
                            height=250, width=300),
                       show_labels=True,
                  ),
                ),
                resizable=True,
                title='3D Seismic Visualization',
                )


m = VolumeSlicer(data=data_cut)
m.configure_traits()
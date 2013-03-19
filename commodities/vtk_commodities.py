import time

import numpy as np
from numpy import linspace
from scipy.special import jn


from traits.api import HasTraits, Any, Array, Instance
from tvtk.api import tvtk
from mayavi import mlab
from mayavi.modules.glyph import Glyph
from enable.vtk_backend.vtk_window import EnableVTKWindow
from chaco.api import ArrayPlotData, Plot, OverlayPlotContainer
from chaco.tools.api import (PanTool, ZoomTool, MoveTool,
                                       RangeSelection, RangeSelectionOverlay)
from chaco.scales.api import CalendarScaleSystem
from chaco.scales_tick_generator import ScalesTickGenerator
from chaco.axis import PlotAxis as ScalesPlotAxis


# Helper function to load data
def read_time_series_from_csv(filename, dtype=['float32', 'float32', 'float32'], first_line_header=True, separator=',', date_col=None, date_format="%d/%b/%y"):
    """ Read a csv file of N columns.
        Parameters:
          - filename: string for file path and name.
          - dtype: list of valid dtype codes to cast column values into
          - first_line_header: True/False does the first line of the csv
                contain header labels?
          - separator: in case the csv file is "X"sv.
          - date_col: special case for time series data to specify which col contains
                text representing a date.
          - date_format: normal python date string format codes for translating date
                string into seconds since the Epoch
    """

    cast = np.cast
    data = [[] for placeholder in xrange(len(dtype))]
    linecount=0
    for line in open(filename, 'r'):
        if linecount!=0 or not first_line_header:
            fields = line.strip().split(separator)
            data[0].append
            for i, number in enumerate(fields):
                # make sure there are no "quotes" around the date text
                dt = number.strip("\"")
                if i==date_col:
                    data[i].append(time.mktime(time.strptime(dt, date_format)))
                else:
                    data[i].append(number)
        else:
            tmpdtype = []
            names = line.strip().split(separator)
            for i, name in enumerate(names):
                tmpdtype.append(tuple([name.strip("\""), dtype[i]]))
            dtype = np.dtype(tmpdtype)

        linecount=1
    for i in xrange(len(dtype)):
        data[i] = cast[dtype[i]](data[i])
    return np.rec.array(data, dtype=dtype)


class MLabChacoPlot(HasTraits):
    
    prices = Array
    m = Instance(Glyph)
    
    def __init__(self, **kw):
        super(MLabChacoPlot, self).__init__(**kw)
        
        self.prices = get_data()
        x = self.prices['Date']
        pd = ArrayPlotData(index = x)
        pd.set_data("y", self.prices["Crude Supply"])

        # Create some line plots of some of the data
        plot = Plot(pd, bgcolor="none", padding=30, border_visible=True, 
                     overlay_border=True, use_backbuffer=False)
        #plot.legend.visible = True
        plot.plot(("index", "y"), name="Crude Price", color=(.3, .3, .8, .8))
        #plot.tools.append(PanTool(plot))

        plot.tools.append(PanTool(plot, constrain=True, drag_button="right",
                                  constrain_direction="x"))

        range_plt = plot.plots['Crude Price'][0]

        range_selection = RangeSelection(range_plt, left_button_selects=True)
        range_selection.on_trait_change(self.update_interval, 'selection')
        range_plt.tools.append(range_selection)
        range_plt.overlays.append(RangeSelectionOverlay(range_plt))


        zoom = ZoomTool(component=plot, tool_mode="range", always_on=False,
                        axis="index", max_zoom_out_factor=1.0,)
        plot.overlays.append(zoom)

        # Set the plot's bottom axis to use the Scales ticking system
        scale_sys = CalendarScaleSystem(fill_ratio=0.4,
                                        default_numlabels=5,
                                        default_numticks=10,)
        tick_gen = ScalesTickGenerator(scale=scale_sys)

        bottom_axis = ScalesPlotAxis(plot, orientation="bottom",
                                     tick_generator=tick_gen,
                                     label_color="white",
                                     line_color="white")

        # Hack to remove default axis - FIXME: how do I *replace* an axis?
        del(plot.underlays[-2])

        plot.overlays.append(bottom_axis)

        # Create the mlab test mesh and get references to various parts of the
        # VTK pipeline
        f = mlab.figure(size=(700,500))
        self.m = mlab.points3d(self.prices['Gasoline Supply'], self.prices['Jet Fuel Supply'], self.prices['Distillate Supply'], self.prices['Crude Supply'])
        
        # Add another glyph module to render the full set of points
        g2 = Glyph()
        g2.glyph.glyph_source.glyph_source.glyph_type = "circle"
        g2.glyph.glyph_source.glyph_source.filled = True
        g2.actor.property.opacity = 0.75
        self.m.module_manager.source.add_module(g2)
        
        # Set a bunch of properties on the scene to make things look right
        self.m.module_manager.scalar_lut_manager.lut_mode = 'PuBuGn'
        self.m.glyph.mask_points.random_mode = False
        self.m.glyph.mask_points.on_ratio = 1
        self.m.scene.isometric_view()
        self.m.scene.background = (.9, 0.95, 1.0)
        
        scene = mlab.gcf().scene
        render_window = scene.render_window
        renderer = scene.renderer
        rwi = scene.interactor

        plot.resizable = ""
        plot.bounds = [600,120]
        plot.padding = 25
        plot.bgcolor = "white"
        plot.outer_position = [30,30]
        plot.tools.append(MoveTool(component=plot,drag_button="right"))

        container = OverlayPlotContainer(bgcolor = "transparent",
                        fit_window = True)
        container.add(plot)

        # Create the Enable Window
        window = EnableVTKWindow(rwi, renderer, 
                component=container,
                istyle_class = tvtk.InteractorStyleTrackballCamera, 
                bgcolor = "transparent",
                event_passthrough = True,
                )

        mlab.show()
        #return window, render_window
    
    def update_interval(self, selected):
        
        if not selected is None:
            p = self.prices['Date']>=selected[0]
            q = self.prices['Date']<=selected[1]
            msk = p & q
            x, y, z, scalars = self.prices['Gasoline Supply'][msk], self.prices['Jet Fuel Supply'][msk], self.prices['Distillate Supply'][msk], self.prices['Crude Supply'][msk]
            
            self.m.glyph.mask_input_points = True
            self.m.glyph.mask_points.offset = int(msk.argmax())
            self.m.glyph.mask_points.maximum_number_of_points = len(x)
            
            self.m.update_data()
        
        else:
            x, y, z, scalars = (self.prices['Gasoline Supply'],
                                self.prices['Jet Fuel Supply'],
                                self.prices['Distillate Supply'],
                                self.prices['Crude Supply'])
            self.m.glyph.mask_input_points = False
            self.m.update_data()

def get_data():
    prices = read_time_series_from_csv("./commodity_supply.csv",
                dtype=["float32", "float32", "float32", "float32", "float32"],
                date_col=0,
                date_format="%m/%d/%Y")

    return prices

if __name__=="__main__":
    
    test = MLabChacoPlot()


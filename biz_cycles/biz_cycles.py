#!/usr/bin/env python
# encoding: utf-8
"""
biz_cycles.py

Created by Travis Vaught on 2009-07-30.
Copyright (c) 2009 Vaught Consulting.

License: BSD

"""

# Standard library imports
import time

# Major package imports
import numpy as np

# Enthought package imports
from enthought.traits.api import HasTraits, Array, Instance, Str
from enthought.traits.ui.api import View, Item
from enthought.chaco.api import (add_default_grids, ArrayPlotData, DataRange1D,
                                FilledLinePlot, PlotLabel,
                                LinePlot, LinearMapper, OverlayPlotContainer,
                                Plot, VPlotContainer, GridContainer)

from enthought.chaco.tools.api import (PanTool, ZoomTool, LineInspector,
                                       RangeSelection, RangeSelectionOverlay)
from enthought.chaco.scales.api import CalendarScaleSystem
from enthought.chaco.scales_tick_generator import ScalesTickGenerator
from enthought.chaco.axis import PlotAxis as ScalesPlotAxis
from enthought.enable.component_editor import ComponentEditor


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
                print i, name
                tmpdtype.append(tuple([name.strip("\""), dtype[i]]))
            dtype = np.dtype(tmpdtype)

        linecount=1
    for i in xrange(len(dtype)):
        data[i] = cast[dtype[i]](data[i])
    return np.rec.array(data, dtype=dtype)


class CyclesPlot(HasTraits):
    """ Simple plotting class with some attached controls"""
    plot = Instance(GridContainer)
    traits_view = View(
        Item('plot',editor=ComponentEditor(), show_label=False),
        width=800, height=600, resizable=True, title="Business Cycles Plot")

    # Private Traits
    _file_path = Str
    _dates = Array
    _series1 = Array
    _series2 = Array
    _selected_s1 = Array
    _selected_s2 = Array

    def __init__(self):
        super(CyclesPlot, self).__init__()
        
        # Normally you'd pass in the data, but I'll hardwire things for this
        #    one-off plot.
        
        srecs = read_time_series_from_csv("./biz_cycles2.csv",
                                          date_col=0, date_format="%Y-%m-%d")
        
        dt = srecs["Date"]
        
        # Industrial production compared with trend (plotted on value axis)
        iprod_vs_trend = srecs["Metric 1"]
        
        # Industrial production change in last 6 Months (plotted on index axis)
        iprod_delta = srecs["Metric 2"]

        self._dates = dt
        self._series1 = self._selected_s1 = iprod_delta
        self._series2 = self._selected_s2 = iprod_vs_trend
        
        end_x = np.array([self._selected_s1[-1]])
        end_y = np.array([self._selected_s2[-1]])
        
        plotdata = ArrayPlotData(x=self._series1,
                                 y=self._series2,
                                 dates=self._dates,
                                 selected_x=self._selected_s1,
                                 selected_y=self._selected_s2,
                                 endpoint_x=end_x,
                                 endpoint_y=end_y)
                                 
        cycles = Plot(plotdata, padding=20)

        cycles.plot(("x", "y"),
                type="line",
                color=(.2, .4, .5, .4))

        cycles.plot(("selected_x", "selected_y"),
                  type="line",
                  marker="circle",
                  line_width=3,
                  color=(.2, .4, .5, .9))
                  
        cycles.plot(("endpoint_x", "endpoint_y"),
                type="scatter",
                marker_size=4,
                marker="circle",
                color=(.2, .4, .5, .2),
                outline_color=(.2, .4, .5, .6))

        
        cycles.index_range = DataRange1D(low_setting=80.,
                                       high_setting=120.)

        cycles.value_range = DataRange1D(low_setting=80.,
                                       high_setting=120.)
        
        # dig down to use actual Plot object
        cyc_plot = cycles.components[0]
        
        # Add the labels in the quadrants
        cyc_plot.overlays.append(PlotLabel("\nSlowdown" + 40*" " + "Expansion",
                                  component=cyc_plot,
                                  font = "swiss 24",
                                  color = (.2, .4, .5, .6),
                                  overlay_position="inside top"))
      
        cyc_plot.overlays.append(PlotLabel("Downturn" + 40*" " + "Recovery\n ",
                                component=cyc_plot,
                                font = "swiss 24",
                                color = (.2, .4, .5, .6),
                                overlay_position="inside bottom"))
                           
        timeline = Plot(plotdata, resizable='h', height=50, padding=20)
        timeline.plot(("dates", "x"),
                      type="line",
                      color=(.2, .4, .5, .8),
                      name='x')
        timeline.plot(("dates", "y"),
                      type="line",
                      color=(.5, .4, .2, .8),
                      name='y')

        # Snap on the tools
        zoomer = ZoomTool(timeline,
                      drag_button="right",
                      always_on=True,
                      tool_mode="range",
                      axis="index",
                      max_zoom_out_factor=1.1)

        panner = PanTool(timeline, constrain=True,
                       constrain_direction="x")
        
        # dig down to get Plot component I want
        x_plt = timeline.plots['x'][0]
        
        range_selection = RangeSelection(x_plt, left_button_selects=True)
        range_selection.on_trait_change(self.update_interval, 'selection')
        
        x_plt.tools.append(range_selection)
        x_plt.overlays.append(RangeSelectionOverlay(x_plt))
        
        # Set the plot's bottom axis to use the Scales ticking system
        scale_sys = CalendarScaleSystem(fill_ratio=0.4,
                                        default_numlabels=5,
                                        default_numticks=10,)
        tick_gen = ScalesTickGenerator(scale=scale_sys)

        bottom_axis = ScalesPlotAxis(timeline, orientation="bottom",
                                     tick_generator=tick_gen)

        # Hack to remove default axis - FIXME: how do I *replace* an axis?
        del(timeline.underlays[-2])
        
        timeline.overlays.append(bottom_axis)
        
        container = GridContainer(padding=20, fill_padding=True,
                                  bgcolor="lightgray", use_backbuffer=True,
                                  shape=(2,1), spacing=(30,30))
        
        # add a central "x" and "y" axis
        
        x_line = LineInspector(cyc_plot, is_listener=True,
                             color="gray",
                             width=2)
        y_line = LineInspector(cyc_plot, is_listener=True,
                          color="gray",
                          width=2,
                          axis="value")
                          
        cyc_plot.overlays.append(x_line)
        cyc_plot.overlays.append(y_line)
        
        cyc_plot.index.metadata["selections"] = 100.0
        cyc_plot.value.metadata["selections"] = 100.0
        
        container.add(cycles)
        container.add(timeline)

        container.title = "Business Cycles"
        
        self.plot = container

        
    def update_interval(self, value):
        
        # Reaching pretty deep here to get selections
        sels = self.plot.plot_components[1].plots['x'][0].index.metadata['selections']
        
        if not sels is None:
            p = self._dates>=sels[0]
            q = self._dates<=sels[1]
            msk = p & q

            self._selected_s1 = self._series1[msk]
            self._selected_s2 = self._series2[msk]

            # Find the index of the last point in the mask
            last_idx = -(msk[::-1].argmax()+1)
            endpoint_x = np.array([self._series1[last_idx]])
            endpoint_y = np.array([self._series2[last_idx]])

        else:
            self._selected_s1 = self._series1
            self._selected_s2 = self._series2
            endpoint_x = np.array([self._series1[-1]])
            endpoint_y = np.array([self._series2[-1]])

        self.plot.plot_components[0].data['selected_x'] = self._selected_s1
        self.plot.plot_components[0].data['selected_y'] = self._selected_s2
        self.plot.plot_components[0].data['endpoint_x'] = endpoint_x
        self.plot.plot_components[0].data['endpoint_y'] = endpoint_y
        

if __name__ == "__main__":
    CyclesPlot().configure_traits()

#### EOF ####################################################################
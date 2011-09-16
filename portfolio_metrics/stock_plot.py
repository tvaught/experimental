

# Standard library imports
import time

# Major package imports
import numpy as np
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, List, Int, Str
from traitsui.api import Item, Group, View

from chaco.api import ArrayPlotData, Plot, add_default_grids, PlotAxis
from chaco.tools.api import RangeSelection, RangeSelectionOverlay
from chaco.scales.api import CalendarScaleSystem
from chaco.scales_tick_generator import ScalesTickGenerator

# Local imports
from mpt import Stock

#===============================================================================
# Attributes to use for the plot view.
title="Simple line plot"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class StockPlot(HasTraits):

    stocks = List(Instance(Stock))
    colors = List()
    plot = Instance(Component)
    title = Str("Stock Prices")
    height = Int(200)
    width = Int(300)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=(300,200)),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title="Stock Plot",
                    width=300, height=200
                    )

    def __init__(self, *args, **kw):

        super(StockPlot, self).__init__(*args, **kw)

        self.plot = self._create_plot_component()

    def _create_plot_component(self):

        index = np.array([time.mktime(x.timetuple()) for x in self.stocks[0].dates.tolist()])
        #print index

        pd = ArrayPlotData(index=index)

        for i in range(len(self.stocks)):
            pd.set_data("y%s" % i, self.stocks[i].stock_prices)

        #plot = create_line_plot((x,y), color=(0,0,1,1), width=2.0, index_sort="ascending")
        plot = Plot(pd, bgcolor="none", padding=30, border_visible=True,
                     overlay_border=True, use_backbuffer=False)

        for i in range(len(self.stocks)):
            plot.plot(("index", "y%s" % i), name=self.stocks[i].symbol, color=self.colors[i])
            
        value_range = plot.value_mapper.range
        index_range = plot.index_mapper.range
        plot.active_tool = RangeSelection(plot, left_button_selects=True)
        #plot.overlays.append(RangeSelectionOverlay(component=plot))
        #plot.bgcolor = "white"
        plot.padding = 50
        add_default_grids(plot)
        # add_default_axes(plot)

        # Set the plot's bottom axis to use the Scales ticking system
        scale_sys = CalendarScaleSystem(fill_ratio=0.4,
                                        default_numlabels=5,
                                        default_numticks=10,)
        tick_gen = ScalesTickGenerator(scale=scale_sys)

        bottom_axis = PlotAxis(plot, orientation="bottom",
                                     tick_generator=tick_gen,
                                     label_color="white",
                                     line_color="white")

        # Hack to remove default axis - FIXME: how do I *replace* an axis?
        del(plot.underlays[-4])

        plot.overlays.append(bottom_axis)

        return plot

    def _plot_default(self):
         return self._create_plot_component()

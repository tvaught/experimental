

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
import metrics

#===============================================================================
# Attributes to use for the plot view.
title="Simple line plot"

#===============================================================================
# # Demo class that is used by the demo.py application.
#===============================================================================
class StockPlot(Plot):
    """ Object to plot stock baskets relative to one another.
    Parameters:
        stocks: List of mpt.Stock objects
        colors: List of Colors
    Returns:
        Chaco component plotting stocks together

    """
    stocks = List(Instance(Stock))
    colors = List()
    plot = Instance(Component)
    title = Str("Stock Prices")

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title="Stock Plot"
                    )

    def __init__(self, *args, **kw):

        super(StockPlot, self).__init__(*args, **kw)

        self.plot = self._create_plot_component()

    def normal_drag_over(self, event):
        from wx import DragCopy # adapt to your needs (wx.Drag...)
        event.window._drag_result = DragCopy # allow call to normal_dropped_on
        event.handled = True

    def normal_dropped_on(self, event):
        dropped_obj = event.obj
        print dropped_obj
        event.handled = True

    def _create_plot_component(self):

        # find longest date
        index_lengths = []
        for stock in self.stocks:
            if stock.stock_data_cache is not None:
                index_lengths.append(len(stock.stock_data_cache['date']))
            else:
                index_lengths.append(len(stock.stock_data['date']))

        index_lengths = np.array(index_lengths)
        lngest = index_lengths.argmax()
        shrtest = index_lengths.argmin()

        index = np.array([time.mktime(x.timetuple()) for x in self.stocks[lngest].dates.tolist()])

        sel_range_low = time.mktime(self.stocks[shrtest].dates.tolist()[0].timetuple())
        sel_range_high = time.mktime(self.stocks[shrtest].dates.tolist()[-1].timetuple())

        sel_range_low_idx = np.where(index==sel_range_low)[0].item()
        sel_range_high_idx = np.where(index==sel_range_high)[0].item()

        pd = ArrayPlotData()

        # Now plot the returns for each asset (cumulative sum of periodic rates of return)
        for i in range(len(self.stocks)):
            if self.stocks[i].stock_data_cache is None:
                stk = self.stocks[i].stock_data
            else:
                stk = self.stocks[i].stock_data_cache
            pd.set_data("idx%s" % i, np.array([time.mktime(x.timetuple()) for x in stk['date'].tolist()]))
            pd.set_data("y%s" % i, metrics.rate_array(stk)['rate'].cumsum())

        plot = Plot(pd, bgcolor="none", padding=30, border_visible=True,
                     overlay_border=True, use_backbuffer=False)

        for i in range(len(self.stocks)):
            # hang on to a reference to the last one of these...
            plt = plot.plot(("idx%s" % i, "y%s" % i), name=self.stocks[i].symbol, color=self.colors[i])

        #value_range = plot.value_mapper.range
        #index_range = plot.index_mapper.range

        plt[0].active_tool = RangeSelection(plt[0], left_button_selects=True)
        plt[0].active_tool.selection=[index[sel_range_low_idx], index[sel_range_high_idx]]
        plt[0].overlays.append(RangeSelectionOverlay(component=plt[0]))
        #plot.bgcolor = "white"
        plot.padding = 50
        add_default_grids(plot)

        # Set the plot's bottom axis to use the Scales ticking system
        scale_sys = CalendarScaleSystem(fill_ratio=0.4,
                                        default_numlabels=5,
                                        default_numticks=10,)
        tick_gen = ScalesTickGenerator(scale=scale_sys)

        bottom_axis = PlotAxis(plot, orientation="bottom",
                                     tick_generator=tick_gen,
                                     label_color="white",
                                     line_color="white")

        # Hack to remove default axis - TODO: how do I *replace* an axis?
        del(plot.underlays[-4])

        plot.overlays.append(bottom_axis)
        plot.legend.visible = True
        return plot

    def _plot_default(self):
         return self._create_plot_component()

#!/usr/bin/env python
# encoding: utf-8
"""
chaco_mpt_display.py

Created by Travis Vaught on 2011-08-23.
Copyright (c) 2011 Vaught Management, LLC.
License: BSD
"""

# Major library imports
import numpy as np

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, List, Str, Button
from traitsui.api import Item, Group, View, SetEditor

# Chaco imports
from chaco.api import (ArrayPlotData, Plot, PlotGraphicsContext,
                      ScatterInspectorOverlay, LabelAxis, jet, VPlotContainer)
from chaco.tools.api import PanTool, ZoomTool, DataLabelTool, ScatterInspector

# Local imports
from data_point_label import DataPointLabel
from metrics import TRADING_DAYS_PER_YEAR
import mpt
import price_utils

db = "data/stocks.db"

# TODO: Get rid of "tolist" requirement
symbols = price_utils.load_symbols_from_table(dbfilename=db)['symbol'].tolist()

# Some other ways to do symbols ...
#init_symbols = ["CSCO", "AAPL", "IBM",  "MSFT", "GE", "WFC", "RIG", "T", "AA", "CAT"]
init_symbols = ["AAPL", "CSCO", "EOG", "YUM", "AA", "BA", "COP"]
#init_symbols = "data/SP500.csv"
init_symbols.sort()

class PortfolioModel(HasTraits):
    
    symbols = List(init_symbols, editor=SetEditor(values=symbols,
                                   can_move_all=True,
                                   left_column_title='Symbols',
                                   right_column_title='Selected Symbols',
                                   )
                                  )
    dbfilename = Str(db)
    portfolio = Instance(mpt.Portfolio)
    plot = Instance(Component)

    recalc_button = Button(label='Recalculate')
    save_plot_button = Button(label='Save Plot')
    
    traits_view = View(
                    Group(
                        Group(
                        Item('plot',
                             editor=ComponentEditor(size=(600,380)),
                             show_label=False),
                        orientation="vertical",
                        show_labels=False
                        ),
                        Group(
                            Item('symbols', style="simple"),
                            Group(
                                Item('recalc_button', show_label=False),
                                Item('save_plot_button', show_label=False),
                                orientation="vertical"),
                            orientation="horizontal",
                            show_labels=False),
                        orientation="horizontal",
                        show_labels=False
                        ),
                    resizable=True,
                    title="Markowitz Mean-Variance View (MPT)"
                    )

    def __init__(self, *args, **kw):
        self.symbols.sort()
        super(PortfolioModel, self).__init__(*args, **kw)
        self.plot = self._create_plot_component()

    def _recalc_button_fired(self, event):
        self.symbols.sort()
        self.plot = self._create_plot_component(recalc=True)
        #self.plot.invalidate_draw()
        self.plot.request_redraw()

    def _save_plot_button_fired(self, event):
        save_plot(pm.plot, "chaco_ef.png", 400,300)

    def _plot_default(self):
        return self._create_plot_component()
    
    def get_stock_data(self):
        
        self.portfolio = p = mpt.Portfolio(symbols=self.symbols,
                                 startdate="2000-07-1", enddate="2005-12-31",
                                 dbfilename=db)
                                 
        # Assemble and report pre-optimized portfolio data
        x = []
        y = []

        for symbol in p.symbols:
            stk = p.stocks[symbol]
            x.append(stk.annual_volatility)
            y.append(stk.annualized_adjusted_return)
    
        return x, y
    
    def get_ef_data(self):
    
        # Note: The risk tolerance variable seems to require a daily
        # volatility value, given our daily rate data.  So, to make this more
        # friendly, start with annual volatility and convert for our
        # calculations.
        rt0 = 0.05
        rtn = 4.0
        rtstep = 0.2
        tdy = TRADING_DAYS_PER_YEAR
        rtrange = np.arange(rt0/tdy, rtn/tdy, rtstep/tdy)

        efx = []
        efy = []
        allocations = {}
        
        p = self.portfolio
    
        for rt in rtrange:
            p.optimize_portfolio(rt=rt, lower_bound_weight=0.0, upper_bound_weight=1.0)
            px = p.port_opt.volatility
            py = p.port_opt.portfolio_return
            efx.append(px)
            efy.append(py)
            # convert to annual returns in %
            allocations[round(rt * 100, 2)] = p.port_opt.weights
        
            # reset the optimization
            p.port_opt = None

        # cache the results
        self.efx = efx
        self.efy = efy
        self.allocations = allocations

        return efx, efy, allocations


    def _create_plot_component(self, recalc=False):

        container = VPlotContainer()

        ### Assemble the scatter plot of the Efficient Frontier
        x, y = self.get_stock_data()
        if not hasattr(self, "efx") or recalc:
            efx, efy, allocations = self.get_ef_data()
        else:
            efx = self.efx
            efy = self.efy

        p = self.portfolio

        symbs = p.symbols

        pd = ArrayPlotData(x=x, y=y, efx=efx, efy=efy)

        # Create some plots of the data
        plot = Plot(pd, title="Efficient Frontier")

        # Create a scatter plot (and keep a handle on it)
        stockplt = plot.plot(("x", "y"), color=(0.0,0.0,0.5,0.25),
                                         type="scatter",
                                         marker="circle")[0]

        efplt = plot.plot(("efx", "efy"), color=(0.0,0.5,0.0,0.25),
                                          type="scatter",
                                          marker="circle")[0]
        efpltline = plot.plot(("efx", "efy"), color=(0.0,0.7,0.0,0.5),
                                          type="line")[0]

        for i in range(len(p.stocks)):
            label = DataPointLabel(component=plot, data_point=(x[i], y[i]),
                              label_position="bottom right",
                              padding=4,
                              bgcolor="transparent",
                              border_visible=False,
                              text=self.symbols[i],
                              marker="circle",
                              marker_color=(0.0,0.0,0.5,0.25),
                              marker_line_color="blue",
                              arrow_size=6.0,
                              arrow_min_length=7.0)

            plot.overlays.append(label)

            tool = DataLabelTool(label, drag_button="left", auto_arrow_root=True)
            label.tools.append(tool)

        stockplt.tools.append(ScatterInspector(stockplt, selection_mode="toggle",
                                          persistent_hover=False))

        scatinsp = ScatterInspectorOverlay(stockplt,
                hover_color = "red",
                hover_marker_size = 8,
                hover_outline_color = (0.7, 0.7, 0.7, 0.5),
                hover_line_width = 1)

        stockplt.overlays.append(scatinsp)

        # Tweak some of the plot properties
        plot.padding = 50
        stockplt.value_range.low=-0.3
        stockplt.value_range.high=0.7
        stockplt.index_range.low=0.0
        stockplt.index_range.high=0.8
        # Attach some tools to the plot
        plot.tools.append(PanTool(plot, drag_button="right"))
        plot.overlays.append(ZoomTool(plot))

        #### Assemble the "stacked area" plot
        if not hasattr(self, "efx") or recalc:
            a = self.get_ef_data()[2]
        else:
            a = self.allocations

        rts = a.keys()
        rts.sort()
        rts = np.array(rts)

        cpd = ArrayPlotData(x=rts)

        symbs = a[rts[0]].keys()
        symbs.sort()

        # "Transpose" symbols' weights to get vectors of weights for each symbol
        symb_data = np.array([[a[rt][symb] for rt in rts] for symb in symbs])

        # Create a scalar field to contour
        xs = np.linspace(rts[0], rts[-1], len(rts))
        ys = np.linspace(0.0, 1.0, 100)
        x, y = np.meshgrid(xs,ys)

        # TODO: a complicated formula to hack a contour plot into a stacked area plot...

        offset = np.zeros(rts.shape)
        symb_bounds = []

        for row in symb_data:
            lb = offset
            ub = row + offset
            symb_bounds.append(zip(lb,ub))
            offset = ub

        symb_bounds = np.array(symb_bounds)

        zvals = range(0,100)

        z = np.ones(x.shape)

        for i in range(len(symb_bounds)):
            for j in range(len(symb_bounds[i])):
                lmsk = y[:,j]>=symb_bounds[i,j,0]
                umsk = y[:,j]<symb_bounds[i,j,1]
                msk = lmsk & umsk
                z[msk,j] = zvals[i]

        # Create a plot data object and give it this data
        cpd = ArrayPlotData()
        cpd.set_data("stacks", z)

        # Create a contour polygon plot of the data
        cplot = Plot(cpd, title="Allocations")
        cplot.contour_plot("stacks",
                      type="poly",
                      poly_cmap=jet,
                      xbounds=(xs[0], xs[-1]),
                      ybounds=(ys[0], ys[-1]))

        cplot.padding = 50

        container.add(cplot)
        container.add(plot)
        return container


def save_plot(plot, filename, width, height):
    plt_bounds = plot.outer_bounds
    plot.do_layout(force=True)
    gc = PlotGraphicsContext(plt_bounds, dpi=72)
    gc.render_component(plot)
    gc.save(filename)
    print "Plot saved to: ", filename


if __name__ == "__main__":

    pm = PortfolioModel()
    pm.configure_traits()

#### EOF #################################################################


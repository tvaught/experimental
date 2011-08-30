#!/usr/bin/env python
# encoding: utf-8
"""
chaco_mpt_display.py

Created by Travis Vaught on 2011-08-23.
Copyright (c) 2011 Vaught Consulting. All rights reserved.
"""

# Major library imports
import numpy as np

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, List, Str, Tuple, Button
from traitsui.api import Item, Group, View, SetEditor

# Chaco imports
from chaco.api import (ArrayPlotData, Plot, Label, PlotGraphicsContext,
                      DataRange1D, ArrayDataSource)
from chaco.tools.api import PanTool, ZoomTool, DataLabelTool

# Local imports
from data_point_label import DataPointLabel
import mpt
from metrics import TRADING_DAYS_PER_YEAR

#symbols = ["CSCO", "AAPL", "IBM",  "MSFT", "GE", "WFC", "RIG", "T", "AA", "CAT"]

symbols = ["AGN", "NYX", "EOG", "WLP", "CPB", "NYT", "YUM", "JWN"]
#symbols = "data/SP500.csv"
db = "data/stocks.db"

#symbols = ["VQNPX", "NAESX", "VGSIX", "VFSTX", "VGPMX", "VPACX"]
#db = "data/indexes.db"


class PortfolioModel(HasTraits):
    
    symbols = List(symbols, editor=SetEditor(values=symbols,
                                   can_move_all=True,
                                   left_column_title='Symbols',
                                   right_column_title='Selected Symbols'))
    dbfilename = Str(db)
    portfolio = Instance(mpt.Portfolio)
    plot = Instance(Component)
    recalc_button = Button(label='Recalculate')
    
    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=(400,300)),
                             show_label=False),
                        Item('symbols', style="custom"),
                        Item('recalc_button', show_label=False),
                        orientation = "horizontal",
                        show_labels=False),
                    resizable=True, title="Efficient Frontier"
                    )

    def __init__(self, *args, **kw):
        super(PortfolioModel, self).__init__(*args, **kw)
        self.plot = self._create_plot_component()

    def _recalc_button_fired(self, event):
        self.plot = self._create_plot_component()
        #self.plot.invalidate_draw()
        self.plot.request_redraw()

    def _plot_default(self):
        return self._create_plot_component()
    
    def get_stock_data(self):
        
        self.portfolio = p = mpt.Portfolio(symbols=self.symbols,
                                 startdate="2001-08-1", enddate="2011-08-11",
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
        rtn = 1.5
        rtstep = 0.05
        tdy = TRADING_DAYS_PER_YEAR
        rtrange = np.arange(rt0/tdy, rtn/tdy, rtstep/tdy)
    
        stps = float(len(rtrange))
        count = 1.0
    
        efx = []
        efy = []
        
        p = self.portfolio
    
        for rt in rtrange:
            p.optimize_portfolio(rt=rt, lower_bound_weight=0.0, upper_bound_weight=1.0)
            px = p.port_opt.volatility
            py = p.port_opt.portfolio_return
            efx.append(px)
            efy.append(py)
        
            # reset the optimization
            p.port_opt = None
        
            print(100.0*count/stps),
            count+=1.0
    
        return efx, efy


    def _create_plot_component(self):
    
        x, y = self.get_stock_data()
        efx, efy = self.get_ef_data()

        pd = ArrayPlotData(x=x, y=y, efx=efx, efy=efy)
    
        # Create some plots of the data
        plot = Plot(pd)

        # Create a scatter plot (and keep a handle on it)
        stockplt = plot.plot(("x", "y"), color=(0.0,0.0,0.5,0.25),
                                         type="scatter",
                                         marker="circle")[0]
    
        efplt = plot.plot(("efx", "efy"), color=(0.0,0.5,0.0,0.25),
                                          type="scatter",
                                          marker="circle")[0]
    
    
        for i in range(len(self.symbols)):
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

        # Tweak some of the plot properties
        plot.padding = 50

        # Attach some tools to the plot
        plot.tools.append(PanTool(plot, drag_button="right"))
        plot.overlays.append(ZoomTool(plot))

        return plot


def save_plot(plot, filename, width, height):
    plot.outer_bounds = [width, height]
    plot.do_layout(force=True)
    gc = PlotGraphicsContext((width, height), dpi=72)
    gc.render_component(plot)
    gc.save(filename)


if __name__ == "__main__":

    pm = PortfolioModel()
    print pm.symbols
    print "Plot:", pm, pm.__dict__, pm.plot
    save_plot(pm.plot, "chaco_mpt.png", 800, 800)
    pm.configure_traits()

#### EOF #################################################################


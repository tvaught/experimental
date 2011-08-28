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
from traits.api import HasTraits, Instance, Str
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, Plot, Label, PlotGraphicsContext
from chaco.tools.api import PanTool, ZoomTool, DataLabelTool

# Local imports
from data_point_label import DataPointLabel
import mpt
from metrics import TRADING_DAYS_PER_YEAR

#symbols = ["CSCO", "AAPL", "IBM",  "MSFT", "GE", "WFC", "RIG", "T", "AA", "CAT"]

symbols = ["VQNPX", "NAESX", "VGSIX", "VFSTX", "VGPMX", "VPACX"]
db = "data/indexes.db"

p = mpt.Portfolio(symbols=symbols, dbfilename=db)

def get_stock_data():

    # Assemble and report pre-optimized porfolio data
    x = []
    y = []

    for symbol in p.symbols:
        stk = p.stocks[symbol]
        x.append(stk.annual_volatility)
        y.append(stk.annualized_adjusted_return)
    
    return x, y
    
def get_ef_data():
    
    # Note: The risk tolerance variable seems to be a daily volatility
    #     value.  So to make this more friendly, start with annual
    #     volatility and convert for our calculations.
    rt0 = 0.05
    rtn = 1.5
    rtstep = 0.05
    tdy = TRADING_DAYS_PER_YEAR
    rtrange = np.arange(rt0/tdy, rtn/tdy, rtstep/tdy)
    
    stps = float(len(rtrange))
    count = 1.0
    
    efx = []
    efy = []
    
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


#============================================================================
# # Create the Chaco plot.
#============================================================================
def _create_plot_component():
    
    x, y = get_stock_data()
    efx, efy = get_ef_data()
    
    pd = ArrayPlotData(x=x, y=y, efx=efx, efy=efy)
    
    # Create some plots of the data
    plot = Plot(pd)

    # Create a scatter plot (and keep a handle on it)
    stockplt = plot.plot(("x", "y"), color=(0.0,0.0,0.5,0.25), type="scatter",
                             marker="circle")[0]
    
    efplt = plot.plot(("efx", "efy"), color=(0.0,0.5,0.0,0.25),
                                      type="scatter",
                                      marker="circle")[0]
    
    
    for i in range(len(symbols)):
        label = DataPointLabel(component=plot, data_point=(x[i], y[i]),
                          label_position="bottom right",
                          padding=4,
                          bgcolor="transparent",
                          border_visible=False,
                          text=symbols[i],
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

#============================================================================
# Attributes to use for the plot view.
size = (350, 350)
title = ""

#============================================================================
# # Demo class that is used by the demo.py application.
#============================================================================
class PlotEF(HasTraits):
    plot = Instance(Component)

    traits_view = View(
                    Group(
                        Item('plot', editor=ComponentEditor(size=size),
                             show_label=False),
                        orientation = "vertical"),
                    resizable=True, title=title
                    )

    def _plot_default(self):
         return _create_plot_component()


def save_plot(plot, filename, width, height):
    plot.outer_bounds = [width, height]
    plot.do_layout(force=True)
    gc = PlotGraphicsContext((width, height), dpi=72)
    gc.render_component(plot)
    gc.save(filename)


plt = PlotEF()

if __name__ == "__main__":
    save_plot(plt.plot, "chaco_mpt.png", 800, 800)
    plt.configure_traits()

#### EOF #################################################################


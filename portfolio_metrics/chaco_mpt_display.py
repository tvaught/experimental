#!/usr/bin/env python
# encoding: utf-8
"""
chaco_mpt_display.py

Created by Travis Vaught on 2011-08-23.
Copyright (c) 2011 Vaught Management, LLC.
License: BSD
"""

# Note: disable the following 2 lines if you want to use the wxWidgets GUI backend.
from traits.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"

# Major library imports
import numpy as np

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, Float, List, Str, Button, Property, File
from traitsui.api import Item, Group, View, SetEditor, TabularEditor, ColorTrait
from traitsui.tabular_adapter import TabularAdapter

# Chaco imports
from chaco.api import (ArrayPlotData, Plot, PlotGraphicsContext,
                      ScatterInspectorOverlay, VPlotContainer)
from chaco.tools.api import PanTool, ZoomTool, DataLabelTool, ScatterInspector

# Local imports
from data_point_label import DataPointLabel
from metrics import TRADING_DAYS_PER_YEAR
import mpt
import price_utils
from stock_plot import StockPlot

COLORS = [(0.8, 0.5, 0.3, 0.7),
            (0.8, 0.1, 0.9, 0.7),
            (0.8, 0.8, 0.2, 0.7),
            (0.8, 0.4, 0.5, 0.7),
            (0.5, 0.8, 0.8, 0.7),
            (0.1, 0.8, 0.0, 0.7),
            (0.4, 0.7, 0.8, 0.7),
            (0.0, 0.5, 0.8, 0.7),
            (0.6, 0.5, 0.8, 0.7),
            (0.2, 0.1, 0.8, 0.7),
            (0.8, 0.4, 0.5, 0.7),
            (0.7, 0.0, 0.1, 0.7)]

#db = "data/stocks.db"
db = "data/bonds.db"


# TODO: Get rid of "tolist" requirement .. seems messy
all_symbols = price_utils.load_symbols_from_table(dbfilename=db)['symbol'].tolist()
print all_symbols

# Some other ways to do symbols ...
#init_symbols = ["CSCO", "AAPL", "IBM",  "MSFT", "GE", "WFC", "RIG", "T", "AA", "CAT"]
#init_symbols = ["AAPL", "GOOG", "EOG", "YUM", "AA", "BA", "COP"]
init_symbols = ["FSTYX", "LALDX", "PIMSX", "USSBX", "BSV"]
init_symbols.sort()

def color_tuple_to_int(rgb_tuple):
    # TODO: This is a major hack to return a hex string so that the bg_color for the rows
    # will work properly.
    return "#"+"".join(map(chr, (int(x*255) for x in rgb_tuple))).encode('hex')

class Symbol(HasTraits):
    symbol = Str
    color = ColorTrait
    #methods = Str

    def __repr__(self):
        return "Symbol: %s, Color: %s" % (self.symbol, self.color)



class SymbolListAdapter(TabularAdapter):

    columns = [('Selected Symbols', 'symbol')]
    column_widths = [10]
    font        = 'Arial 10'
    alignment   = 'left'

    Symbol_symbol_bg_color = Property

    def _get_Symbol_symbol_bg_color(self):
        # background colors are specified in actual int (from hex)
        # values, so we have to go through this...
        if isinstance(self.item.color, tuple):
            return color_tuple_to_int(self.item.color[:3])
        else:
            return None

class SymbolPoolAdapter(TabularAdapter):

    columns = [('Symbols', 'symbol')]
    column_widths = [30]
    font        = 'Arial 10'
    alignment   = 'left'


symbols_tabular_editor = TabularEditor(adapter=SymbolListAdapter(),
                                    operations=['move'], drag_move=True)
symbol_pool_tabular_editor = TabularEditor(adapter=SymbolPoolAdapter(),
                                    operations=['move'], drag_move=True,
                                    )

class PortfolioModel(HasTraits):


    symbols = List(init_symbols)
    # Test this for now...
    symbols2 = List(Instance(Symbol))
    symbol_pool = List(Instance(Symbol))

    # Arbitrary date range for pulling asset data
    startdate = Str("2000-01-1")
    enddate = Str("2012-03-23")

    dbfilename = File("data/stocks.db")
    portfolio = Instance(mpt.Portfolio)
    plot = Instance(Component)

    recalc_button = Button(label='Recalculate')
    save_plot_button = Button(label='Save Plot')

    symbol_pool_item = Item('symbol_pool', editor=symbol_pool_tabular_editor,
                                 width=20, resizable=True)

    symbols_item = Item('symbols', style="simple", resizable=True,
                        editor=SetEditor(values=all_symbols,
                        can_move_all=True,
                        left_column_title='Symbols',
                        right_column_title='Selected Symbols'),
                        width=0.1)

    model_portfolio_x = Float(0.0241)
    model_portfolio_y = Float(0.051)
    
    traits_view = View(
                    Group(
                        Group(
                            Item('dbfilename',
                                 label='Database File',
                                 width=-20),
                            Item('startdate',
                                 label='Start Date',
                                 width=-20),
                            Item('enddate',
                                 label='End Date',
                                 width=-20),
                            Item('model_portfolio_x',
                                 label='Model Portfolio Volatility',
                                 style='simple'),
                            Item('model_portfolio_y',
                                 label='Model Portfolio Return',
                                 style='simple'),
                            Item('recalc_button', show_label=False,
                                 width=-20),
                            Item('save_plot_button', show_label=False,
                                 width=-20),
                            symbols_item,
                            #symbol_pool_item,
                            Item('symbols2', editor=symbols_tabular_editor,
                                 height=0.2, springy=True),
                            orientation="vertical",
                            springy=True,
                            id='leftpane'),
                        Group(
                            Item('plot',
                                editor=ComponentEditor(size=(400,400)),
                                show_label=False),
                            orientation="vertical",
                            show_labels=False
                            ),
                        orientation="horizontal",
                        show_labels=False),
                    resizable=True,
                    title="Markowitz Mean-Variance View (MPT)",
                    width=0.9,
                    height=0.9)

    def __init__(self, *args, **kw):
        self.symbols.sort()
        super(PortfolioModel, self).__init__(*args, **kw)
        symbol_list = price_utils.load_symbols_from_table(dbfilename=self.dbfilename)['symbol'].tolist()
        self.symbol_pool = [Symbol(symbol=symb) for symb in symbol_list]
        #self.symbols2 = [Symbol(symbol=s) for s in init_symbols]
        self.plot = self._create_plot_component()

    # #############################
    # Methods triggered by trait events
    # #############################
    def _recalc_button_fired(self, event):
        self.symbols.sort()
        self.plot = self._create_plot_component(recalc=True)
        #self.plot.invalidate_draw()
        self.plot.request_redraw()

    def _save_plot_button_fired(self, event):
        save_plot(pm.plot, "chaco_ef.png", 400,300)

    def _dbfilename_changed(self, event):
        #reload symbols
        # TODO: what's the right way to do this?
        symbol_list = price_utils.load_symbols_from_table(dbfilename=self.dbfilename)['symbol'].tolist()
        #print self.dbfilename, symbol_list
        if len(symbol_list) > 2:
            #print "New symbols: ", symbol_list
            self.trait_view('symbols_item').editor.values = symbol_list
            #print "Symbol list setting: ", self.trait_view('symbols_item').editor.values

            self.trait_view('traits_view').updated = True

            self.symbols = symbol_list[:2]
            #self.trait_view( 'symbols' ).updated = True
        return


    def _symbols_changed(self, event):
        self.symbols2 = [Symbol(symbol=s) for s in self.symbols]

    def _plot_default(self):
        return self._create_plot_component()
    
    def get_stock_data(self):
        
        self.portfolio = p = mpt.Portfolio(symbols=self.symbols,
                                 startdate=self.startdate, enddate=self.enddate,
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
        rt0 = 0.02
        rtn = 1.0
        rtstep = 0.02
        tdy = TRADING_DAYS_PER_YEAR
        rtrange = np.arange(rt0/tdy, rtn/tdy, rtstep/tdy)

        efx = []
        efy = []
        allocations = {}
        
        p = self.portfolio
    
        for rt in rtrange:
            p.optimize_portfolio(rt=rt, lower_bound_weight=0.1, upper_bound_weight=1.0)
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

        pd = ArrayPlotData(x=x, y=y, efx=efx, efy=efy, mp_x=[self.model_portfolio_x], mp_y=[self.model_portfolio_y])

        # Create some plots of the data
        plot = Plot(pd, title="Efficient Frontier")

        # Create a scatter plot (and keep a handle on it)
        stockplt = plot.plot(("x", "y"), color="transparent",
                                         type="scatter",
                                         marker="dot",
                                         marker_line_color="transparent",
                                         marker_color="transparent",
                                         marker_size=1)[0]

        efplt = plot.plot(("efx", "efy"), color=(0.0,0.5,0.0,0.25),
                                          type="scatter",
                                          marker="circle",
                                          marker_size=6)[0]
        efpltline = plot.plot(("efx", "efy"), color=(0.1,0.4,0.1,0.7),
                                          type="line")[0]


        # Create another one-point scatter for a model portfolio
        mp_plot = plot.plot(("mp_x", "mp_y"), color=(1.0, 0.5, 0.5, 0.25),
            type="scatter",
            market="triangle",
            market_size=7)[0]

        for i in range(len(p.stocks)):
            label = DataPointLabel(component=plot, data_point=(x[i], y[i]),
                              label_position="bottom right",
                              padding=4,
                              bgcolor="transparent",
                              border_visible=False,
                              text=self.symbols[i],
                              marker="circle",
                              marker_color=(0.0,0.0,0.5,0.25),
                              marker_line_color="lightgray",
                              marker_size=6,
                              arrow_size=8.0,
                              arrow_min_length=7.0,
                              font_size=14)

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
        stockplt.value_range.low=0.0
        stockplt.value_range.high=0.1
        stockplt.index_range.low=0.0
        stockplt.index_range.high=0.1
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

        symbs = a[rts[0]].keys()
        symbs.sort()

        # "Transpose" symbols' weights to get vectors of weights for each symbol
        symb_data = np.array([[a[rt][symb] for rt in rts] for symb in symbs])

        self.symbols2 = [Symbol(symbol=symbs[i], color=COLORS[i]) for i in range(len(symbs))]

        # Create a plot data object and give it this data
        bpd = ArrayPlotData()
        bpd.set_data("index", rts)
        bpd.set_data("allocations", symb_data)

        # Create a contour polygon plot of the data
        bplot = Plot(bpd, title="Allocations")
        bplot.stacked_bar_plot(("index", "allocations"),
                        color = COLORS,
                        outline_color = "gray")

        bplot.padding = 50
        #bplot.legend.visible = True

        # Add a plot of the stocks
        stock_obj_list = [p.stocks[symb] for symb in symbs]
        
        #for itm in stock_obj_list:
            #itm.print_traits()
            #print "Has Cache?:", itm.stock_data_cache is not None

        splot = StockPlot(stocks=[p.stocks[symb] for symb in symbs], colors=COLORS).plot

        container.add(bplot)
        container.add(plot)
        container.add(splot)
        
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


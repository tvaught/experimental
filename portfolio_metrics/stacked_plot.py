""" Plot renderer for stacked bar/area plots.
"""

from numpy import array, column_stack, compress

# Enthought library imports
from enthought.traits.api import (Array, Float,
                                  List, Property, Str)
from enthought.chaco.api import (BaseXYPlot)
from enthought.enable.api import ColorTrait, LineStyle




class StackedRenderer(BaseXYPlot):

    index_name = Str('date')
    value_names = List(Str)

    # Accept any recarray as data
    data = Array

    index = Property
    value = Property

    # Traits for setting appearance.
    # The line style {"dot", "dash", "solid", others?}
    line_style = LineStyle

    # Outline thickness.  Use 0 for no outline
    line_width = Float(1.0)

    # Outline color
    line_color = ColorTrait("black")

    def _gather_points(self):
        """
        Gathers up the data points that are within our bounds and stores them
        """
        if self._cache_valid:
            return
        if not self.index:
            return

        values = []

        idx = self.data[self.index_name].get_data()
        index_mask = self.index_range.mask_data(idx)
        
        for itm in self.data.dtype.names:
            values.append(self.data[itm][index_mask])

        print idx, values

        value_lengths = array(map(len, values))

        if len(idx) == 0 or any(value_lengths == 0) or any(len(idx) != value_lengths):
            print "Chaco: using empty dataset; index_len=%d, value_lengths=%s." \
                                % (len(idx), str(value_lengths))
            self._cached_data_pts = []
            self._cache_valid = True
            return

        points = column_stack([idx,] + values)

        for ds in [self.open, self.high, self.low, self.close, self.average]:
            value, tmp_value_mask = ds.get_data_mask()
            values.append(value)
            if value_mask is None:
                value_mask = tmp_value_mask
            else:
                value_mask &= tmp_value_mask

        # Broaden the range masks by 1
        #index_range_mask = broaden(self.index_mapper.range.mask_data(index))
        #value_range_mask = broaden(self.value_mapper.range.mask_data(points, high_ndx=2, low_ndx=3))
        index_range_mask = self.index_mapper.range.mask_data(idx)
        value_range_mask = self.value_mapper.range.mask_data(points, high_ndx=2, low_ndx=3)
        nan_mask = invert(isnan(index_mask)) & invert(isnan(value_mask))
        point_mask = index_mask & value_mask & nan_mask & \
                     index_range_mask & value_range_mask

        self._cached_data_pts = compress(point_mask, points, axis=0)

        self._cache_valid = True
        return

    def _draw_component(self, gc, view_bounds=None, mode="normal"):
        # Gather the points within the view range into self._cached_data_pts

        #self._gather_points()
        self._gather_points()
        if self._cached_data_pts.size == 0:
            # No data.
            return

        names = self.data.dtype.names
        pts = zip(names, self._cached_data_pts.transpose())
        for pt in pts:
            setattr(self, *pt)

        # Map data points into screen space
        values = [self.index_mapper.map_screen(getattr(self, self.index_name))]

        for itm in names:
            if itm != self.index_name:
                values.append(self.value_mapper.map_screen(getattr(self,itm)))

        # Render the screen space points
        gc.save_state()
        gc.set_antialias(False)
        gc.clip_to_rect(self.x, self.y, self.width, self.height)
        self._render(gc, values)
        gc.restore_state()

    def _get_index(self):
        return self.data[self.index_name]

    def _set_index(self, new_index):
        self.index = new_index

    def _get_value(self):
        return self.data[self.value_name]

    def _set_value(self, new_value):
        self.value = new_value

# EOF ####################################################################
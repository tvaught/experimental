#!/usr/bin/env python
# encoding: utf-8
"""
data_point_label.py

Created by Travis Vaught on 2011-08-25.
Copyright (c) 2011 Vaught Management, LLC.
License: BSD

Extends the DataLabel class to simply accept a text string (more general).
"""

# Major library imports
from chaco.api import DataLabel
from traits.api import Str, on_trait_change

class DataPointLabel(DataLabel):
    
    text = Str("Label")
    
    def _create_new_labels(self):
        pt = self.data_point
        if pt is not None:
            self.lines = [self.text]

    def _text_changed(self, old, new):
       self._create_new_labels()
    @on_trait_change("text,label_position,position,position_items,bounds,bounds_items")
    def _invalidate_layout(self):
        self._layout_needed = True
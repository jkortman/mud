'''
Utility classes to mark vector features.
Each class takes an Event and generates a subvector, which are then concatenated by a vector builder.
'''

import numpy as np
from .binary_vector import binvec

class Feature(object):
    def dim(self):
        return 0

    def make_subvector(self, event):
        return np.zeros(0)

class IsNote(Feature):
    def __init__(self):
        pass

    def dim(self):
        return 1

    def make_subvector(self, event):
        if event.is_note():
            np.zeros(1)
        else:
            np.zeros(0)

class NotePitch(Feature):
    def __init__(self, pitch_labels):
        '''
        Create a note pitch feature.
        'labels' should be a dict that maps pitch strings (without octaves) to labels.
        (labels are integers)
        see: mud.fmt.make_pitch_labels
        '''
        self._pitch_labels = pitch_labels
        self._dim = pitch_labels.num_labels

    def dim(self):
        return self._dim

    def make_subvector(self, event):
        label = self._pitch_labels.get_label_of(event.pitch())
        return binvec(self._dim, label)

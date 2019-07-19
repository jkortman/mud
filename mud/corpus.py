'''
Module containing the Corpus class, which provides methods for loading an entire corpus of Pieces.
'''

from glob import iglob
import random
import pickle
import music21 as mu
from typing import Optional, Iterable

from .piece import Piece
from .fmt.piece_data import PieceData
from . import piece_filter

class AbstractCorpus(object):
    # Common code for save/loading of corpuses.
    def __init__(self):
        raise NotImplementedError

    def save(self, fname):   
        with open(fname, 'wb+') as f:
            pickle.dump(self.__dict__,
                        f,
                        pickle.HIGHEST_PROTOCOL)

    def load(self, fname):
        with open(fname, 'rb') as f:
            self.__dict__ = pickle.load(f)

class Corpus(AbstractCorpus):
    '''
    A Corpus contains a collection of different mud.Piece objects.
    '''
    def __init__(
            self,
            patterns:           Iterable[str] = [],
            filters:            Iterable[str] = [],
            from_file:          Optional[str] = None,
            discard_rests:      bool = False,
            max_len:            Optional[int] = None,
            ignore_load_errors: bool = False,
            verbose:            bool = False,
            transpose_to:       Optional[str] = None):
        '''
        Load a corpus of pieces.
        
        Args:
            `patterns`: an iterable of globbable patterns (ie '*.musicxml'). Files which match the
                patterns will be loaded into the corpus. (Default: [])
            `filters`: an iterable of functions. Each function should take the form
                `f(mud.Piece) -> bool`. Only pieces which pass all filter functions will be kept.
                Useful filters are found in the `mud.piece_filter` module. (Default: [])
            `from_file`: This is a path to a pickled Corpus that will be loaded.
                If used, other information provided to load pieces will be *ignored*. (Optional)
            `discard_rests`: If True, the Rest notation events will be discarded in every piece.
                (Default: False)
            `max_len`: Stop loading when this many pieces have been successfully loaded. (Optional)
            `ignore_load_errors`: If True, ignore any load errors. Depending on the data being
                loaded, Music21 may not load pieces successfully, and this may be required.
                (Default: False)
            `verbose`: Show verbose output about the piece-loading process. (Default: False)
            `transpose_to`: If provided, transpose all pieces to this key. (Optional)

        Returns:
            A corpus containing the requested pieces.
        '''
        self._pieces = []
        self._num_rejected = 0

        if from_file is not None:
            if len(patterns) > 1:
                raise ValueError('Should not provide patterns if loading from file')
            self.load(from_file)
        else:
            def load(self_):
                for pattern in patterns:
                    for fname in iglob(pattern):
                        try:
                            res, why = self_.load_piece(fname, filters, transpose_to)
                        except (mu.exceptions21.StreamException,
                                mu.musicxml.xmlToM21.MusicXMLImportException):
                            if verbose: print(f'    Failed to load file {fname}: ', end='')
                            if ignore_load_errors:
                                if verbose: print('continuing')
                                continue
                            if verbose: print('failing (use `ignore_load_errors=True` in corpus '
                                              'to prevent)')
                            raise
                        if verbose:
                            if res:
                                print(f'    loaded: {fname}')
                            else:
                                print(f'    rejected: {fname}, {why}')
                        if max_len is not None and self_.size() >= max_len:
                            return
            load(self)
            
        if discard_rests:
            self.discard_rests()

    def size(self):
        return len(self._pieces)

    @property
    def pieces(self):
        return self._pieces

    @property
    def num_rejected(self):
        return self._num_rejected

    def passes_filters(self, piece, filters):
        for f in filters:
            if not f(piece):
                self._num_rejected += 1
                return False, piece_filter.failure_reason(f)
        return True, "Passes"

    def load_piece(self, piece, filters=tuple(), transpose_to=None):
        p = Piece(piece, transpose_to)
        passes, reason = self.passes_filters(p, filters)
        if passes:
            p = self._pieces.append(p)
            return True, "Success"
        return False, reason

    def format_data(self, formatter, slice_resolution, discard_rests=False):
        return DataCorpus(self, formatter, slice_resolution, discard_rests)

    def filter(self, *filters):
        '''
        Filter out pieces that do not adhere to a set of filters.
        see: piece_filter.py
        '''
        len_old = len(self._pieces)
        for f in filters:
            self._pieces = [p for p in self._pieces if f(p)]
        self._num_rejected += len_old - len(self._pieces)

    def discard_rests(self):
        for piece in self._pieces:
            piece.discard_rests()

class DataCorpus(AbstractCorpus):
    '''
    A DataCorpus contains only ""data"" of a collection of pieces, intended for use as inputs and
    targets for a machine learning model. See the `mud.fmt.PieceData` class for more info.
    '''
    def __init__(
            self,
            corpus:           Corpus,
            formatter:        EventDataBuilder,
            slice_resolution: float,
            discard_rests:    bool = False):
        self._data = [PieceData(p, formatter, slice_resolution, discard_rests)
                      for p in corpus.pieces]

    def size(self):
        return len(self._data)

    @property
    def data(self):
        return self._data

    def __iter__(self):
        return self._data.__iter__()
    
    def __len__(self):
        return len(self._data)



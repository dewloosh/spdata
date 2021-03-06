# -*- coding: utf-8 -*-
from spdata.utils import count_cols
import numpy as np
from numpy import concatenate as join
import awkward as ak
from awkward import unflatten as build
import numpy as np
#from operator import add
#from functools import reduce


def shape(arr): return arr.shape[:2]
def cut(shp): return np.full(shp[0], shp[1], dtype=np.int64)
def flatten(arr): return arr.flatten()


class JaggedArray(ak.Array):
    """Currently it only supports 2 dimensional arrays."""

    def __init__(self, data, behavior=None, with_name=None,
                 check_valid=False, cache=None, kernels=None,
                 cuts=None):
        if isinstance(data, np.ndarray):
            nD = len(data.shape)
            assert nD <= 2, "Only 2 dimensional arrays are supported!"
            if nD == 1:
                assert isinstance(cuts, np.ndarray)
                data = build(data, cuts)
        elif isinstance(data, list):
            assert all(map(lambda arr: len(arr.shape) == 2, data)), \
                "Only 2 dimensional arrays are supported!"
            # NOTE - implementaion 1
            # > Through the back door, but this is probably the cleanest solution of all.
            # > It only requires to create one python list, without further operations on it.
            # NOTE This line is one of the most unreadable things I've ever done.
            data = build(join(list(map(flatten, data))), join(list(map(cut, map(shape, data)))))
            # NOTE - implementaion 2
            # > This also works, but requires data to jump back and forth just to
            # > have a merged list of lists. It also requires to add nested python lists,
            # > which is probably not the quickest operation in the computational world.
            #data = ak.from_iter(reduce(add, map(lambda arr : ak.Array(arr).to_list(), data)))
            # NOTE - implementaion 3
            # > This also works at creation, but fails later at some operation due to
            # > the specific layout generated by ak.concatenate
            #data = ak.concatenate(list(map(lambda arr : ak.Array(arr), data)))
        super().__init__(data, behavior=behavior, with_name=with_name,
                         check_valid=check_valid, cache=cache, kernels=kernels)

    def is_jagged(self):
        widths = self.widths()
        return not np.all(widths == widths[0])

    def widths(self):
        assert self.ndim == 2, "Only 2 dimensional arrays are supported!"
        return count_cols(self)

    def flatten(self, return_cuts=False):
        if return_cuts:
            return self.widths(), ak.flatten(self)
        else:
            return ak.flatten(self)

    def __array_function__(self, func, types, args, kwargs):
        if func == np.unique:
            return unique2d(*args, **kwargs)
        return super().__array_function__(func, types, args, kwargs)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        return super().__array_ufunc__(ufunc, method, *inputs, **kwargs)

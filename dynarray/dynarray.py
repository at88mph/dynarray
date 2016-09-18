import numpy as np


class DynamicArray(object):

    MAGIC_METHODS = ('__radd__',
                     '__add__',
                     '__sub__',
                     '__rsub__',
                     '__mul__',
                     '__rmul__',
                     '__div__',
                     '__rdiv__',
                     '__pow__',
                     '__rpow__',
                     '__eq__')

    class __metaclass__(type):
        def __init__(cls, name, parents, attrs):

            def make_delegate(name):

                def delegate(self, *args, **kwargs):
                    return getattr(self._data[:self._size], name)

                return delegate

            type.__init__(cls, name, parents, attrs)

            for method_name in cls.MAGIC_METHODS:
                setattr(cls, method_name, property(make_delegate(method_name)))

    def __init__(self, array_or_shape, dtype=None, capacity=10):

        if isinstance(array_or_shape, tuple):
            self._shape = array_or_shape
            self._dtype = dtype
            self._size = 0
            self._capacity = capacity
        elif isinstance(array_or_shape, np.ndarray):
            self._shape = array_or_shape.shape[1:]
            self._dtype = array_or_shape.dtype
            self._size = array_or_shape.shape[0]
            self._capacity = max(self._size, capacity)

        self._data = np.empty((self._capacity,) + self._shape,
                              dtype=self._dtype)

        if isinstance(array_or_shape, np.ndarray):
            self[:] = array_or_shape

    def __getitem__(self, idx):

        return self._data[:self._size][idx]

    def __setitem__(self, idx, value):

        self._data[:self._size][idx] = value

    def _grow(self, new_size):

        self._capacity = new_size
        self._data = np.resize(self._data, ((self._capacity,) + self._shape))

    def _as_dtype(self, value):

        if hasattr(value, 'dtype') and value.dtype == self._dtype:
            return value
        else:
            return np.array(value).astype(self._dtype)

    def append(self, value):

        value = self._as_dtype(value)

        if value.shape != self._shape:

            value_unit_shaped = value.shape == (1,) or len(value.shape) == 0
            self_unit_shaped = self._shape == (1,) or len(self.shape) == 0

            if value_unit_shaped and self_unit_shaped:
                pass
            else:
                raise ValueError('Input shape {} incompatible with '
                                 'array shape {}'.format(value.shape,
                                                         self._shape))

        if self._size == self._capacity:
            self._grow(self._capacity * 2)

        self._data[self._size] = value

        self._size += 1

    def extend(self, values):

        values = self._as_dtype(values)

        required_size = self._size + values.shape[0]

        if required_size >= self._capacity:
            self._grow(max(self._capacity * 2,
                           required_size))

        self._data[self._size:required_size] = values
        self._size = required_size

    def shrink_to_fit(self):

        self._grow(self._size)

    def __repr__(self):

        return (self._data[:self._size].__repr__()
                .replace('array',
                         'DynamicArray(size={}, capacity={})'
                         .format(self._size, self._capacity)))

import numpy
from gtrackcore.util.CommonConstants import BINARY_MISSING_VAL


def insert_into_array_of_larger_shape(array, shape):
    new_array = numpy.empty(shape=shape, dtype=array.dtype)
    new_array.fill(get_default_numpy_value(array.dtype))
    new_array[[slice(0, shape_dimension) for shape_dimension in array.shape]] = array
    return new_array


def get_default_numpy_value(dtype):
    dtype = numpy.dtype(dtype)  # ensure numpy.dtype object
    if dtype.kind == 'i':
        return BINARY_MISSING_VAL
    elif dtype.kind == 'f':
        return numpy.nan
    elif dtype.kind == 'S':
        return ''
    elif dtype.kind == 'b':
        return False

    raise ValueError('%s is not a valid data type' % str(dtype))

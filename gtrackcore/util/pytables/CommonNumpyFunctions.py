import numpy


def insert_into_array_of_larger_shape(array, shape):
    new_array = numpy.zeros(shape=shape, dtype=array.dtype)  # TODO: + gtrackcore default value for dtype
    new_array[[slice(0, shape_dimension) for shape_dimension in array.shape]] = array
    return new_array


import numpy as np

def averageLinkWeight(weights, customAverageFunction=None):
    """
    Find the average of a tracks edge weights. This make the most sense
    when the weight is a number, but we try to give a result for the other
    types. One can use the customAverageFunction if one needs some other
    type of average calculation.

    A weight has a dimension and a type. The supported dimensions and types
    are listed below.

    - Edge weight type
      one of:
        number
        binary
        character
        category

        Default value: number

    - Edge weight dimension
      one of:
        scalar
        pair
        vector
        list

        Default value: scalar

    :param weights: Numpy array. A tracks link weights
    :param customAverageFunction: Overloads the average function.
    :return: The average of the weights.
    """

    assert weights is not None
    assert len(weights) > 0

    first = weights[0]
    if isinstance(first, np.ndarray) or isinstance(first, list):
        # List type
        # Check
        #lengths = [len(x) for x in weights]
        #equalLengths = len(set(lengths)) <= 1

        if customAverageFunction is not None:
            # When using a custom function we assume that the user knows what
            # type the weights have.
            avgPerWeight = np.array([customAverageFunction(x) for x in weights])
            return customAverageFunction(avgPerWeight)
        # The calculations is equal for list, pairs and vectors.
        elif isinstance(first[0], (bool, np.bool_)):
            # Average of a boolean.. Return the all(weight) for now.
            avgPerWeight = np.array([all(x) for x in weights])
            return all(avgPerWeight)
        elif isinstance(first[0], (int, long, float)):
            # Number
            avgPerWeight = np.array([np.nanmean(x) for x in weights])
            return np.nanmean(avgPerWeight)
        else:
            # character or category
            raise NotImplementedError
    else:
        # Scalar
        if customAverageFunction is not None:
            # When using a custom function we assume that the user knows what
            # type the weights have.
            return customAverageFunction(weights)

        elif isinstance(first, (bool, np.bool_)):
            # Average of a boolean.. Return the all(weight) for now.
            return all(weights)
        elif isinstance(first, (int, long, float)):
            # Numbers
            return np.nanmean(weights)
        else:
            # char or string
            raise NotImplementedError

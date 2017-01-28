import numpy as np

def someOperation(starts, ends, someOption=None, someOtherOption=False,
                  debug=False):

    # Each raw operations should be as simple as possible.
    # We take numpy arrays as inputs, do some calculation on them,
    # andre return either the arrays that constitutes a new track
    # or some type calculated value.

    if debug:
        # Debug printing is often useful.
        print("Start of someOperation")
        print("t1Starts: {}".format(starts))

    if someOtherOption:
        # If a option is given we may want to change some of the
        # arrays or may provide different calculation
        starts = starts + 1

    # Tracks may have additional data columns, as these are
    # not necessary here we need to extract them later.
    # To make this possible we need to create a index array that
    # tells us where in the original array the elements are.
    index = np.arange(0, len(starts), 1, dtype='int32')

    # If the operation uses more then on track, we do also
    # need to know which track to get the value from.
    # As we have only one track here, we do not need it.
    encoding = np.zeros(len(starts), dtype='int32') + 1

    # In this simple example we find all elements that
    # have a start bigger then 1000, and a end smaller then
    # 2000.
    # The np.where method is very powerful one and can
    # be used in many situations
    selectIndex = np.where((starts > 1000) | (ends < 2000))

    # We then use the index to select the data for our new track.

    starts = starts[selectIndex]
    ends = ends[selectIndex]
    index = index[selectIndex]

    # The return value is always ndarrays. Its the
    # responsibility of the class operator to create the
    # new TrackView
    return starts, ends, index

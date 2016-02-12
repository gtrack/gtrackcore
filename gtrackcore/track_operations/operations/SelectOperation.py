__author__ = 'skh'

from gtrackcore.track_operations.exeptions.Operations import OutputTrackTypeNotSupportedError


# Example of a select tree for a operations supporting all track types.
req = self._RESULT_TRACK_REQUIREMENTS
if req.isDense():
    # GP, SP, F, LGP, LSF, LF, LBS
    if req.isValued():
       # SF, F, LSF, LF
       if req.isInterval():
           # SF, LSF
           if req.isLinked():
               # LSF
               raise OutputTrackTypeNotSupportedError(
                   "Linked Step Function", "Union")
           else:
               # SF
               raise OutputTrackTypeNotSupportedError(
                   "Step Function", "Union")
       else:
           # F, LF
           if req.isLinked():
               # LF
               raise OutputTrackTypeNotSupportedError(
                   "Linked Function", "Union")
           else:
               # F
               raise OutputTrackTypeNotSupportedError(
                   "Function", "Union")
    else:
        # GP, LGP, LBP
        if req.isInterval():
            # GP LGP,
            if req.isLinked():
                # LGP
                raise OutputTrackTypeNotSupportedError(
                    "Linked Genome Partition", "Union")
            else:
                # GP
                raise OutputTrackTypeNotSupportedError(
                    "Genome Partition", "Union")
        else:
            # LBP
            raise OutputTrackTypeNotSupportedError(
                "Linked Base Pair", "Union")
else:
    # P, VP, S, VS, LP, LVP, LS, LVS
    if req.isValued():
        # VP, VS LVP LVS
        if req.isInterval():
            # VS, LVS
            if req.isLinked():
                # LVS
                raise OutputTrackTypeNotSupportedError(
                    "Linked Valued Segments", "Union")
            else:
                # VS
                raise OutputTrackTypeNotSupportedError(
                    "Valued Segments", "Union")
        else:
            # VP, LVP
            if req.isLinked():
                # VP
                raise OutputTrackTypeNotSupportedError(
                    "Valued Points", "Union")
            else:
                # LVP
                raise OutputTrackTypeNotSupportedError(
                    "Linked Valued Points", "Union")
    else:
        # P, S, LP, LS
        if req.isInterval():
            # S, LS
            if req.isLinked():
                # LS
                raise OutputTrackTypeNotSupportedError(
                    "Linked Segments", "Union")
            else:
                # Segment
                raise OutputTrackTypeNotSupportedError(
                    "Segments", "Union")
        else:
            # P, LP
            if req.isLinked():
                # Linked Points
                raise OutputTrackTypeNotSupportedError(
                    "Linked Points", "Union")
            else:
                # Points
                raise OutputTrackTypeNotSupportedError(
                    "Points", "Union")

class Warning(Exception):
    pass

class InvalidFormatWarning(Warning):
    pass

class InvalidFormatError(Exception):
    pass

class IncompatibleTracksError(Exception):
    pass

class AbstractClassError(Exception):
    pass
#
#class SplittableStatNotAvailableError(Exception):
#    pass
#
class NotSupportedError(Exception):
    pass

class ShouldNotOccurError(Exception):
    pass

#class NotValidGESequence(Exception):
#    pass
#
class EmptyGESourceError(Exception):
    pass

class InvalidRunSpecException(Exception):
    pass

#class CentromerError(Exception):
#    pass
#
#class TooLargeBinError(Exception):
#    pass

#class TooSmallBinError(Exception):
#    pass
#
#class IncompatibleAssumptionsError(Exception):
#    pass
#
#class NoneResultError(Exception):
#    pass
#    
#class FileLockError(Exception):
#    pass
#
#class NoMoreUniqueValsError(Exception):
#    pass
#
class ArgumentValueError(Exception):
    pass
#
#class MissingEntryError(Exception):
#    pass
#
#class ExecuteError(Exception):
#    pass
#
#class SilentError(Exception):
#    pass
#
#class IdenticalTrackNamesError(Exception):
#    pass
#    
class NotIteratedYetError(Exception):
    pass
    
class OutsideBoundingRegionError(Exception):
    pass
    
class BoundingRegionsNotAvailableError(Exception):
    pass

class DBNotOpenError(Exception):
    pass

import os
#import sys
import functools
import re
import urllib
#import contextlib
#import traceback
#import numpy
import operator
from collections import Iterable
#
#from config.Config import STATIC_PATH, GALAXY_BASE_DIR, URL_PREFIX
#from third_party.decorator import decorator
#
#from config.Config import PROCESSED_DATA_PATH, DEFAULT_GENOME, \
#    ORIG_DATA_PATH, OUTPUT_PRECISION, MEMOIZED_DATA_PATH, NONSTANDARD_DATA_PATH, \
#    PARSING_ERROR_DATA_PATH, IS_EXPERIMENTAL_INSTALLATION
from gtrackcore.core.Config import Config
#from gtrackcore.util.CustomExceptions import InvalidFormatError
from gtrackcore.util.CommonConstants import BINARY_MISSING_VAL
#from gtrackcore.application.SignatureDevianceLogging import takes,returns
#from third_party.decorator import decorator
#
def createPath(fn):
    "Assumes that fn consists of a basepath (folder) and a filename, and ensures that the folder exists."
    path = os.path.split(fn)[0]
    
    if not os.path.exists(path):
        #oldMask = os.umask(0002)
        os.makedirs(path)
        #os.umask(oldMask)
#        
#def reloadModules():
#    for module in [val for key,val in sys.modules.iteritems() \
#                   if key.startswith('gold') or key.startswith('quick') or key.startswith('test')]:
#        try:
#            reload(module)
#        except:
#            print module
#            
#def wrapClass(origClass, keywords={}):
#    #for key in keywords.keys():
#    #    if re.match('^[0-9]+$',keywords[key]) is not None:
#    #        keywords[key] = int(keywords[key])
#    #    elif re.match('^[0-9]?[.][0-9]?$',keywords[key]) is not None and keywords[key] != '.':
#    #        keywords[key] = float(keywords[key])
#           
#    args = []
#    wrapped = functools.partial(origClass, *args, **keywords)
#    functools.update_wrapper(wrapped, origClass)
#    return wrapped
#
def extractIdFromGalaxyFn(fn):
    pathParts = fn.split(os.sep)
    assert(len(pathParts) >= 2), pathParts
    
    if fn.endswith('.dat'):
        id1 = pathParts[-2]
        id2 = re.sub('[^0-9]', '', pathParts[-1])
        id = [id1, id2]
    else:
        for i in range(len(pathParts)-2, 0, -1):
            if not pathParts[i].isdigit():
                id = pathParts[i+1:-1]
                assert len(id) >= 2, 'Could not extract id from galaxy filename: ' + fn
                break
    
    return id
#
#def getUniqueRunSpecificId(id=[]):
#    return ['run_specific'] + id
#
#def getUniqueWebPath(id=[]):
#    return os.sep.join([STATIC_PATH] + getUniqueRunSpecificId(id))
# 
#def getLoadToGalaxyHistoryURL(fn, genome='hg18', galaxyDataType=None):
#    import base64
#    
#    return URL_PREFIX + '/tool_runner?tool_id=file_import&dbkey=%s&runtool_btn=yes&input=' % genome\
#            + base64.urlsafe_b64encode(fn) + ('&datatype='+galaxyDataType if galaxyDataType is not None else '')
#
#def getRelativeUrlFromWebPath(webPath):
#    return URL_PREFIX + webPath[len(GALAXY_BASE_DIR):]
#
#def isFlatList(list):
#    for l in list:
#        if type(l) == type([]):
#            return False
#    return True    
#    
#def flattenList(list):
#    "recursively flattens a nested list (does not handle dicts and sets..)"
#    if isFlatList(list):
#        return list
#    else:
#        return flattenList( reduce(lambda x,y: x+y, list ) )
#
def listStartsWith(a, b):
    return len(a) > len(b) and a[:len(b)] == b

def isNan(a):
    import numpy
    
    try:
        return numpy.isnan(a)
    except (TypeError, NotImplementedError):
        return False
        
def isListType(x):
    import numpy
    return type(x) == list or type(x) == tuple or isinstance(x, numpy.ndarray) or isinstance(x, dict)

def ifDictConvertToList(d):
    return [(x, d[x]) for x in sorted(d.keys())] if isinstance(d, dict) else d

def smartRecursiveAssertList(x, y, assertEqualFunc, assertAlmostEqualFunc):
    import numpy
    
    if isListType(x):
        if isinstance(x, numpy.ndarray):
            try:
                if not assertEqualFunc(x.shape, y.shape):
                    return False
            except Exception, e:
                raise AssertionError(str(e) + ' on shape of lists: ' + str(x) + ' and ' + str(y))
                
            try:
                if not assertEqualFunc(x.dtype, y.dtype):
                    return False
            except Exception, e:
                raise AssertionError(str(e) + ' on datatypes of lists: ' + str(x) + ' and ' + str(y))
        else:
            try:
                if not assertEqualFunc(len(x), len(y)):
                    return False
            except Exception, e:
                raise AssertionError(str(e) + ' on length of lists: ' + str(x) + ' and ' + str(y))

        for el1,el2 in zip(*[ifDictConvertToList(x) for x in [x, y]]):
            if not smartRecursiveAssertList(el1, el2, assertEqualFunc, assertAlmostEqualFunc):
                return False
        return True
            
    else:
        try:
            return assertAlmostEqualFunc(x, y)
        except TypeError:
            return assertEqualFunc(x, y)

def bothIsNan(a, b):
    import numpy
    
    try:
        if not any(isListType(x) for x in [a,b]):
            return numpy.isnan(a) and numpy.isnan(b)
    except (TypeError, NotImplementedError):
        pass
    return False
    
def smartEquals(a, b):
    if bothIsNan(a, b):
        return True
    return a == b
        
def smartRecursiveEquals(a, b):
    return smartRecursiveAssertList(a, b, smartEquals, smartEquals)
        
def reorderTrackNameListFromTopDownToBottomUp(trackNameSource):
    prevTns = []
    source = trackNameSource.__iter__()
    trackName = source.next()
    
    try:
        while True:
            if len(prevTns) == 0 or listStartsWith(trackName, prevTns[0]):
                prevTns.insert(0, trackName)
                trackName = source.next()
                continue
            yield prevTns.pop(0)
    
    except StopIteration:
        while len(prevTns) > 0:
            yield prevTns.pop(0)
#
#R_ALREADY_SILENCED = False
#def silenceRWarnings():
#    global R_ALREADY_SILENCED
#    if not R_ALREADY_SILENCED:
#        from gtrackcore.application.RSetup import r
#        r('sink(file("/dev/null", open="wt"), type="message")')
#        R_ALREADY_SILENCED = True
#
#R_ALREADY_SILENCED_OUTPUT = False
#def silenceROutput():
#    global R_ALREADY_SILENCED_OUTPUT
#    if not R_ALREADY_SILENCED_OUTPUT:
#        from gtrackcore.application.RSetup import r
#        r('sink(file("/dev/null", open="wt"), type="output")')
#        R_ALREADY_SILENCED_OUTPUT = True
#
#def createHyperBrowserURL(genome, trackName1, trackName2=None, track1file=None, track2file=None, \
#                          demoID=None, analcat=None, analysis=None, \
#                          configDict=None, trackIntensity=None, method=None, region=None, \
#                          binsize=None, chrs=None, chrArms=None, chrBands=None, genes=None): 
#    urlParams = []
#    urlParams.append( ('dbkey', genome) )
#    urlParams.append( ('track1', ':'.join(trackName1)) )
#    if trackName2:
#        urlParams.append( ('track2', ':'.join(trackName2)) )
#    if track1file:
#        urlParams.append( ('track1file', track1file) )
#    if track2file:
#        urlParams.append( ('track2file', track2file) )
#    if demoID:
#        urlParams.append( ('demoID', demoID) )
#    if analcat:
#        urlParams.append( ('analcat', analcat) )
#    if analysis:
#        urlParams.append( ('analysis', analysis) )
#    if configDict:
#        for key, value in configDict.iteritems():
#            urlParams.append( ('config_%s' % key, value) )
#    if trackIntensity:
#        urlParams.append( ('trackIntensity', trackIntensity) )
#    if method:
#        urlParams.append( ('method', method) )
#    if region:
#        urlParams.append( ('region', region) )
#    if binsize:
#        urlParams.append( ('binsize', binsize) )
#    if chrs:
#        urlParams.append( ('__chrs__', chrs) )
#    if chrArms:
#        urlParams.append( ('__chrArms__', chrArms) )
#    if chrBands:
#        urlParams.append( ('__chrBands__', chrBands) )
#    if genes:
#        urlParams.append( ('genes', genes) )
#    #genes not __genes__?
#    #encode?
#    
#    return URL_PREFIX + '/hyper?' + '&'.join([urllib.quote(key) + '=' + \
#                                              urllib.quote(value) for key,value in urlParams])
#    
#@decorator
#def obsoleteHbFunction(func, *args, **kwArgs):
#    print 'Warning, this function is going to be phased out of the HB codebase..'
#    return func(*args, **kwArgs)
#
#def numAsPaddedBinary(comb, length):
#    return '0'*(length-len(bin(comb)[2:]))+bin(comb)[2:]
#    
#@contextlib.contextmanager
#def changedWorkingDir(new_dir):
#    orig_dir = os.getcwd()
#    os.chdir(new_dir)
#    try:
#        yield
#    finally:
#        os.chdir(orig_dir)
#        
def convertTNstrToTNListFormat(tnStr, doUnquoting=False):
    tnStr = tnStr.strip()
    tnList = re.split(':|\^|\|', tnStr)
    if doUnquoting:        
        tnList = [urllib.unquote(x) for x in tnList]
    return tnList
#    
##used by echo
#def format_arg_value(arg_val):
#    """ Return a string representing a (name, value) pair.
#    
#    >>> format_arg_value(('x', (1, 2, 3)))
#    'x=(1, 2, 3)'
#    """
#    arg, val = arg_val
#    return "%s=%r" % (arg, val)
#    
#def echo(fn, write=sys.stdout.write):
#    """ Echo calls to a function.
#    
#    Returns a decorated version of the input function which "echoes" calls
#    made to it by writing out the function's name and the arguments it was
#    called with.
#    """
#    import functools
#    # Unpack function's arg count, arg names, arg defaults
#    code = fn.func_code
#    argcount = code.co_argcount
#    argnames = code.co_varnames[:argcount]
#    fn_defaults = fn.func_defaults or list()
#    argdefs = dict(zip(argnames[-len(fn_defaults):], fn_defaults))
#    
#    @functools.wraps(fn)
#    def wrapped(*v, **k):
#        # Collect function arguments by chaining together positional,
#        # defaulted, extra positional and keyword arguments.
#        positional = map(format_arg_value, zip(argnames, v))
#        defaulted = [format_arg_value((a, argdefs[a]))
#                     for a in argnames[len(v):] if a not in k]
#        nameless = map(repr, v[argcount:])
#        keyword = map(format_arg_value, k.items())
#        args = positional + defaulted + nameless + keyword
#        write("%s(%s)\n" % (name(fn), ", ".join(args)))
#        return fn(*v, **k)
#    return wrapped
#
def getDirPath(trackName, genome, chr=None, allowOverlaps=False, basePath=Config.PROCESSED_DATA_PATH):
    """
    >>> getDirPath(['trackname'],'genome','chr1')
    '/100000/noOverlaps/genome/trackname/chr1'
    """
    from gtrackcore.util.CompBinManager import CompBinManager
    if len(trackName)>0 and trackName[0] == 'redirect':
        genome = trackName[1]
        chr = trackName[2]
        #trackName[3] is description
        trackName = trackName[4:]
        
    #print [basePath, str(CompBinManager.getIndexBinSize()), ('withOverlaps' if allowOverlaps else 'noOverlaps'), genome] +\
    #    list(trackName) + ([chr] if chr is not None else [])
    
    return os.sep.join( [basePath, str(CompBinManager.getIndexBinSize()), ('withOverlaps' if allowOverlaps else 'noOverlaps'), genome] +\
        list(trackName) + ([chr] if chr is not None else []) )
#
##def createMemoPath(trackName, genome, chr, statName):
##    return os.sep.join( [MEMOIZED_DATA_PATH, statName, str(COMP_BIN_SIZE), genome]+list(trackName)+[chr] )
#def createMemoPath(region, statId, configHash, track1Hash, track2Hash):
#    chr = region.chr
#    genome = region.genome
#    return os.sep.join( [MEMOIZED_DATA_PATH, str(len(region)), statId, genome, str(track1Hash)] + \
#                        ([str(track2Hash)] if track2Hash is not None else []) + \
#                        [str(configHash), chr] ).replace('-','_') #replace('-','_') because hashes can be minus, and minus sign makes problems with file handling
#
#@takes(str,(list,tuple),(str,type(None)))
def createOrigPath(genome, trackName, fn=None):
    return os.sep.join([Config.ORIG_DATA_PATH, genome] + trackName + ([fn] if fn is not None else []))
#
#@takes(str,(list,tuple),(str,type(None)))
#def createCollectedPath(genome, trackName, fn=None):
#    return os.sep.join([Config.NONSTANDARD_DATA_PATH, genome] + trackName + ([fn] if fn is not None else []))
#    
#@takes(str,(list,tuple),(str,type(None)))
#def createParsingErrorPath(genome, trackName, fn=None):
#    return os.sep.join([Config.PARSING_ERROR_DATA_PATH, genome] + trackName + ([fn] if fn is not None else []))

#@takes(str)
def getFileSuffix(fn):
    from gtrackcore.core.DataTypes import getSupportedFileSuffixes
    for suffix in getSupportedFileSuffixes():
        if '.' in suffix and fn.endswith('.' + suffix):
            return suffix
    return os.path.splitext(fn)[1].replace('.','')
#
#def getOrigFns(genome, trackName, suffix, fileTree='standardized'):
#    assert fileTree in ['standardized', 'collected', 'parsing error']
#    from gtrackcore.application.LogSetup import logMessage, logging
#    
#    if fileTree == 'standardized':
#        path = createOrigPath(genome, trackName)
#    elif fileTree == 'collected':
#        path = createCollectedPath(genome, trackName)
#    else:
#        path = createParsingErrorPath(genome, trackName)
#
#    if not os.path.exists(path):
#        if IS_EXPERIMENTAL_INSTALLATION:
#            logMessage('getOrigFn - Path does not exist: ' + path, logging.WARNING)
#        return []
#    
#    return [path + os.sep + x for x in os.listdir(path) if os.path.isfile(path + os.sep + x) \
#            and x.endswith(suffix) and not x[0] in ['.','_','#'] and not x[-1] in ['~','#']]
#    
#def getOrigFn(genome, trackName, suffix, fileTree='standardized'):
#    fns = getOrigFns(genome, trackName, suffix, fileTree=fileTree)
#    if len(fns) != 1:
#        if IS_EXPERIMENTAL_INSTALLATION:
#            from gtrackcore.application.LogSetup import logMessage, logging
#            logMessage('getOrigFn - Cannot decide among zero or several filenames: %s' % fns, logging.WARNING)
#        return None
#    
#    return fns[0]
#
#def parseDirPath(path):
#    'Returns [genome, trackName, chr] from directory path'
#    path = path[len(PROCESSED_DATA_PATH + os.sep):]# + str(CompBinManager.getIndexBinSize())):]
#    while path[0] == os.sep:
#        path = path[1:]
#    path.replace(os.sep*2, os.sep)
#    el = path.split(os.sep)
#    return el[2], tuple(el[3:-1]), el[-1]
#
def extractTrackNameFromOrigPath(path):
    """
    Convert a absolute trackName path to a trackName list .

    Parameters
    ==========
    path : string
        The absolute path of a track.

    Returns
    =======
    list
        The trackName list that has been extracted from the path.
    """
    excludeEl = None if os.path.isdir(path) else -1
    path = path[len(Config.ORIG_DATA_PATH):]
    path = path.replace('//','/')
    if path[0]=='/':
        path = path[1:]
    if path[-1]=='/':
        path = path[:-1]
    return path.split(os.sep)[1:excludeEl]
#    
def getStringFromStrand(strand):
    if strand in (None, BINARY_MISSING_VAL):
        return '.'
    return '+' if strand else '-'

def parseRegSpec(regSpec, genome = None, includeExtraChrs = False):
    from gtrackcore.track.core.GenomeRegion import GenomeRegion
    from gtrackcore.metadata.GenomeInfo import GenomeInfo

    class SimpleUserBinSource(list):
        pass
        
    regions = []
    allRegSpecs = regSpec.strip().split(',')
    for curRegSpec in allRegSpecs:
        regParts = curRegSpec.strip().split(':')
        if genome == None:
            genome = regParts[0]
            #assert GenomeInfo(genome).isInstalled(), "Specified genome is not installed: %s" % genome
        
        if not (regParts[0]=='*' or regParts[0] in GenomeInfo.getExtendedChrList(genome)):
        #if (regParts[0]=='*' or regParts[0].startswith('chr')):
        #    if genome == None:
        #        genome = DEFAULT_GENOME
        #else:
        #    assert genome is None or genome == regParts[0], \
    
            assert regParts[0] == genome, \
                "Region specification does not start with one of '*' or correct chromosome or genome name. Region specification: %s. Genome: %s" % (curRegSpec, genome)
            #genome = regParts[0]        
            regParts = regParts[1:]
        
        if regParts[0] == '*':
            assert len(regParts) == 1, \
                "Region specification starts with '*' but continues with ':'. Region specification: %s" % curRegSpec
            assert len(allRegSpecs) == 1, \
                "Region specification is '*', but is in a list with other region specifications: %s" % regSpec
            chrList = GenomeInfo.getExtendedChrList(genome) if includeExtraChrs else GenomeInfo.getChrList(genome)
            for chr in chrList:
                regions.append(GenomeRegion(genome, chr, 0, GenomeInfo.getChrLen(genome, chr)))
        else:
            #assert(regParts[0].startswith('chr')), \
            assert regParts[0] in GenomeInfo.getExtendedChrList(genome), \
                "Region specification does not start with chromosome specification. Region specification: %s " % curRegSpec
            chr = regParts[0]
            try:
                chrLen = GenomeInfo.getChrLen(genome, chr)
            except Exception, e:
                raise InvalidFormatError("Chromosome '%s' does not exist for genome '%s'" % (chr, genome))
                
            if len(regParts)>1:
                posParts = regParts[1]
                assert '-' in posParts, \
                    "Position specification does not include character '-'. Region specification: %s " % curRegSpec
                rawStart, rawEnd = posParts.split('-')
                
                start = int(rawStart.replace('k','001').replace('m','000001'))
                end = int(rawEnd.replace('k','000').replace('m','000000')) if rawEnd != '' else chrLen
                assert start >= 1, \
                    "Start position is not positive. Region specification: %s " % curRegSpec
                assert end >= start, \
                    "End position is not larger than start position. Region specification: %s " % curRegSpec
                assert end <= chrLen, \
                    "End position is larger than chromosome size. Genome: %s. Chromosome size: %s. Region specification: %s" % (genome, chrLen, curRegSpec)
                #-1 for conversion from 1-indexing to 0-indexing end-exclusive
                start-=1
                
            else:
                start,end = 0, chrLen
            regions.append( GenomeRegion(genome, chr, start, end) )
    ubSource = SimpleUserBinSource(regions)
    ubSource.genome = genome
    return ubSource

def parseTrackNameSpec(trackNameSpec):
    return trackNameSpec.split(':')
#    
def prettyPrintTrackName(trackName, shortVersion=False):
    from urllib import unquote
    if len(trackName) == 0:
        return ''
    elif len(trackName) == 1:
        return trackName[0]
    elif trackName[0] in ['galaxy','redirect','virtual']:
        return "'" + re.sub('([0-9]+) - (.+)', '\g<2> (\g<1>)', unquote(trackName[3])) + "'"
    elif trackName[0] in ['external']:
        return "'" + re.sub('[0-9]+ - ', '', unquote(trackName[4])) + "'"
    else:
        if trackName[-1]=='':
            return "'" + trackName[-2] + "'"
        return "'" + trackName[-1] + (' (' + trackName[-2] + ')' if not shortVersion else '') + "'"
        #return "'" + trackName[1] + (' (' + '-'.join(trackName[2:]) + ')' if len(trackName) > 2 else '') + "'"
        #return trackName[1] + (' (' + '-'.join(trackName[2:]) + ')' if len(trackName) > 2 else '')
#    
#def insertTrackNames(text, trackName1, trackName2 = None, shortVersion=False):
#    PREFIX = '(the points of |points of |point of |the segments of |segments of |segment of |the function of |function of )?'
#    POSTFIX = '([- ]?segments?|[- ]?points?|[- ]?function)?'
#    newText = re.sub(PREFIX + '[tT](rack)? ?1' +  POSTFIX, prettyPrintTrackName(trackName1, shortVersion), text)
#    if trackName2 != None:
#        newText = re.sub(PREFIX + '[tT](rack)? ?2' + POSTFIX, prettyPrintTrackName(trackName2, shortVersion), newText)
#    return newText
#
#def resultsWithoutNone(li):
#    for el in li:
#        if el is not None:
#            yield el
#
#def smartSum(li):
#    try:
#        resultsWithoutNone(li).next()
#    except StopIteration:
#        return None
#    
#    return sum(resultsWithoutNone(li))
#
def isIter(obj):
    from numpy import memmap
    if isinstance(obj, memmap):
        return False
    return hasattr(obj, '__iter__')

def getClassName(obj):
    return obj.__class__.__name__

def strWithStdFormatting(val):
    try:
        assert val != int(val)
        integral, fractional = (('%#.' + str(Config.OUTPUT_PRECISION) + 'g') % val).split('.')
    except:
        integral, fractional = str(val), None
        
    try:
        return ('-' if integral[0] == '-' else '') + \
            '{:,}'.format(abs(int(integral))).replace(',', ' ') + \
            ('.' + fractional if fractional is not None else '')
    except:
        return integral
#
#def smartStrLower(obj):    
#    return str.lower(str(obj))
#
def splitOnWhitespaceWhileKeepingQuotes(msg):
    return re.split('\s+(?=(?:[^"]*"[^"]*")*[^"]*$)', msg.strip())

def parseShortenedSizeSpec(spec):
    spec = spec.strip()
    if spec[-1].lower() == 'k':
        size = int(spec[0:-1]) * 1000
    elif spec[-1].lower() == 'm':
        size = int(spec[0:-1]) * 1000000
    else:
        size = int(spec)
    return size
#
#def generateStandardizedBpSizeText(size):
#    if size == 0:
#        return '0 bp'
#    elif size % 10**9 == 0:
#        return str(size/10**9) + ' Gb'
#    elif size % 10**6 == 0:
#        return str(size/10**6) + ' Mb'
#    elif size % 10**3 == 0:
#        return str(size/10**3) + ' kb'
#    else:
#        return str(size) + ' bp'
#    
#
#
#def quenchException(fromException, replaceVal):
#    "if a certain exception occurs within method, catch this exception and instead return a given value"
#    def _quenchException(func, *args, **kwArgs):
#        try:        
#            return func(*args, **kwArgs)
#        except fromException,e:
#            return replaceVal
#    return decorator(_quenchException)
#
#def reverseDict(mapping):
#    vals = mapping.values()
#    assert len(set(vals)) == len(vals) #Ensure all values are unique
#    return dict((v,k) for k, v in mapping.iteritems())
#
#def mean(l):
#    return float(sum(l)) / len(l)
#
def product(l):
    """Product of a sequence."""
    return functools.reduce(operator.mul, l, 1)
    
def flatten(l):
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

def multiReplace(str, fromList, toList):
    assert len(fromList) == len(toList)
    for i, fromStr in enumerate(fromList):
        str = str.replace(fromStr, toList[i])
    return str

def replaceIllegalElementsInTrackNames(string):
    return multiReplace(string, [':','=','[',']','/','-->'],['.','-','(',')','_', '-'])

#def repackageException(fromException, toException):
#    def _repackageException(func, *args, **kwArgs):
#        try:        
#            return func(*args, **kwArgs)
#        except fromException,e:
#            raise toException('Repackaged exception.., original was: ' + getClassName(e) + ' - '+str(e) + ' - ' + traceback.format_exc())
#    return decorator(_repackageException)
#
##Typical use, for instance
#    #from gtrackcore.util.CommonFunctions import repackageException
#    #from gtrackcore.util.CustomExceptions import ShouldNotOccurError
#    #@repackageException(Exception, ShouldNotOccurError)
#
##Repackaging can also be done manually for chunks of code by:
#    #import traceback
#    #from gtrackcore.util.CustomExceptions import ShouldNotOccurError
#    #from gtrackcore.util.CommonFunctions import getClassName
#    #try:
#    #    pass #code chunk here..
#    #except Exception,e:
#    #    raise ShouldNotOccurError('Repackaged exception.., original was: ' + getClassName(e) + ' - '+str(e) + ' - ' + traceback.format_exc())

def getDatabasePath(dirPath, trackName):
    DATABASE_FILE_SUFFIX = 'h5'  # put in Config
    return "%s%s%s.%s" % (dirPath, os.sep, trackName[-1], DATABASE_FILE_SUFFIX)

import os
import logging
import time
import traceback

from copy import copy
from logging import FileHandler
from logging.handlers import RotatingFileHandler
from urllib import unquote

from gtrackcore.third_party.decorator import decorator
from gtrackcore.core.Config import Config

gtrackcore_LOGGER = 'gtrackcore'

LOG_PATH = Config.LOG_PATH
DETAILED_ROTATING_LOG_FN = LOG_PATH + os.sep + 'detailed.log'
WARNINGS_LOG_FN = LOG_PATH + os.sep + 'warnings.log'

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

defaultFormatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

logging.getLogger(gtrackcore_LOGGER).setLevel(5)

detailedHandler = RotatingFileHandler(DETAILED_ROTATING_LOG_FN, maxBytes=10**6, backupCount=5, delay=True)
detailedHandler.setLevel(logging.DEBUG)
detailedHandler.setFormatter(defaultFormatter)
logging.getLogger(gtrackcore_LOGGER).addHandler(detailedHandler)

warningsHandler = FileHandler(WARNINGS_LOG_FN)
warningsHandler.setLevel(logging.WARNING)
warningsHandler.setFormatter(defaultFormatter)
logging.getLogger(gtrackcore_LOGGER).addHandler(warningsHandler)

def exceptionLogging(exceptClass = Exception, level=logging.DEBUG, message='', raiseFurther=False):
    def _exceptionLogging(func, *args, **kwArgs):
        try:
            return func(*args, **kwArgs)
        except exceptClass,e:
            logging.getLogger(gtrackcore_LOGGER).log(level, 'Exception in ' + func.__name__ + '() in module ' + func.__module__  + \
                                               ' - ' + e.__class__.__name__ + ': ' + str(e) +'. ' + message)
            logging.getLogger(gtrackcore_LOGGER).debug(traceback.format_exc())
            if raiseFurther:
                raise
    return decorator(_exceptionLogging)

def logException(e, level = logging.DEBUG, message = ''):
    logging.getLogger(gtrackcore_LOGGER).log(level, 'Exception' + \
                                   ' - ' + e.__class__.__name__ + ': ' + str(e) +'. ' + message)
    logging.getLogger(gtrackcore_LOGGER).debug(traceback.format_exc())
    
def logMessage(message, level = logging.DEBUG, logger=gtrackcore_LOGGER):
    #from traceback import extract_stack
    #logging.getLogger(logger).log(level, str(extract_stack()))
    logging.getLogger(logger).log(level, message)
    
LOG_ONCE_CACHE = set([])
def logMessageOnce(message, id=None, level = logging.DEBUG, logger=gtrackcore_LOGGER):
    if id is None:
        id = message
    if not id in LOG_ONCE_CACHE:
        LOG_ONCE_CACHE.add(id)
        logMessage(message, level, logger)
    
def logExceptionOnce(e, level = logging.DEBUG, message='', id=None):
    if id is None:
        id = message
    assert id!='' #should not have empty id as this is used to avoid future logging of same id..
    if not id in LOG_ONCE_CACHE:
        LOG_ONCE_CACHE.add(id)
        logException(e, level, message)

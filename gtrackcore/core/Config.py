import os

from ConfigParser import SafeConfigParser
from collections import OrderedDict
from itertools import chain


class ConfigInit(type):
    def __getattribute__(cls, key):
        if not (type.__getattribute__(cls, '_INITIALIZED') or key == 'initialize'):
            type.__getattribute__(cls, 'initialize')()

        return type.__getattribute__(cls, key)

class Config(object):
    __metaclass__ = ConfigInit

    _INITIALIZED = False

    @classmethod
    def initialize(cls, configFileName=None, dataDir=None):
        cls._INITIALIZED = True

        if dataDir is not None:
            dataDir = '/'.join(dataDir.split('/')[:-1])
            gtrackcore_dir = dataDir

        else:
            gtrackcore_dir = os.environ.get('GTRACKCORE_DIR')

            if not gtrackcore_dir:
                if os.environ.get('HOME') is not None:
                    print 'GTRACKCORE_DIR env should be defined. Using %s as data directory' % os.environ.get('HOME')
                    gtrackcore_dir = os.environ.get('HOME')
                else:
                    raise EnvironmentError('Neither env GTRACKCORE_DIR nor HOME is set')

            if gtrackcore_dir[-1] == '/':
                gtrackcore_dir = gtrackcore_dir[:-1]

        # temp hack until GTRACKCORE_DIR is set on insilico
        if gtrackcore_dir == '/cluster/home/ghbrowse':
            gtrackcore_dir = '/hyperbrowser/staticFiles/gtrackcore'
            print 'Using /hyperbrowser/staticFiles/gtrackcore as data directory...'

        data_dir = os.sep.join([gtrackcore_dir, 'gtrackcore_data'])
        config_filename = os.sep.join([gtrackcore_dir, 'gtrackcore_config'])
        try:
            configDef = OrderedDict()

            configDef['General'] = OrderedDict( \
                [('LOG_PATH', os.sep.join([gtrackcore_dir, 'gtrackcore_logs'])), \
                 ('ORIG_DATA_PATH', os.sep.join([data_dir, 'Original'])), \
                 ('PROCESSED_DATA_PATH', os.sep.join([data_dir, 'Processed'])), \
                 ('METADATA_FILES_PATH', os.sep.join([data_dir, 'Metadata'])), \
                 ('RESOURCE_DONWLOAD_DIR', os.sep.join([data_dir, 'tmp/downloads'])), \
                 ('RESOURCE_DIR', os.sep.join([data_dir, 'tmp/resources'])), \
                 ('MAX_CONCAT_LEN_FOR_OVERLAPPING_ELS', '20'), \
                 ('OUTPUT_PRECISION', '4'), \
                 ('USE_SLOW_DEFENSIVE_ASSERTS', 'False')])

            configDef['Compatibility'] = OrderedDict( \
                [('URL_PREFIX', '')])

            configDef['Memmap'] = OrderedDict( \
                [('COMP_BIN_SIZE', '100000'), \
                 ('MEMMAP_BIN_SIZE', str(1024 * 1024))])

            cls._initConfig(configDef)

            if config_filename:
                if os.path.exists(config_filename):
                    cls._readConfig(config_filename, configDef)
                cls._writeConfig(config_filename, configDef)

        except:
            cls._INITIALIZED = False
            raise

    @classmethod
    def _readConfig(cls, configFileName, configDef):
        defaults = cls._getDefaultDict(configDef)
        config = SafeConfigParser(defaults)
        config.read(configFileName)

        for section, section_vars in configDef.iteritems():
            if config.has_section(section):
                for var, val in section_vars.iteritems():
                    configMethod = cls._getConfigParseMethod(val)
                    setattr(cls, var, getattr(config, configMethod)(section, var))

    @classmethod
    def _initConfig(cls, configDef):
        defaults = cls._getDefaultDict(configDef)

        for section, section_vars in configDef.iteritems():
            for var, val in section_vars.iteritems():
                valType = cls._getValType(val)
                setattr(cls, var, valType(val))

    @classmethod
    def _writeConfig(cls, configFileName, configDef):
        config = SafeConfigParser()
        for section, section_vars in configDef.iteritems():
            config.add_section(section)
            for var in section_vars:
                config.set(section, var, str(getattr(cls, var)))

        with open(configFileName, 'wb') as configFile:
            config.write(configFile)

    @classmethod
    def _getDefaultDict(cls, configDef):
        return OrderedDict(chain(*[configDef[section].iteritems() for section in configDef]))

    @classmethod
    def _getConfigParseMethod(cls, val):
        return cls._commonGetParseMethod(val, returnConfigMethod=True)

    @classmethod
    def _getValType(cls, val):
        return cls._commonGetParseMethod(val, returnConfigMethod=False)

    @classmethod
    def _commonGetParseMethod(cls, val, returnConfigMethod):
        try:
            int(val)
            configMethod, valType = 'getint', int
        except:
            try:
                float(val)
                configMethod, valType = 'getfloat', float
            except:
                if val.lower() in ['true', 'false']:
                    configMethod, valType = 'getboolean', bool
                else:
                    configMethod, valType = 'get', str

        return configMethod if returnConfigMethod else valType

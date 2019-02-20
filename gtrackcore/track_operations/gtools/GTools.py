import argparse
import importlib
import logging
import tempfile
from datetime import datetime
import shutil

from gtrackcore.api.BTrack import BTrack
from gtrackcore.api.CommandParser import CommandParser
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.gtools.OperationHelp import OperationHelp
from gtrackcore.track_operations.operations.Operator import getOperation, Operator


class GTools(object):

    def __init__(self):

        self._importOperations()
        self._parser = self._createParser()
        if self._args.debug:
            level = logging.DEBUG
        else:
            level = logging.INFO

        logging.basicConfig(level=level,
                            format='[%(asctime)s - %(filename)s:%(lineno)s '
                                   '%(funcName)20s()] %(levelname)7s - '
                                   '%(message)s')
        self.runOperation()

    def runOperation(self):
        """
        Run the selected operation.
        :return: None
        """
        logging.debug(self._args)

        logging.debug("Loaded operations: {0}".format(
            self._importedOperations.keys()))

        operation = self._args.which
        if not operation:
            return

        if operation == 'create':
            BTrack(self._args.btrackPath, self._args.genomePath)
        elif operation == 'list':
            btrack = BTrack(self._args.btrackPath)
            btrack.listTracks()

        elif operation == 'import':
            btrack = BTrack(self._args.btrackPath)
            btrack.importTrackFromFile(self._args.trackPath, self._args.trackName)

        elif operation == 'export':
            allowOverlaps = not self._args.noOverlaps
            btrack = BTrack(self._args.btrackPath)
            btrack.exportTrackToFile(self._args.trackPath, self._args.trackName, allowOverlaps=allowOverlaps)
        elif operation == 'execute':
            allowOverlaps = not self._args.noOverlaps
            tmpDirPath = None
            btrack= None
            if self._args.btrackPath:
                btrack = BTrack(self._args.btrackPath)
            if self._args.tracks:
                if not self._args.genomePath:
                    print 'Genome path missing'
                    return
                if not btrack:
                    tmpDirPath = tempfile.mkdtemp()
                    btrack = BTrack(tmpDirPath, self._args.genomePath)
                for trackPath in self._args.tracks:
                    variable, path = trackPath.split('=')
                    btrack.importTrackFromFile(path, variable)

            if not btrack or not btrack.hasTracks():
                print 'Could not load tracks'
                return

            parser = CommandParser(self._importedOperations, btrack)
            obj = parser.parse(self._args.command)

            outputTrackName = None
            if isinstance(obj, Operator):
                res = obj.calculate()
            elif isinstance(obj, tuple):
                outputTrackName = obj[0]
                res = obj[1].calculate()
            else:
                print 'Could not evaluate operation'
                return

            if isinstance(res, TrackContents):
                if not outputTrackName:
                    outputTrackName = self.generateTrackName('outputTrack')
                btrack.importTrack(res, outputTrackName, allowOverlaps=allowOverlaps)
                if self._args.outputPath:
                    btrack.exportTrackToFile(self._args.outputPath, outputTrackName,
                                             allowOverlaps=allowOverlaps)
                elif tmpDirPath:
                    print 'No btrack or output path'
            elif res:
                print "Result:"
                if isinstance(res, dict):
                    for k,v in res.iteritems():
                        print str(k) + ' : ' + str(v)
            else:
                print "Did not get any result"

            if tmpDirPath:
                shutil.rmtree(tmpDirPath)
        elif operation == 'help':
            if self._args.operation:
                operation = self._importedOperations[self._args.operation]
                operationHelp = OperationHelp(operation)
                print operationHelp.getHelpStr()
                print operationHelp.getTrackHelp()
                print operationHelp.getKwArgHelp()
            else:
                self._parser.print_help()
                print '\n--Operations: '
                for op in self._importedOperations:
                    print op


    def generateTrackName(self, prefix):
        return prefix + '_' + str(datetime.now().strftime('%Y%m%d_%H%M%S'))

    def _importOperations(self):
        """
        Import all defined operations
        :return: None
        """
        module, operations = getOperation()

        self._importedOperations = {}

        for operation in operations:
            m = "{0}.{1}".format(module, operation)

            mod = importlib.import_module(m)
            cls = getattr(mod, operation)

            # TODO check if class

            self._importedOperations[operation] = cls

    def _createParser(self):
        """
        Create the main argparser. Subparsers for each operation
        are dynamically created using a classmethod in each operation.
        :return: None
        """

        parser = argparse.ArgumentParser(prog='GTools')
        parser.add_argument('-d', '--debug', action='store_true',
                            help='Run in debug mode')
        subparsers = parser.add_subparsers(help='Supported commands')

        list = subparsers.add_parser('list', help='List tracks in provided BTrack')
        list.add_argument('-b', help="Btrack path", dest='btrackPath')
        list.set_defaults(which='list')

        imp = subparsers.add_parser('import', help='Import track')
        imp.add_argument('-t', help="File path of the track", dest='trackPath')
        imp.add_argument('-n', help="Name of the track", dest='trackName')
        imp.add_argument('-b', help="Btrack path", dest='btrackPath')
        imp.set_defaults(which='import')

        exp = subparsers.add_parser('export', help='Export track to disk')
        exp.add_argument('-o', help='File path of output', dest='trackPath')
        exp.add_argument('-n', help='Name of the track', dest='trackName')
        exp.add_argument('-b', help="Btrack path", dest='btrackPath')
        exp.add_argument('--noOverlaps', action='store_true', help='Do not allow overlaps')
        exp.set_defaults(which='export')

        create = subparsers.add_parser('create', help='Create new BTrack')
        create.add_argument('-b', help='File path for btrack', dest='btrackPath')
        create.add_argument('-g', help='File path for genome', dest='genomePath')
        create.set_defaults(which='create')

        execute = subparsers.add_parser('execute', help='Execute command (track operations)')
        execute.add_argument('command', help='command as a string')
        execute.add_argument('tracks', nargs='*', help='Variables with path to tracks')
        execute.add_argument('-b', help='File path for btrack', dest='btrackPath')
        execute.add_argument('--noOverlaps', action='store_true', help='Do not allow overlaps')
        execute.add_argument('-o', help='File path for output', dest='outputPath')
        execute.add_argument('-g', help='Genome path', dest='genomePath')
        execute.set_defaults(which='execute')

        help = subparsers.add_parser('help', help='Display help for operation that is used as a parameter')
        help.add_argument('operation', nargs='?', help='Operation name')
        help.set_defaults(which='help')

        self._args = parser.parse_args()

        return parser

if __name__ == '__main__':
    GTools()



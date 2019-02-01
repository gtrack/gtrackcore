import argparse
import importlib
import logging

from gtrackcore.api.BTrack import BTrack
from gtrackcore.api.CommandParser import CommandParser
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.operations.Operator import getOperation, Operator


class GTools(object):

    def __init__(self):

        self._importOperations()
        self._createParser()
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

        if operation == 'test':
            btrack = BTrack(self._args.path, self._args.genome)
            t1 = btrack.importTrackFromFile(self._args.trackPath, 'testtrack:whatever')

            btrack.importTrack(t1, "trackFromContents")

            btrack.exportTrackToFile('/Users/radmilko/PycharmProjects/gtools/gtrackcore/data/gtrack/exportedTrack.bed', trackContents=t1)

        elif operation == 'create':
            btrack = BTrack(self._args.btrackPath, self._args.genomePath)

        elif operation == 'list':
            btrack = BTrack(self._args.btrackPath)
            btrack.listTracks()

        elif operation == 'import':
            btrack = BTrack(self._args.btrackPath)
            t1 = btrack.importTrackFromFile(self._args.trackPath, self._args.trackName)

        elif operation == 'export':
            btrack = BTrack(self._args.btrackPath)
            btrack.exportTrackToFile(self._args.trackPath, trackName=self._args.trackName, allowOverlaps=self._args.allowOverlaps)
        elif operation == 'execute':
            btrack = BTrack(self._args.btrackPath)
            parser = CommandParser(self._importedOperations, btrack)
            obj = parser.parse(self._args.command)

            if isinstance(obj, Operator):
                res = obj.calculate()
            elif isinstance(obj, tuple):
                outputTrackName = obj[0]
                res = obj[1].calculate()

            if not res:
                print "did not get any result"
                return

            if isinstance(res, TrackContents):
                if outputTrackName:
                    btrack.importTrack(res, outputTrackName, allowOverlaps=self._args.allowOverlaps)
                else:
                    print 'Missing result track name!'
            else:
                print "Result:"
                print res

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

        list = subparsers.add_parser('list', help='List tracks in GTrackCore')
        list.add_argument('btrackPath', help="Btrack path")
        list.set_defaults(which='list')

        imp = subparsers.add_parser('import', help='Import track')
        imp.add_argument('trackPath', help="File path of the track")
        imp.add_argument('trackName', help="Name of the track")
        imp.add_argument('btrackPath', help="Btrack path")
        imp.set_defaults(which='import')

        exp = subparsers.add_parser('export', help='Export track to disk')
        exp.add_argument('trackName', help='Name of the track')
        exp.add_argument('trackPath', help='File path of track')
        exp.add_argument('btrackPath', help="Btrack path")
        exp.add_argument('--allowOverlaps', action='store_true', help='Allow overlaps')
        exp.set_defaults(which='export')

        test = subparsers.add_parser('test')
        test.add_argument('path', help="File path for BTrack")
        test.add_argument('genome', help="Path to genome")
        test.add_argument('trackPath', help="Path to track")
        test.set_defaults(which='test')

        create = subparsers.add_parser('create')
        create.add_argument('btrackPath', help='File path for btrack')
        create.add_argument('genomePath', help='File path for genome')
        create.set_defaults(which='create')

        execute = subparsers.add_parser('execute')
        execute.add_argument('command', help='command as a string')
        execute.add_argument('btrackPath', help='File path for btrack')
        execute.add_argument('--allowOverlaps', action='store_true', help='Allow overlaps')
        execute.set_defaults(which='execute')

        self._args = parser.parse_args()

if __name__ == '__main__':
    GTools()

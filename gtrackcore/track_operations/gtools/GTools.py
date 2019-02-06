import argparse
import importlib
import logging
import tempfile
from datetime import datetime
import shutil

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
            btrack.exportTrackToFile(self._args.trackPath, trackName=self._args.trackName, allowOverlaps=allowOverlaps)
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

            if isinstance(res, TrackContents):
                if not outputTrackName:
                    outputTrackName = self.generateTrackName('outputTrack')
                btrack.importTrack(res, outputTrackName, allowOverlaps=allowOverlaps)
                if self._args.outputPath:
                    btrack.exportTrackToFile(self._args.outputPath, trackName=outputTrackName,
                                             allowOverlaps=allowOverlaps)
                elif tmpDirPath:
                    print 'No btrack or output path'
            elif res:
                print "Result:"
                print res
            else:
                print "Did not get any result"

            if tmpDirPath:
                shutil.rmtree(tmpDirPath)

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
        list.add_argument('btrackPath', help="Btrack path")
        list.set_defaults(which='list')

        imp = subparsers.add_parser('import', help='Import track')
        imp.add_argument('trackPath', help="File path of the track")
        imp.add_argument('trackName', help="Name of the track")
        imp.add_argument('btrackPath', help="Btrack path")
        imp.set_defaults(which='import')

        exp = subparsers.add_parser('export', help='Export track to disk')
        exp.add_argument('trackPath', help='File path of track')
        exp.add_argument('trackName', help='Name of the track')
        exp.add_argument('btrackPath', help="Btrack path")
        exp.add_argument('--noOverlaps', action='store_true', help='Do not allow overlaps')
        exp.set_defaults(which='export')

        create = subparsers.add_parser('create', help='Create new BTrack')
        create.add_argument('btrackPath', help='File path for btrack')
        create.add_argument('genomePath', help='File path for genome')
        create.set_defaults(which='create')

        execute = subparsers.add_parser('execute', help='Execute command (track operations)')
        execute.add_argument('command', help='command as a string')
        execute.add_argument('tracks', nargs='*', help='Variables with path to tracks')
        execute.add_argument('-b', help='File path for btrack', dest='btrackPath')
        execute.add_argument('--noOverlaps', action='store_true', help='Do not allow overlaps')
        execute.add_argument('-o', help='File path for output', dest='outputPath')
        execute.add_argument('-g', help='Genome path', dest='genomePath')
        execute.set_defaults(which='execute')

        for name, operation in self._importedOperations.iteritems():

            # Call the getKwArguments.
            # Use the kwarguments and nr of tracks to generate
            self._createSubparser(operation, subparsers)


        self._args = parser.parse_args()

    def _createSubparser(self, operation, subparsers):

        if operation is None:
            return

        # Get the operation info
        info = operation.getInfoDict()

        if info['operationHelp'] is None:
            # If there is not defined a help text for the operation we
            # ignore it.
            #print("ignoring: {}".format(operation))
            return

        name = info['name']
        opr = subparsers.add_parser(name,
                                    help=info['operationHelp'],  usage=name + '(args, keywordArgs)')
        opr._positionals.title = 'args - arguments (required)'
        opr._optionals.title = 'keywordArgs - keyword arguments (optional)'

        assert info['numTracks'] == len(info['trackHelp'])

        # Add the track inputs
        if len(info['trackHelp']) == 1:
            opr.add_argument('track', help=info['trackHelp'][0])
        else:
            for i, v in enumerate(info['trackHelp']):
                opr.add_argument('track-{}'.format(i), help=v)

        #opr.add_argument('genome', help='File path of Genome definition')

        # Add the options

        kws = operation.getKwArgumentInfoDict()

        for k, kw in kws.iteritems():
            if kw.shortkey is None:
                # non optional
                if kw.contentType is bool:
                    if kw.defaultValue:
                        # Default is False
                        opr.add_argument(kw.key, action='store_false',
                                         help=kw.help)
                    else:
                        # Default is True
                        opr.add_argument(kw.key, action='store_true',
                                         help=kw.help)
                else:
                    opr.add_argument(kw.key, help=kw.help)

            else:
                # optional
                if kw.contentType is bool:
                    if kw.defaultValue:
                        # Default is False
                        opr.add_argument("-{}".format(kw.shortkey),
                                         "--{}".format(kw.key),
                                         action='store_false',
                                         help=kw.help, dest=k)
                    else:
                        # Default is True
                        opr.add_argument("-{}".format(kw.shortkey),
                                         "--{}".format(kw.key),
                                         action='store_true',
                                         help=kw.help, dest=k)
                else:
                    opr.add_argument("-{}".format(kw.shortkey),
                                     "--{}".format(kw.key),
                                     help=kw.help, dest=k)
        opr.set_defaults(which=info['name'])

if __name__ == '__main__':
    GTools()

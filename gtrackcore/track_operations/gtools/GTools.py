import argparse
import importlib
import logging
import sys

from gtrackcore.api.BTrack import BTrack
from gtrackcore.core.Api import getAvailableTracks
from gtrackcore.core.Api import importFile
from gtrackcore.core.Api import importTrackFromTrackContents
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.operations.Operator import getOperation
from gtrackcore.api.CommandParser import CommandParser

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
            self._listTracksInGTrackCore(self._args.genome)

        elif operation == 'import':
            btrack = BTrack(self._args.btrackPath)
            t1 = btrack.importTrackFromFile(self._args.trackPath, self._args.trackName)

        elif operation == 'export':
            btrack = BTrack(self._args.btrackPath)
            btrack.exportTrackToFile(self._args.trackPath, trackName=self._args.trackName)
        elif operation == 'execute':
            print self._args.btrackPath
            btrack = BTrack(self._args.btrackPath)
            outputTrackName = self._args.command.split('=', 1)[0]
            expr = self._args.command.split('=', 1)[1]
            parser = CommandParser(self._importedOperations, btrack)
            obj = parser.parseFunctionCall(expr)

            res = obj.calculate()

            if not res:
                print "did not get any result"
                return

            if isinstance(res, TrackContents):
                btrack.importTrack(res, outputTrackName)

        else:
            assert operation in self._importedOperations.keys()

            logging.debug("Running operation: {0}".format(operation))

            oper = self._importedOperations[operation]
            # check args?
            a = oper.factory(self._args)
            res = a.calculate()

            if a.resultIsTrack:
                pass

            if res is not None and isinstance(res, TrackContents):
                # Save result if any
                # TODO add support for custom name..
                name = a.createTrackName()
                logging.debug("Importing track. Name: {0}".format(name))

                for k,v in res.trackViews.iteritems():
                    s = v.startsAsNumpyArray()

                    if s is not None and len(s) > 0:
                        print(s)
                        print(type(s))
                        print(v.endsAsNumpyArray())
                        print(type(v.endsAsNumpyArray()))
                        print(v.idsAsNumpyArray())
                        print(type(v.idsAsNumpyArray()))
                        print(v.edgesAsNumpyArray())
                        print(type(v.edgesAsNumpyArray()))
                        print(v.weightsAsNumpyArray())
                        print(type(v.weightsAsNumpyArray()))

                importTrackFromTrackContents(trackContents=res, trackName=name)

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

    def _trackInStdin(self):
        """
        Testing something..

        Problem: How do we "move" a track over the pipe?

        - Saving it in GTrackCore. Piping the name. Removing the track
        afterwards.

        - Will the track be track A or B in the second operation?
            - A as default, switch for B?

        :return: None
        """
        if not sys.stdin.isatty():
            # Running in pipe, trying to parse as track.
            return None
        else:
            return None

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
        list.add_argument('genome', help="Name of genome")
        list.set_defaults(which='list')

        imp = subparsers.add_parser('import', help='Import track')
        imp.add_argument('trackPath', help="File path of the track")
        imp.add_argument('trackName', help="Name of the track")
        imp.add_argument('btrackPath', help="Btrack path")
        imp.set_defaults(which='import')

        exp = subparsers.add_parser('export', help='Export track to disk')
        exp.add_argument('trackName', help='Name of the track')
        #exp.add_argument('allowOverlaps', action='store_true', help='Name of the track')
        exp.add_argument('trackPath', help='File path of track')
        exp.add_argument('btrackPath', help="Btrack path")
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
        execute.set_defaults(which='execute')

        for operation in self._importedOperations.values():

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
            print("ignoring: {}".format(operation))
            return

        name = info['name']
        opr = subparsers.add_parser(name[0].lower() + name[1:],
                                    help=info['operationHelp'])

        assert info['numTracks'] == len(info['trackHelp'])

        # Add the track inputs
        if len(info['trackHelp']) == 1:
            opr.add_argument('track', help=info['trackHelp'][0])
        else:
            for i, v in enumerate(info['trackHelp']):
                opr.add_argument('track-{}'.format(i), help=v)

        opr.add_argument('genome', help='File path of Genome definition')

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
                    print(operation)
                    print(k)
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

    # **** GTools operations ****
    def _listTracksInGTrackCore(self, genome):
        """
        Print the available tracks for a given genome.
        :param genome: String. Selected genome
        :return: None
        """

        tracks = getAvailableTracks(genome)

        print("Available tracks for genome {0}:".format(genome))
        for trackName in tracks:
            print('\t' + ':'.join(trackName))

    def _importTrackFromFile(self, genome, path, name):
        """
        Import track from file into GTrackCore
        :param path:
        :return:
        """
        importFile(path, 'hg19', name)
        #importFile(path, genome, name)

if __name__ == '__main__':
    GTools()

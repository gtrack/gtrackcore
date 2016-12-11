import os
import sys
import logging

import argparse
import importlib

from gtrackcore.track_operations.operations.Operator import getOperation
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.utils.TrackHandling import importTrackIntoGTrack
from gtrackcore.track_operations.Genome import Genome

from gtrackcore.core.Api import importFile
from gtrackcore.core.Api import exportFile

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion

from gtrackcore.core.Api import getAvailableTracks
from gtrackcore.core.Api import importTrackFromTrackContents

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

        if operation == 'list':
            self._listTracksInGTrackCore(self._args.genome)

        elif operation == 'import':
            genome = Genome.createFromJson(self._args.genome)
            importTrackIntoGTrack(self._args.name, genome, self._args.path)

        elif operation == 'export':

            #genome = Genome.createFromJson(self._args.genome)

            # fileFormatName = GTrack

            exportFile(outFileName=self._args.outName,
                       genome=self._args.genome,
                       trackName=self._args.name,
                       fileFormatName='GTrack',
                       allowOverlaps=self._args.allowOverlaps)

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

        list = subparsers.add_parser('list', help='List tracks in '
                                                    'GTrackCore')
        list.add_argument('genome', help="Name of genome")
        list.set_defaults(which='list')

        imp = subparsers.add_parser('import', help='Import track')
        imp.add_argument('genome', help="Name of genome")
        imp.add_argument('path', help="File path of track")
        imp.add_argument('name', help="Name of the track")
        imp.set_defaults(which='import')

        exp = subparsers.add_parser('export', help='Export track to disk')
        exp.add_argument('genome', help='Name of genome')
        exp.add_argument('name', help='Name of the track')
        exp.add_argument('allowOverlaps', action='store_true',
                         help='Name of the track')
        exp.add_argument('outName', help='File name of track')
        exp.set_defaults(which='export')

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

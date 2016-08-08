__author__ = 'skh'

import os
import sys
import logging

import argparse
import importlib

from gtrackcore.track_operations.operations.Operator import getOperation
from gtrackcore.track_operations.TrackContents import TrackContents

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

        else:
            assert operation in self._importedOperations.keys()

            logging.debug("Running operation: {0}".format(operation))

            oper = self._importedOperations[operation]
            # check args?
            a = oper.createOperation(self._args)
            res = a.calculate()

            if a.resultIsTrack():
                pass

            if res is not None and isinstance(res, TrackContents):
                # Save result if any
                # TODO add support for custom name..
                name = a.createTrackName()
                logging.debug("Importing track. Name: {0}".format(name))
                print(res)
                print(name)
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

        subparser = subparsers.add_parser('list', help='List tracks in '
                                                    'GTrackCore')
        subparser.add_argument('genome', help="Name of genome")
        subparser.set_defaults(which='list')

        for operation in self._importedOperations.values():
            operation.createSubParser(subparsers)

        self._args = parser.parse_args()

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

    def _importTrackFromFile(self, path):
        """
        Import track from file into GTrackCore
        :param path:
        :return:
        """
        raise NotImplementedError

if __name__ == '__main__':
    GTools()

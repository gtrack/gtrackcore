__author__ = 'skh'

import os
import sys

import argparse
import importlib

from gtrackcore.track_operations.operations.Operator import getOperation
from gtrackcore.track_operations.TrackContents import TrackContents

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion

from gtrackcore.core.Api import listAvailableTracks


class GTools(object):

    def __init__(self):

        self._importOperations()
        self._createParser()
        self.runOperation()

    def runOperation(self):

        print self._args

        operation = self._args.which

        if operation == 'list':
            listAvailableTracks(self._args.genome)

        else :
            assert operation in self._importedOperations.keys()
            oper = self._importedOperations[operation]
            # check args?
            a = oper.createOperation(self._args)
            res = a()
            print(res.genome.name)

            for region in res.regions:
                starts =  res.getTrackView(region).startsAsNumpyArray()
                ends =  res.getTrackView(region).endsAsNumpyArray()

                if len(starts) != 0:
                    print(starts)
                    print(ends)



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
        parser.add_argument('-d', action='store_true', help='Run in debug mode')
        subparsers = parser.add_subparsers(help='Supported commands')

        subparser = subparsers.add_parser('list', help='List tracks in '
                                                    'GTrackCore')
        subparser.add_argument('genome', help="Name of genome")
        subparser.set_defaults(which='list')

        for operation in self._importedOperations.values():
            operation.createSubParser(subparsers)

        self._args = parser.parse_args()

if __name__ == '__main__':
    GTools()

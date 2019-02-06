from collections import OrderedDict
import json
import yaml

from gtrackcore.track.core.GenomeRegion import GenomeRegion

class Genome(object):
    """
    Container class for a genome definition. Used by the track content class.

    TODO: Create from UCSC files.
    """
    def __init__(self, name, regionDefinition):
        self.__name = name
        self.__regions = self.generateGenomeRegions(self, regionDefinition)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.__name

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def regions(self):
        return self.__regions

    @regions.setter
    def regions(self, regions):
        if isinstance(regions, dict):
            self.__regions = self._generateGenomeRegions(regions)
        else:
            raise TypeError("Regions needs to be a dict")

    def getChromosomeNameList(self):
        chrs = []
        for reg in self.regions:
            chrs.append(reg.chr)

        return chrs

    def getTrackViewList(self):
        pass

    @classmethod
    def _generateGenomeRegions(cls, name, regionDefinition):
        """
        Legacy, remove if not in use.
        :param name:
        :param regionDefinition:
        :return:
        """
        cls.generateGenomeRegions(name, regionDefinition)

    @classmethod
    def generateGenomeRegions(cls, name, regionDefinition):
        """
        Helper method for setting the genome regions. Takes a simple genome
        definition dict and creates a GenomeRegion list.

        The dict needs to be in the form of (segID, segLength).

        Example dict:
        def = {
            "chr1":    247249719,
            "chr2":    242951149,
            "chr3":    199501827,
            "chr4":    191273063,
            ...
            ...
            "chrM":    16571
        }

        :param regionDefinition: Dict defining the length of the regions
        :return: OrderedDict of GenomeRegions
        """

        return list((GenomeRegion(name, c, 0, l)
                        for c, l in regionDefinition.iteritems()))

    @classmethod
    def createFromJson(cls, path):

        # Check if file exists?

        with open(path) as jsonFile:
            g = yaml.safe_load(jsonFile)
            #g = json.load(jsonFile)

        assert "name" in g.keys()
        assert "size" in g.keys()

        gen = Genome(g['name'], g['size'])
        return gen

    def getRegionLength(self, region):
        """
        Return the length of a region
        :param region:
        :return:
        """
        if region in self.__regions:
            return self.__regions[region]
        else:
            return None

    @classmethod
    def createFromTabular(self, path, name):
        chrSizes = {}
        with open(path) as file:
            for line in file:
                cols = line.split('\t')
                if not cols or len(cols) != 2:
                    continue
                chrSizes[cols[0]] = int(cols[1])

        genome = Genome(name, chrSizes)

        return genome



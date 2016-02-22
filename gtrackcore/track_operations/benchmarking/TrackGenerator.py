__author__ = 'skh'

from gtrackcore.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion

import timeit

def generateWorstCasePoints(niceness=10):
    """
    Generate two worst case point tracks
    :param niceness: int. Divide the length of chr1 with this number. The
    large the number the smaller the generated track. Default is 10

    File size will be quite large (>1gb) for niceness smaller the 10.

    This method creates two "worst case" point tracks. The first one
    contains only odd numbered positions (1,3,..., len(chr1)). The second one
    contains only even numbered positions (0,2,4,...,len(chr1)).
    :return: Two worst case point tracks writen to disk.
    """

    hg18 = list((GenomeRegion('hg18', c, 0, l)
                 for c, l in GenomeInfo.GENOMES['hg18']['size'].iteritems()))

    chr1 = (GenomeRegion('hg18', 'chr1', 0,
            GenomeInfo.GENOMES['hg18']['size']['chr1']))

    header = ("##gtrack version: 1.0\n"
              "##track type: points\n"
              "##uninterrupted data lines: true\n"
              "##sorted elements: true\n"
              "##no overlapping elements: true\n"
              "###seqid\tstart\n")

    start = timeit.default_timer()
    with open("./test_tracks/wc-points-odd.gtrack", 'w+') as point:
        point.write(header)

        print("Starting generation odd track of {0}".format(chr1.chr))
        positions = range(1, len(chr1)/niceness, 2)

        for position in positions:
            out = "{0}\t{1}\n".format(chr1.chr, position)
            point.write(out)

    with open("./test_tracks/wc-points-even.gtrack", 'w+') as point:
        point.write(header)

        print("Starting generation even track of {0}".format(chr1.chr))
        positions = range(0, len(chr1)/niceness, 2)

        for position in positions:
            out = "{0}\t{1}\n".format(chr1.chr, position)
            point.write(out)

    end = timeit.default_timer()

    print("Generation finished! Total time {0}".format(end-start))

if __name__ == '__main__':
    generateWorstCasePoints()

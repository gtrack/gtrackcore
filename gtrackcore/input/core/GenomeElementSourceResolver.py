import os
import numpy

from util.CustomExceptions import NotSupportedError


class GenomeElementSourceResolver(object):

    def __new__(cls, fn, genome=None, trackName=None, suffix=None, forPreProcessor=False, *args, **kwArgs):
        return getGenomeElementSourceObject(fn, genome=genome, trackName=trackName, suffix=suffix, forPreProcessor=forPreProcessor, *args, **kwArgs)


def getGenomeElementSourceClass(fn, suffix=None, forPreProcessor=False):
    for geSourceCls in getAllGenomeElementSourceClasses(forPreProcessor):
        for clsSuffix in geSourceCls.FILE_SUFFIXES:
            if fn.endswith('.' + clsSuffix) if suffix is None else clsSuffix == suffix:
                return geSourceCls
    else:
        fileSuffix = os.path.splitext(fn)[1] if suffix is None else suffix
        raise NotSupportedError('File type ' + fileSuffix + ' not supported.')


def getGenomeElementSourceObject(fn, genome=None, trackName=None, suffix=None, forPreProcessor=False, *args, **kwArgs):
    geSourceCls = getGenomeElementSourceClass(fn, suffix=suffix, forPreProcessor=forPreProcessor)

    return geSourceCls(fn, genome=genome, trackName=trackName, *args, **kwArgs)


def getAllGenomeElementSourceClasses(forPreProcessor):
    import pyximport;
    pyximport.install(setup_args={"include_dirs": numpy.get_include()},
                      reload_support=True, language_level=2)
    from gtrackcore.input.fileformats.BedGenomeElementSource import \
        PointBedGenomeElementSource, BedValuedGenomeElementSource, \
        BedCategoryGenomeElementSource, BedGenomeElementSource
    from gtrackcore.input.fileformats.GffGenomeElementSource import \
        GffCategoryGenomeElementSource, GffGenomeElementSource
    from gtrackcore.input.fileformats.FastaGenomeElementSource import FastaGenomeElementSource
    from gtrackcore.input.fileformats.HBFunctionGenomeElementSource import \
        HBFunctionGenomeElementSource
    from gtrackcore.input.fileformats.BedGraphGenomeElementSource import \
        BedGraphTargetControlGenomeElementSource, BedGraphGenomeElementSource
    from gtrackcore.input.fileformats.MicroarrayGenomeElementSource import \
        MicroarrayGenomeElementSource
    from gtrackcore.input.fileformats.BigBedGenomeElementSource import \
        BigBedGenomeElementSource

    from input.fileformats.VcfGenomeElementSource import VcfGenomeElementSource
    allGESourceClasses = [PointBedGenomeElementSource, BedValuedGenomeElementSource,
                          BedCategoryGenomeElementSource, \
                          BedGenomeElementSource, GffCategoryGenomeElementSource,
                          GffGenomeElementSource, \
                          FastaGenomeElementSource, HBFunctionGenomeElementSource, \
                          BedGraphTargetControlGenomeElementSource,
                          BedGraphGenomeElementSource, MicroarrayGenomeElementSource,
                          BigBedGenomeElementSource, VcfGenomeElementSource]

    if forPreProcessor:
        from gtrackcore.input.fileformats.WigGenomeElementSource import \
            HbWigGenomeElementSource
        from gtrackcore.input.fileformats.GtrackGenomeElementSource import \
            HbGzipGtrackGenomeElementSource, HbGtrackGenomeElementSource
        from gtrackcore.input.fileformats.BigWigGenomeElementSource import \
            BigWigGenomeElementSourceForPreproc
        allGESourceClasses += [HbWigGenomeElementSource, HbGzipGtrackGenomeElementSource,
                               HbGtrackGenomeElementSource,
                               BigWigGenomeElementSourceForPreproc]
    else:
        from gtrackcore.input.fileformats.WigGenomeElementSource import WigGenomeElementSource
        from gtrackcore.input.fileformats.GtrackGenomeElementSource import \
            GzipGtrackGenomeElementSource, GtrackGenomeElementSource
        from gtrackcore.input.fileformats.BigWigGenomeElementSource import \
            BigWigGenomeElementSource

        allGESourceClasses += [WigGenomeElementSource, GzipGtrackGenomeElementSource,
                               GtrackGenomeElementSource, BigWigGenomeElementSource]

    return allGESourceClasses

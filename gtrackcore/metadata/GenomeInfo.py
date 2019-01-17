#import os
#from config.Config import METADATA_FILES_PATH, IS_EXPERIMENTAL_INSTALLATION
from gtrackcore.util.CustomExceptions import ArgumentValueError #, NotSupportedError
#from gtrackcore.util.CommonFunctions import strWithStdFormatting
#from third_party.roman import fromRoman
#from gtrackcore.result.HtmlCore import HtmlCore
#from collections import defaultdict
#import third_party.safeshelve as safeshelve
#import copy
#
#SHELVE_FN = METADATA_FILES_PATH + os.sep + 'GenomeInfo.shelve'
#
##class GenomeTools
class GenomeInfo(object):
#    _chrLengths = {}
#    _genomeChrLists = {}
#    _genomeExtChrLists = {}
#    _chrArmRegs = {}
#    _chrRegs = {}
#    _containingChrArms = {}
#    _chrMap = {'MT': 'chrM', 'chrMT': 'chrM', '23': 'chrX', 'chr23': 'chrX'}
#    _chrMatches = defaultdict(dict)
#    
#    def __new__(cls, genome=None):
#        if genome is None:
#            return object.__new__(cls)
#        
#        genomeInfoShelve = safeshelve.open(SHELVE_FN)
#        stored = genomeInfoShelve.get(genome)
#        genomeInfoShelve.close()
#        if stored is not None:
#            return stored
#        else:
#            return object.__new__(cls)
#    
#    def __init__(self, genome=None):
#        if genome is None:
#            return
#        
#        existingAttrs = copy.copy(self.__dict__)
#        assert existingAttrs.get('genome') in [None, genome], '%s not in [None, %s]' % (existingAttrs.get('genome'), genome)
#        
#        self.genome = genome
#        self.fullName = ''
#        self.sourceUrls = []
#        self.sourceChrNames = []
#        self.installedBy = ''
#        self.genomeBuildSource = ''
#        self.genomeBuildName = ''
#        self.species = ''
#        self.speciesTaxonomyUrl = ''
#        self.assemblyDetails = ''
#        self.ucscClade = ''
#        self.ucscGenome = ''
#        self.ucscAssembly = ''
#        self.isPrivate = False
#        self.privateAccessList = []
#        self.isExperimental = True
#        self.timeOfInstallation = None
#        
#        self.__dict__.update(existingAttrs)
#        self._calcAndStoreChrInfo()
#        
#    def _calcAndStoreChrInfo(self):
#        try:
#            dirty = False
#            
#            if not hasattr(self, 'numChrs'):
#                self.numChrs = len(GenomeInfo.getChrList(self.genome))
#                dirty = True
#                
#            if not hasattr(self, 'numExtChrs'):
#                self.numExtChrs = len(GenomeInfo.getExtendedChrList(self.genome)) - self.numChrs
#                dirty = True
#            
#            if not hasattr(self, 'numBps'):
#                chrs = GenomeInfo.getChrList(self.genome)
#                self.numBps = sum(GenomeInfo.getChrLen(self.genome, chr) for chr in chrs)
#                dirty = True
#            
#            if not hasattr(self, 'numBpsWithExt'):
#                extChrs = GenomeInfo.getExtendedChrList(self.genome)
#                self.numBpsWithExt = sum(GenomeInfo.getChrLen(self.genome, chr) for chr in extChrs) \
#                                     if self.numExtChrs > 0 else None
#                dirty = True
#                
#            if dirty:
#                self.store()
#        
#        except Exception, e:
#            if IS_EXPERIMENTAL_INSTALLATION:
#                from gtrackcore.application.LogSetup import logException, logMessage
#                logMessage('Exception for genome: %s' % self.genome)
#                logException(e)
#                import traceback
#                logMessage(''.join(traceback.format_stack()))
#    
#    def removeEntryFromShelve(self):
#        genomeInfoShelve = safeshelve.open(SHELVE_FN)
#        if self.genome in genomeInfoShelve:
#            del genomeInfoShelve[self.genome]
#        genomeInfoShelve.close()
#        
#    def store(self):
#        genomeInfoShelve = safeshelve.open(SHELVE_FN)
#        genomeInfoShelve[ self.genome ] = self
#        genomeInfoShelve.close()
#
#    def __str__(self):
#        return self.allInfo(printEmpty=True)
#        
#    def allInfo(self, printEmpty=False):
#        core = HtmlCore()
#        
#        if printEmpty or self.assemblyDetails:
#            core.descriptionLine('Assembly details', self.assemblyDetails)
#        
#        if printEmpty or hasattr(self, 'numChrs') and self.numChrs:
#            if hasattr(self, 'numExtChrs') and self.numExtChrs > 0:
#                core.descriptionLine('Number of standard chromosomes', strWithStdFormatting(self.numChrs))
#            else:
#                core.descriptionLine('Number of chromosomes', strWithStdFormatting(self.numChrs))            
#        
#        if printEmpty or hasattr(self, 'numExtChrs') and self.numExtChrs:
#            core.descriptionLine('Number of extended chromosomes', strWithStdFormatting(self.numExtChrs))
#        
#        if printEmpty or hasattr(self, 'numBps') and self.numBps:
#            if hasattr(self, 'numExtChrs') and self.numExtChrs > 0:
#                core.descriptionLine('Total number of bps (standard chromosomes only)', strWithStdFormatting(self.numBps))
#            else:
#                core.descriptionLine('Total number of bps', strWithStdFormatting(self.numBps))
#        
#        if printEmpty or hasattr(self, 'numBpsWithExt') and hasattr(self, 'numExtChrs') and self.numBpsWithExt and self.numExtChrs:
#            core.descriptionLine('Total number of bps (with extended chromosomes)', strWithStdFormatting(self.numBpsWithExt))
#        
#        return self.mainInfo(printEmpty) + str(core)
#
#    def mainInfo(self, printEmpty=False):
#        core = HtmlCore()
#        if printEmpty or self.species:
#            core.descriptionLine('Species', str(HtmlCore().link(self.species, self.speciesTaxonomyUrl)))
#        if printEmpty or self.genomeBuildName:
#            core.descriptionLine('Genome build', self.genomeBuildName + \
#                                 (' (%s)' % self.genomeBuildSource if self.genomeBuildSource else ''))
#        
#        core.descriptionLine('Short name', self.genome)
#        return str(core)
#    
#    @classmethod
#    def fixChr(cls, chr):
#        if chr in cls._chrMap:
#            return cls._chrMap[chr]
#        else:
#            try:
#                return 'chr' + str(fromRoman(chr))
#            except:
#                if chr.find('chr') > 0:
#                    return chr[chr.find('chr'):]
#                else:
#                    return chr
#
#    def isInstalled(self):
#        from gtrackcore.util.CommonFunctions import createDirPath
#        from gtrackcore.application.ProcTrackOptions import ProcTrackOptions
#        return self.timeOfInstallation is not None and \
#            ProcTrackOptions.isValidTrack(self.genome, GenomeInfo.getChrTrackName(self.genome), fullAccess=True) and \
#            ProcTrackOptions.isValidTrack(self.genome, GenomeInfo.getAssemblyGapsTrackName(self.genome), fullAccess=True)
#
#    def hasOrigFiles(self):
#        from gtrackcore.util.CommonFunctions import createOrigPath
#        return os.path.exists(createOrigPath(self.genome, []))
    
    @classmethod
    def getExtendedChrList(cls, genome):
        "Returns a list of all chromosomes of the genome build file set."
        if genome.name.lower() in ['testgenome']:
            return ['chr21', 'chrM']
        else:
            return genome.getChromosomeNameList()

    @classmethod
    def getChrList(cls, genome):
        '''
        Returns a list of all standard chromosomes of the genome build, e.g.
        chromosomes that are usually used in analyses. (For human, this includes
        chr1-chr22, chrX, and chrY, but not chrM).
        '''
        return cls.getExtendedChrList(genome)


#        else:
#            chrListFn = cls.getChrRegsFn(genome)
#            if chrListFn is None:
#                return []
#            assert chrListFn is not None and os.path.exists(chrListFn), 'did not find file with chr-names: '+str(chrListFn)
#            chrList = [line.split()[3].strip() for line in open(chrListFn,'U')]
#        #if genome.lower() in ['ncbi36','hg18']:
#        #    chrList = ["chr"+str(i) for i in range(1,23)] + ["chrX" , "chrY"]
#        #elif genome.lower() in ['testgenome']:
#        #    chrList = ['chr21', 'chrM']
#        #else:
#        #    chrList = [fn.replace('.fa','') for fn in os.listdir( os.sep.join([ORIG_DATA_PATH,genome,'sequence']) ) if fn.endswith('.fa')]
#            #raise NotSupportedError()
#        cls._genomeChrLists[genome] = chrList
#        return chrList
#
        
    @classmethod
    def getStdChrRegionList(cls, genome):
        from gtrackcore.track.core.GenomeRegion import GenomeRegion
        return [GenomeRegion(genome, chr, 0, cls.getChrLen(genome, chr))
                for chr in cls.getChrList(genome)]
    
    @classmethod
    def getStdChrLengthDict(cls, genome):
        result = dict()
        for chrom in cls.getChrList(genome):
            result[chrom] = cls.getChrLen(genome, chrom)
        return result

    @classmethod
    def isValidChr(cls, genome, chrName):
        return chrName in genome.getChromosomeNameList()

#        # Removed this, as chromosome mismatch now only displays a warning:
#        #
#        #return chr in cls.getExtendedChrList(genome) or \
#        #    (chr.lower() in [x.lower() for x in cls.getExtendedChrList(genome)] and not chr in cls.getChrList(genome)) #allow case mismatch as long as it is an ignored chromosome anyway
#    @staticmethod
#    def getNumElementsInFastaFile(fn):
#        f = open(fn)
#        headerLine = f.readline()
#        assert '\r' not in headerLine #check that the file does not use double newlines (\r\n)
#        
#        headerLen = len( headerLine )
#        lineLen = len( f.readline() ) #assumes all consecutive lines of same max length
#        byteLen = os.path.getsize(fn)
#        byteLen -= headerLen
#        f.seek(-1,2)
#        if f.read(1) == os.linesep:
#            byteLen -= 1 #last newline char.
#        return int(byteLen - (byteLen / lineLen)*len(os.linesep)) #subtract number of newline chars.. 
#        
    @classmethod
    def getChrLen(cls, genome, chrName):
        assert genome is not None
        assert chr is not None
        # For the unit-tests
        if genome.name.lower() == 'testgenome':
            if chr == 'chr21':
                return 46944323
            if chr == 'chrM':
                return 16571
            else:
                raise ArgumentValueError("Error: chromosome '%s' is not part of genome '%s'." % (chr, genome))
        else:
            for region in genome.regions:
                if region.chr == chrName:
                    return len(region)

#        if genome in cls._chrLengths and \
#            chr in cls._chrLengths[genome]:
#            return cls._chrLengths[genome][chr]
#        else:
#            try:
#                #length = cls.getNumElementsInFastaFile(os.sep.join([ORIG_DATA_PATH, genome, 'sequence', cls.fixChr(chr) + '.fa']))
#                from gtrackcore.util.CommonFunctions import createOrigPath
#                length = cls.getNumElementsInFastaFile(createOrigPath(genome, cls.getSequenceTrackName(genome), chr + '.fa'))
#            except IOError:
#                raise ArgumentValueError("Error: chromosome '%s' is not part of genome '%s'." % (chr, genome))
#
#            if not genome in cls._chrLengths:
#                cls._chrLengths[genome] = {}
#            cls._chrLengths[genome][chr] = length
#            return length
#
#        #if genome in cls._chrLengths and \
#        #    chr in cls._chrLengths[genome]:
#        #    return cls._chrLengths[genome][chr]
#        #else:
#        #    try:
#        #        regs = cls.getChrRegs(genome,[chr])
#        #        assert len(regs)==1
#        #        length = regs[0].end
#        #    except:
#        #        try:
#        #            length = cls.getNumElementsInFastaFile(os.sep.join([ORIG_DATA_PATH, genome, 'sequence', chr + '.fa']))
#        #        except Exception, e:
#        #            print "Unable to open sequence file for chromosome '" + chr + "'. Format should be either ('chr1', 'chr2'...) or ('chrX','chrY','chrM')."
#        #            raise
#        #
#        #    if not genome in cls._chrLengths:
#        #        cls._chrLengths[genome] = {}
#        #    cls._chrLengths[genome][chr] = length
#        #    return length
#        
#    @staticmethod
#    def getPropertyTrackName(genome, propertyName):
#        propertyName = propertyName.lower()
#        if propertyName in ['chrs', 'chrarms', 'chrbands', 'gaps']:
#            propertyTNDict = {'chrs': 'Chromosomes',
#                              'chrbands': 'Cytobands',
#                              'chrarms': 'Chromosome arms',
#                              'gaps': 'Assembly gaps'}
##            if genome in ['hg18','hg18','TestGenome','pombe2007']:
#            prefixTN = ['Genome build properties']
##            else:
##                prefixTN = ['Mapping and Sequencing Tracks']
#            return prefixTN + [ propertyTNDict[propertyName] ]
#        elif propertyName == 'ensembl':
##            if genome in ['hg18','hg18','pombe2007']:
#            prefixTN = ['Genes and gene subsets','Genes']
##            else:
##                prefixTN = ['Genes and Gene Prediction Tracks','Genes']
#            return prefixTN + ['Ensembl']
#        elif propertyName == 'nmer':
##            if genome in ['hg18','hg18','pombe2007']:
#            prefixTN = ['Sequence']
##            else:
##                prefixTN = ['Mapping And Sequencing Tracks']
#            return prefixTN + ['Nmers']
#        elif propertyName == 'protein':
#            return prefixTN + ['Proteins']
#        elif propertyName == 'literature':
#            return ['Genes and gene subsets','Gene subsets','Literature-derived']
#        elif propertyName == 'sequence':
#            return ['Sequence','DNA']
#        elif propertyName == 'encode':
#            return ['Genome build properties','ENCODE regions']
#        
#    @staticmethod
#    def getChrTrackName(genome):
#        return GenomeInfo.getPropertyTrackName(genome, 'chrs')
#
#    @staticmethod
#    def getCytobandsTrackName(genome):
#        return GenomeInfo.getPropertyTrackName(genome, 'chrbands')
#
#    @staticmethod
#    def getChrArmsTrackName(genome):
#        return GenomeInfo.getPropertyTrackName(genome, 'chrarms')
#
#    @staticmethod
#    def getAssemblyGapsTrackName(genome):
#        return GenomeInfo.getPropertyTrackName(genome, 'gaps')
#
#    @staticmethod
#    def getEnsemblTrackName(genome):
#        return GenomeInfo.getPropertyTrackName(genome, 'ensembl')
#        
#    @staticmethod
#    def getProteinTrackName(genome):
#        return GenomeInfo.getPropertyTrackName(genome, 'protein')
#
#    @staticmethod
#    def getNmerTrackName(genome):
#        return GenomeInfo.getPropertyTrackName(genome, 'nmer')
#
#    @staticmethod
#    def getLiteratureTrackName(genome):
#        return GenomeInfo.getPropertyTrackName(genome, 'literature')
#
#    @staticmethod
#    def getSequenceTrackName(genome):
#        return GenomeInfo.getPropertyTrackName(genome, 'sequence')
#
#    @staticmethod
#    def getEncodeTrackName(genome):
#        return GenomeInfo.getPropertyTrackName(genome, 'encode')
#
#    @staticmethod
#    def getChrRegsFn(genome):
#        from gtrackcore.util.CommonFunctions import getOrigFn
#        return getOrigFn(genome, GenomeInfo.getChrTrackName(genome), '.category.bed')
#        
#    @classmethod
#    def getChrRegs(cls, genome, categoryFilterList = None):
#        if not genome in cls._chrRegs:
#            from gtrackcore.util.CommonFunctions import createOrigPath
#            #from gtrackcore.application.UserBinSource import UnfilteredUserBinSource
#            from gtrackcore.application.UserBinSource import ValuesStrippedUserBinSource
#            fn = cls.getChrRegsFn(genome)
#            if fn is not None and os.path.exists(fn):
#                cls._chrRegs[genome] = ValuesStrippedUserBinSource('file', fn, genome, categoryFilterList)
#            else:
#                cls._chrRegs[genome] =  None
#        return cls._chrRegs[genome]
#
#    @staticmethod
#    def getChrArmRegsFn(genome):
#        from gtrackcore.util.CommonFunctions import getOrigFn
#        return getOrigFn(genome, GenomeInfo.getChrArmsTrackName(genome), '.category.bed')
#    
#    @classmethod
#    def getChrArmRegs(cls, genome, categoryFilterList = None):
#        if not genome in cls._chrArmRegs:                    
#            from gtrackcore.util.CommonFunctions import createOrigPath
#            from gtrackcore.application.UserBinSource import UserBinSource
#            fn = cls.getChrArmRegsFn(genome)
#            if fn is not None and os.path.exists(fn):    
#                cls._chrArmRegs[genome] = UserBinSource('file', fn, genome, categoryFilterList)
#            else:
#                cls._chrArmRegs[genome] = None
#        return cls._chrArmRegs[genome]
#    
#    @classmethod
#    def getStdGeneRegsTn(cls, genome):
#        return cls.getEnsemblTrackName(genome)
#    
#    @classmethod
#    def getStdGeneRegsFn(cls, genome):
#        from gtrackcore.util.CommonFunctions import getOrigFn
#        return getOrigFn(genome, cls.getStdGeneRegsTn(genome), '.category.bed')
#    
#    @classmethod
#    def getStdGeneRegs(cls, genome, categoryFilterList = None, cluster = True):
#        fn = cls.getStdGeneRegsFn(genome)
#        return cls.getGeneRegs(genome, fn, categoryFilterList, cluster)
#        
#    @classmethod
#    def getGeneRegs(cls, genome, fn, categoryFilterList = None, cluster = True):
#        if fn is not None and os.path.exists(fn):
#            if cluster:
#                from gtrackcore.application.UserBinSource import UserBinSource
#                return UserBinSource('file',fn, genome, categoryFilterList)
#            else:
#                from gtrackcore.application.UserBinSource import UnBoundedUnClusteredUserBinSource
#                return UnBoundedUnClusteredUserBinSource('file',fn, genome, categoryFilterList)
#        else:
#            return None
#    
#    @staticmethod
#    def getChrBandRegsFn(genome):
#        from gtrackcore.util.CommonFunctions import getOrigFn
#        return getOrigFn(genome, GenomeInfo.getCytobandsTrackName(genome), '.category.bed')
#    
#    @staticmethod
#    def getEncodeRegsFn(genome):
#        from gtrackcore.util.CommonFunctions import getOrigFn
#        return getOrigFn(genome, GenomeInfo.getEncodeTrackName(genome), '.category.bed')
#    
#    @classmethod
#    def getEncodeRegs(cls, genome, categoryFilterList = None, cluster = True):
#        fn = cls.getEncodeRegsFn(genome)
#        return cls.getGeneRegs(genome, fn, categoryFilterList, cluster)
#    
#    @classmethod
#    def getChrBandRegs(cls, genome, categoryFilterList = None):        
#        from gtrackcore.application.UserBinSource import UserBinSource
#        fn = cls.getChrBandRegsFn(genome)
#        if fn is not None and os.path.exists(fn):
#            return UserBinSource('file',fn, genome, categoryFilterList, strictMatch=False)
#        else:
#            return None
#    
#    @staticmethod
#    def getProteinRegsFn(genome):
#        from gtrackcore.util.CommonFunctions import getOrigFn
#        return getOrigFn(genome, GenomeInfo.getProteinTrackName(genome), '.category.bed')
#    
#    @classmethod
#    def getProteinRegs(cls, genome, categoryFilterList = None, cluster = True):
#        fn = cls.getProteinRegsFn(genome)
#        return cls.getGeneRegs(genome, fn, categoryFilterList, cluster)
#    
#    @classmethod
#    def getContainingChrArms(cls, region):
#        if not region in cls._containingChrArms:
#            cls._containingChrArms[region] = [arm for arm in cls.getChrArmRegs(region.genome) if arm.overlaps(region)]
#        return cls._containingChrArms[region]
#            
    @classmethod
    def regIntersectsCentromer(cls, region):
        return False
#        
#    @classmethod
#    def findBestMatchingChr(cls, genome, chrStr):
#        if chrStr not in cls._chrMatches[genome]:
#            matchingChr = cls._findBestMatchingChr(genome, chrStr)
#            cls._chrMatches[genome][chrStr] = matchingChr
#        
#        return cls._chrMatches[genome][chrStr]
#    
#    @classmethod
#    def _findBestMatchingChr(cls, genome, chrStr):
#        if chrStr in cls._chrMap:
#            chrStr = cls._chrMap[chrStr]
#    
#        chrList = cls.getExtendedChrList(genome)
#        lowerChrList = [(chr, chr.lower()) for chr in chrList]
#        lowerChrStr = chrStr.lower()
#        
#        for chr, lowerChr in lowerChrList:
#            if lowerChrList == lowerChr:
#                return chr
#                        
#        for curChrStr, curChrList in [(chrStr, [(chr,chr) for chr in chrList]), \
#                                       (lowerChrStr, lowerChrList), \
#                                        (cls._convertRomanNumbersInStr(chrStr), lowerChrList), \
#                                         (chrStr, [(chr, cls._convertRomanNumbersInStr(chr)) for chr in chrList])]:
#            
#            chrCandidates = [chr for chr, changedChr in curChrList if curChrStr in changedChr]
#
#            if len(chrCandidates) == 1:
#                return chrCandidates[0]
#
#            elif len(chrCandidates) > 1:
#                chrCandidates = [cand for cand in chrCandidates if not any(x.isdigit() for x in cand.replace(curChrStr,''))]
#
#                if len(chrCandidates) == 1:
#                    return chrCandidates[0]
#                    
#                elif len(chrCandidates) > 1:
#                    import numpy as np
#                    min_i = np.array([len(x) for x in chrCandidates]).argmin()
#                    if all(chrCandidates[min_i] in chr for chr in chrCandidates):
#                        return chrCandidates[min_i]
#                    else:
#                        return chrStr
#        return chrStr
#    
#    @classmethod
#    def _convertRomanNumbersInStr(cls, inStr):
#        from third_party.roman import fromRoman
#        import re
#        
#        romanStr = ''.join(re.findall('[IVXLCDM]', inStr))
#        if len(romanStr) > 0:
#            i = inStr.find(romanStr)                            
#            if i >= 0:
#                return inStr[:i] + str(fromRoman(romanStr)) + inStr[i+len(romanStr):]
#        
#        return inStr

##TODO: this is still here because it is used in some tests - move it somewhere else later!
GENOMES = {
    "hg18": {
        "name":"HG18",
        "size": {
            "chr1":    247249719,
            "chr2":    242951149,
            "chr3":    199501827,
            "chr4":    191273063,
            "chr5":    180857866,
            "chr6":    170899992,
            "chr7":    158821424,
            "chr8":    146274826,
            "chr9":    140273252,
            "chr10":   135374737,
            "chr11":   134452384,
            "chr12":   132349534,
            "chr13":   114142980,
            "chr14":   106368585,
            "chr15":   100338915,
            "chr16":   88827254,
            "chr17":   78774742,
            "chr18":   76117153,
            "chr19":   63811651,
            "chr20":   62435964,
            "chr21":   46944323,
            "chr22":   49691432,
            "chrX":    154913754,
            "chrY":    57772954,
            "chrM":    16571
        },
    },
    "hg19": {
        "name":"HG19",
        "size": {
            "chr1":    249250621,
            "chr2":    243199373,
            "chr3":    198022430,
            "chr4":    191154276,
            "chr5":    180915260,
            "chr6":    171115067,
            "chr7":    159138663,
            "chr8":    146364022,
            "chr9":    141213431,
            "chr10":   135534747,
            "chr11":   135006516,
            "chr12":   133851895,
            "chr13":   115169878,
            "chr14":   107349540,
            "chr15":   102531392,
            "chr16":   90354753,
            "chr17":   81195210,
            "chr18":   78077248,
            "chr19":   59128983,
            "chr20":   63025520,
            "chr21":   48129895,
            "chr22":   51304566,
            "chrX":    155270560,
            "chrY":    59373566,
            "chrM":    16571
        },
        "code": {
            "chr1":    0,
            "chr2":    1,
            "chr3":    2,
            "chr4":    3,
            "chr5":    4,
            "chr6":    5,
            "chr7":    6,
            "chr8":    7,
            "chr9":    8,
            "chr10":   9,
            "chr11":   10,
            "chr12":   11,
            "chr13":   12,
            "chr14":   13,
            "chr15":   14,
            "chr16":   15,
            "chr17":   16,
            "chr18":   17,
            "chr19":   18,
            "chr20":   19,
            "chr21":   21,
            "chr22":   22,
            "chrX":    23,
            "chrY":    24,
            "chrM":    25
        }
    }
}
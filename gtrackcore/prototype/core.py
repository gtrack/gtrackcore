import numpy as np

from tables import UInt8Col, UInt32Col #@UnresolvedImport
from tables import openFile, IsDescription, Atom
from tables.exceptions import NoSuchNodeError

class gtrackcore(object):
    
    gtrackcore_VERSION = 1
    
    NODE_DTYPE = np.dtype([("seqid", "uint8"), ("left", "uint32"), ("right", "uint32")])
    LINK_DTYPE = np.dtype([("source", "uint32"), ("target", "uint32")])
    
    class _Nodes(IsDescription):
        seqid = UInt8Col()
        start = UInt32Col()
        stop = UInt32Col()

    class _Links(IsDescription):
        source = UInt32Col()
        target = UInt32Col()    
    
    # statics
    ROOT = "/"
    NODES = "nodes"
    NODE_VALS = "node_values"
    LINKS = "links"
    LINK_VALS = "link_values"
    
    @staticmethod 
    def _get(attrs, key, **kwargs):
        try:
            return attrs[key]
        except KeyError, e:
            if "default" in kwargs:
                return kwargs["default"]
            else:
                raise e
     
    @classmethod
    def is_valid_gtrackcore(cls, h5):
        valid = True
        if not cls._get(h5.root._v_attrs, "gtrackcore", default=False):
            valid = False
        if cls._get(h5.root._v_attrs, "gtrackcore_version", default=None) != cls.gtrackcore_VERSION:
            valid = False
        if not cls._get(h5.root._v_attrs, "gtrackcore_consistent", default=False):
            valid = False
        if not (
                cls._get(h5.root._v_attrs, "gtrackcore_nodes_sealed", default=False)
                and 
                cls._get(h5.root._v_attrs, "gtrackcore_links_sealed", default=False)
                ):
            valid = False    
        genome = cls._get(h5.root._v_attrs, "gtrackcore_genome", default={})
        if not genome.get("name", ""):
            valid = False
        if not genome.get("size", {}):
            valid = False
        if not genome.get("code", {}):
            valid = False        
        return valid
        
    @classmethod
    def empty_track(cls, fn, genome, expectedrows=1000000, title="track"):
        """
        """
        h5 = openFile(fn, mode="w", title=title)
        # root attributes
        root = h5.getNode("/")
        root._v_attrs["gtrackcore"] = True
        root._v_attrs["gtrackcore_version"] = True
        root._v_attrs["gtrackcore_genome"] = genome
        root._v_attrs["gtrackcore_consistent"] = True
        root._v_attrs["gtrackcore_nodes_sealed"] = True
        root._v_attrs["gtrackcore_links_sealed"] = True
        # root groups and leaves
        h5.createGroup(cls.ROOT, cls.NODE_VALS, "data for nodes")
        h5.createGroup(cls.ROOT, cls.LINK_VALS, "data for links")
        h5.createTable(cls.ROOT, cls.NODES, cls._Nodes, expectedrows=expectedrows)
        h5.createTable(cls.ROOT, cls.LINKS, cls._Links, expectedrows=expectedrows)
        h5.flush()
        h5.close()
        return gtrackcore(fn, mode="r+")
    
    def __init__(self, fn, mode="r"):
        h5 = openFile(fn, mode=mode)
        if self.is_valid_gtrackcore(h5):
            self.h5 = h5
            self.attrs = self.h5.root._v_attrs
        else:
            raise ValueError("HDF5 file does not contain a valid Track")
        
    def _is_consistent(self):
        # TODO: write validation
        consistent = True
        for (X, X_VALS) in [(self.NODES, self.NODE_VALS), (self.LINKS, self.LINK_VALS)]:
            nnodes = self.h5.getNode(self.ROOT, X).nrows
            for values in self.h5.getNode(self.ROOT, X_VALS)._f_iterNodes():
                if len(values) != nnodes:
                    consistent = False
                    break
        return consistent

    def _is_writeable(self):
        # "r" is the only possible read-only mode
        return self.h5.mode != "r"
 
    def _is_sealed(self):
        return self.attrs["gtrackcore_nodes_sealed"] and self.attrs["gtrackcore_links_sealed"]
    
    def _seal_nodes(self):
        if not self.attrs["gtrackcore_nodes_sealed"]:
            self.attrs["gtrackcore_nodes_sealed"] = True
        else:
            raise ValueError("Track nodes already sealed")
    
    def _unseal_nodes(self):
        if self.attrs["gtrackcore_nodes_sealed"]:
            if self._is_writeable():
                self.attrs["gtrackcore_nodes_sealed"] = False
            else:
                raise ValueError("Track is not writeable")
        else:
            raise ValueError("Track nodes are not sealed")
         
    def _seal_links(self):
        if not self.attrs["gtrackcore_links_sealed"]:
            self.attrs["gtrackcore_links_sealed"] = True
        else:
            raise ValueError("Track links already sealed") 

    def _unseal_links(self):
        if self.attrs["gtrackcore_links_sealed"]:
            if self._is_writeable():
                self.attrs["gtrackcore_links_sealed"] = False
            else:
                raise ValueError("Track is not writeable")
        else:
            raise ValueError("Track links are not sealed")
    
    def flush(self):
        self.h5.flush()
          
    def seal(self):
        if self._is_consistent():
            self._seal_nodes()
            self._seal_links()        
        else:
            raise ValueError("Track is not consistent and cannot be sealed")

    def unseal(self):
        self._unseal_nodes()
        self._unseal_links()
        
    def add_nodes(self, nodes):
        if not self.attrs["gtrackcore_nodes_sealed"]:
            all_nodes = self.h5.getNode(self.ROOT, self.NODES)
            all_nodes.append(nodes)
        else:
            raise ValueError("Track nodes are sealed") 

    def add_links(self, links):
        if not self.attrs["gtrackcore_nodes_sealed"]:
            all_links = self.h5.getNode(self.ROOT, self.LINKS)
            all_links.append(links)
        else:
            raise ValueError("Track links are sealed")

    def _add_earray(self, root, name, dtype, shape, **kwargs):
        atom = Atom.from_dtype(np.dtype(dtype))        
        earr = self.h5.createEArray(root, name, atom, shape, **kwargs)
        return earr

    def add_node_values(self, name, dtype="f", shape=(0,), **kwargs):
        if self.attrs["gtrackcore_nodes_sealed"]:
            raise ValueError("Track nodes are sealed")
        earr = self._add_earray("/node_values", name, dtype, shape, **kwargs)
        return earr
    
    def add_link_values(self, name, dtype="f", shape=(0,), **kwargs):
        if self.attrs["gtrackcore_links_sealed"]:
            raise ValueError("Track links are not sealed")
        earr = self._add_earray("/link_values", name, dtype, shape, **kwargs)
        return earr

    def __len__(self):
        if self._is_sealed():
            return len(self.h5.getNode(self.ROOT, self.NODES))
        else:
            raise ValueError("Track is not sealed")
    
    def __iter__(self):
        if self._is_sealed():
            for row in self.h5.getNode(self.ROOT, self.NODES):
                sss = row.fetch_all_fields() # seqid, start, stop
                yield sss
        else:
            raise ValueError("Track is not sealed")
         
    def __getitem__(self, idx):
        nodes = self.h5.getNode(self.ROOT, self.NODES)
        return nodes.__getitem__(idx)
    
    def get_node_values(self, key):
        if self._is_sealed():
            try:
                return self.h5.getNode(self.ROOT, self.NODE_VALS + "/" + key)
            except NoSuchNodeError:
                raise KeyError()
        else:
            raise ValueError("Track is not sealed")
            
        
        
              
    def close(self):
        if not self._is_sealed():
            self.seal()
        self.h5.flush()
        self.h5.close()

GENOMES = {
           "HG19": {
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
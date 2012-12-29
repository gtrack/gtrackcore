from prototype.core import Track5, GENOMES

def _strconv(x, genome):
    return str(x)

def _intconv(x, genome):
    return int(x)

def _numconv(x, genome):
    fx = float(x)
    ix = int(fx)
    if fx == ix:
        return ix
    else:
        return fx

def _allconv(x, genome):
    try:
        return _numconv(x, genome)
    except:
        return _strconv(x, genome)

def _codeconv(x, genome):
    return genome["code"][x]

BEDGRAPH_COLS = ((0, "seqid", _codeconv, "s"), 
                 (1, "left", _intconv, "i"), 
                 (2, "right", _intconv, "i"),
                 (3, "data", _allconv, "f"))

def tab_parser_converter(fh, parsecols, genome):
    """Generator splits tab-delimited lines into fields.
    """
    for line in fh:
        line = line.strip()
        if not line or line.startswith(('#', "track")):
            continue
        allfields = line.split('\t')
        fields = []
        for col, name, conv, _ in parsecols:
            field = allfields[col]
            fields.append(conv(field, genome))
        yield fields
        
def tab_loader(inputfn, trackfn, genome, parsecols, expectedrows):
    buffersize = int(expectedrows / 100)
    # element
    seqid_col = [col for (col, name, _, _) in parsecols if name == "seqid"][0]
    left_col  = [col for (col, name, _, _) in parsecols if name == "left"][0]
    right_col = [col for (col, name, _, _) in parsecols if name == "right"][0]
    # data(s)
    for (col, name, _, typ) in parsecols:
        dtype = []
        data_cols = []
        if name not in ("seqid", "left", "right"):
            dtype.append(typ)
            data_cols.append(col)
    #
    title = trackfn.split(".")[0]
    track = Track5.empty_track(trackfn, genome, expectedrows, title)    
    #
    track.unseal()    
    arr = track.add_node_values(name, ",".join(dtype))
    with open(inputfn) as rh:
        nodes = []
        datas = []
        for i, fields in enumerate(tab_parser_converter(rh, parsecols, genome)):
            node = (fields[seqid_col], fields[left_col], fields[right_col])
            nodes.append(node)
            data = tuple([fields[data_col] for data_col in data_cols])
            datas.append(data[0] if len (data) == 1 else data)
            if ((i + 1) % buffersize) == 0:
                track.add_nodes(nodes)
                arr.append(datas)
                track.flush()
                nodes, datas = [], []
        if nodes:
            track.add_nodes(nodes)
            arr.append(datas)
    track.flush()
    track.seal()
    return track


def load_bedgraph(inputfn, trackfn="data", genome_name="HG19", expectedrows=500):
    genome = GENOMES[genome_name]
    track = tab_loader(inputfn, trackfn, genome, BEDGRAPH_COLS, expectedrows)
    return track






#def valid_bedgraph(lines):
#    header = lines.next()
#    return header.startswith("track type=bedGraph")
#
#def parse_bedgraph(bedfn, trackfn, expectedrows=10000000, title=""):
#    with open(bedfn) as fh:
#        if not valid_bedgraph(fh):
#            raise ValueError("Not a valid BedGraph stream")
#        # Track 
#        track = Track5.empty_track(trackfn, expectedrows, title)
#        node_buffer = 
#        value_buffer = 
#        # wendy golden
#    # contents
#    
#    
#    for i, line in enumerate(lines):
#        
#    
#    def parse_nodes(self, lines, parser, buffer_size=10000):
#        # allocate new buffer
#        if self.is_sealed():
#            raise ValueError("Track is sealed")
#
#        buffer = self.get_node_buffer(buffer_size)
#        for line in lines:
#            parser.consume(line)
#            if parser.has_produce():
#                
#            
#            if parser.has_node():
#                parser.procuce(buffer)
#                
#            
#            # will the result fit
#            if (i + 1) % buffer_size:
#                #
#


#
#
#
#
## Generate some data
#x = np.random.random((100,100,100))
#print x[0,0,0]
#
## Store "x" in a chunked array with level 5 BLOSC compression...
#f = tables.openFile('test.hdf', 'w')
#atom = tables.Atom.from_dtype(x.dtype)
#
#filters = tables.Filters(complib='blosc', complevel=5)
#ds[:] = x
#f.close()
#del f
#
#f = h5py.File("test.hdf", "r+")
#print f["t"].compression
#f["t"][0,0,0] = 1.0
#print f["t"][0,0,0]
#print "z"
#f.create_dataset("h", (100,100,100), dtype="f", compression="gzip")
#print "y"
#f["h"][:,:,:] = np.random.random((100,100,100))
#print f["h"][0,0,0]
#print "x"
#f.close()
#del f
#print "xxx"
#f = tables.openFile('test.hdf', 'r+')
#print "xxx"
#h = f.getNode("/", "h")
#t = f.getNode("/", "t")
#print h[0,0,0]
#print t[0,0,0]


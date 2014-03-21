class Edge(object):
    def __init__(self, fromNode, toNode, weight=None, directed=True):
        self.fromNode = fromNode
        self.toNode = toNode
        self.weight = weight
        self.directed = directed
        
    def __eq__(self, other):
        return hash(self) == hash(other)

    #def setUndirected(self):
    #    self.directed = False
    
    def __repr__(self):
        return "%s->%s (%s)" % (self.fromNode, self.toNode, self.weight)
            
    def __hash__(self):
        if self.directed:
            return hash(( hash(self.fromNode), hash(self.toNode), hash(self.weight) ))
        else:        
            return hash(( sorted(( hash(self.fromNode), hash(self.toNode))), hash(self.weight) ))
        
#e = Edge(node1,node2)
#e2 = Edge(node2,node1)
#a[e]=True
#e2 in a

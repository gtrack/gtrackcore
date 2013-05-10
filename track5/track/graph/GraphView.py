import numpy as np
from collections import OrderedDict
from copy import copy
from track5.graph.NodeElement import NodeElement
from track5.graph.Edge import Edge

class BaseGraphView(object):
    def __init__(self, trackViewDict, id2index, isDirected):
        'Typically called with the members of a graphview (typically protoGraphView) object as input, mainly only setting these same member variables'
        self._trackViewDict = trackViewDict
        self._id2index = id2index
        self._id2nodes = {}
        self._isDirected = isDirected
        
class GraphView(BaseGraphView):
    #def __init__(self, graphView,idFilter=None):    
    def hasNode(self, nodeId):
        return nodeId in self._id2index
    
    def filterNodes(self, idFilter):
        if idFilter != None:
            self._id2index = {id:self._id2index[id] for id in idFilter} 
            self._id2nodes = {id:self._id2nodes[id] for id in idFilter if id in self._id2nodes}
            
    def getNewSubGraphFromNodeIdSet(self, nodeIds):
        'Returns a GraphView object corresponding to the nodes provided in nodeIds, with edges between these ndoes'
        subGraph = GraphView(self._trackViewDict, self._id2index, self._isDirected)
        subGraph.filterNodes(nodeIds)
        return subGraph

    def getRandomNode(self):
        from track5.util.RandomUtil import random
        index = random.randint(0, len(self._id2index))
        return self.getNode( self._id2index.keys()[index])
        
    def getNode(self, id):
        if not id in self._id2nodes:
            reg,pos = self._id2index[id]
            #te = TrackElement(self._trackViewDict[reg],index=pos)            
            self._id2nodes[id] = NodeElement(self._trackViewDict[reg], pos, self)
        return self._id2nodes[id]
           
    def getNodeIter(self):
        for id in self._id2index:
            yield self.getNode(id)
    
    def getEdgeIter(self):
        for node in self.getNodeIter():
            for neighbor in node.getNeighborIter():
                #if hash(node) == hash(neighbor.node):
                #    assert node == neighbor.node
                #    
                #if hash(node)<=hash(neighbor.node):
                #    yield Edge(node, neighbor.node, neighbor.weight) 

                if self.isDirected() or node.id() <= neighbor.toNode.id():
                    yield Edge(node, neighbor.toNode, neighbor.weight, self.isDirected())
                   
    def isDirected(self):
        return self._isDirected
    
    def resetColoring(self):
        for node in self.getNodeIter():
            node.color = None
        

    def _commonGetMatrixRepresentation(self, completeMatrix, rowsAsFromNodes, hasWeights, missingEdgeWeight):
        if completeMatrix:
            rows = np.unique( np.array([(edge.fromNode.id(), edge.toNode.id()) for edge in self.getEdgeIter()], dtype='S').flatten() )
            cols = copy(rows)
        else:
            rows = np.unique( np.array([edge.fromNode.id() for edge in self.getEdgeIter()], dtype='S') )
            cols = np.unique( np.array([edge.toNode.id() for edge in self.getEdgeIter()], dtype='S') )
            if not rowsAsFromNodes:
                rows, cols = cols, rows
        
        shape=(len(rows),len(cols)) if len(rows) > 0 and len(cols) > 0 else (0,)
        matrix = np.zeros(shape=shape, dtype='float64' if hasWeights else 'bool8')
        if missingEdgeWeight != 0:
            matrix[:] = missingEdgeWeight
        
        for edge in self.getEdgeIter():
            if rowsAsFromNodes:
                matrix[rows==edge.fromNode.id(), cols==edge.toNode.id()] = edge.weight if hasWeights else 1
            else:
                matrix[rows==edge.toNode.id(), cols==edge.fromNode.id()] = edge.weight if hasWeights else 1
        return OrderedDict([('Matrix', matrix), ('Rows', rows), ('Cols', cols)])

        
    def getBinaryMatrixRepresentation(self, completeMatrix=False, rowsAsFromNodes=True):
        '''
        Computes a boolean matrix representation of the graph, where i,j is True if there is an edge between node i and node j.
        Returns this as a dict of two numpy arrays ('Rows' and 'Cols') and one numpy matrix ('Matrix').
        Rows and Cols contain the row and column names, respectively, while Matrix contains the binary
        matrix, where matrix[nodeIdi][nodeIdj] gives the value for i,j
        '''
        return self._commonGetMatrixRepresentation(completeMatrix, rowsAsFromNodes, hasWeights=False, missingEdgeWeight=0)
        
    def getEdgeWeightMatrixRepresentation(self, completeMatrix=False, rowsAsFromNodes=True, missingEdgeWeight=0):
        '''
        Computes a matrix representation of the weights of all edges of the graph, where i,j is the weight of an edge between node i and node j.
        Entries corresponding to lacking edges is filled in with missingEdgeWeight.
        Returns this as a dict of two numpy arrays ('Rows' and 'Cols') and one numpy matrix ('Matrix').
        'Rows' and 'Cols' contain the row and column names, respectively, while 'Matrix' contains the binary
        matrix, where matrix[nodeIdi][nodeIdj] gives the value for i,j
        '''
        return self._commonGetMatrixRepresentation(completeMatrix, rowsAsFromNodes, hasWeights=True, missingEdgeWeight=missingEdgeWeight)
            
class ProtoGraphView(BaseGraphView):            
    def getClosedGraphVersion(self):
        '''Simply returns a corresponding GraphView-objects, as this in a lazy fashion will
        apply a filter to NodeNeighbors, so that all neighbors outside the node set are filtered out'''
        return GraphView(self._trackViewDict, self._id2index, self._isDirected)
    

class LazyProtoGraphView(ProtoGraphView):
    @classmethod
    def createInstanceFromTrackView(cls, trackView, isDirected=True):
        gReg = trackView.genomeAnchor
        trackViewDict = {gReg:trackView}
        ids = trackView.idsAsNumpyArray()
        isDirected = isDirected #trackView.trackFormat.isDirectedGraph()
        
        #operate with mapping to tuples of tvId (GenomeRegion) and posId (position within tv)
        indexes = zip([gReg]*len(ids), range(len(ids)) )
        id2index = dict(zip(ids, indexes))
        return LazyProtoGraphView(trackViewDict, id2index, isDirected)
    
        #operate directly with simple lists        
        #self._id2nodeIndex = dict(zip(ids, xrange(len(ids)))) #the values of this dict indexes against the two following lists..
        #self._nodeIndex2tvNumber = [gReg]*xrange(len(ids))
        #self._nodeIndex2tvPos = xrange(len(ids))
                              

    @classmethod
    def mergeProtoGraphViews(cls, pgvList):
        #operate with mapping to tuples of tvId and posId
        mergedTrackViewDict = {}
        mergedId2index = {}
        mergedIsDirected = None
        for pgv in pgvList:
            mergedTrackViewDict.update(pgv._trackViewDict)
            mergedId2index.update(pgv._id2index)
            if mergedIsDirected is None:
                mergedIsDirected  = pgv._isDirected
            else:
                assert mergedIsDirected  == pgv._isDirected
                
        pgv = LazyProtoGraphView(mergedTrackViewDict, mergedId2index, mergedIsDirected)
        #operate directly with simple lists
        #mergedId2nodeIndex = {}
        #mergedTrackViewDict = []
        #mergedNodeIndex2tvNumber = []
        #mergedNodeIndex2tvPos = []
        #
        #for i,pgv in enumerate(pgvList):
        #    mergedId2nodeIndex = mergedId2nodeIndex.update(pgv._id2nodeIndex)
        #    mergedTrackViewDict += pgv._trackViewDict[0]
        #    #mergedNodeIndex2tvNumber += [i]*xrange(len(ids))
        #    mergedNodeIndex2tvNumber += pgv._nodeIndex2tvNumber
        #    mergedNodeIndex2tvPos += pgv._nodeIndex2tvPos
        return pgv

#class ExplicitProtoGraphView(ProtoGraphView):
#    def __init__(self, trackView):
#        self._ids = trackView.getIdsAsNumpyArray()
#        self._protoNodes = [trackView.getProtoNodeElement(i) for i in len(trackView)]
#        
#        #not needed, as part of nodes..
#        #edges = trackView.getEdgesAsNumpyArray()
#        #weights = trackView.getWeightsAsNumpyArray()
#
#    @classmethod
#    def mergeProtoGraphViews(cls, pgvList):
#        pass

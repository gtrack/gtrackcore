import weakref

from gtrackcore.track.graph.Edge import Edge
from gtrackcore.track.core.TrackView import TrackElement, AutonomousTrackElement, noneFunc
from gtrackcore.track.pytables.database.Database import DatabaseReader
from gtrackcore.util.pytables.NameFunctions import get_database_filename, get_track_table_node_names


class NodeElement(TrackElement):
    'A track element that also includes references to its neighbors as other NodeElements'
    def __init__(self, trackView, index, graphView):
        TrackElement.__init__(self, trackView, index=index)
        if trackView._weightsList == None:
            self.weights = noneFunc
        # Weak proxy is used to remove memory leak caused by circular reference when GraphView is deleted
        self._graphView = weakref.proxy(graphView)
        self.color = None
        
    def getNeighborIter(self):
        'Allows iteration through neighbors in the form of Edge objects'
        edgeList = self.edges()
        weightList = self.weights()
        #numNeighbors = len(edgeList)
        
        for i, neighborId in enumerate(edgeList[edgeList != '']):          
            if self._graphView.hasNode(neighborId):
                toNode = self._graphView.getNode( neighborId )
                yield Edge(self, toNode, weightList[i] if (weightList is not None) else None, self._graphView.isDirected() )
    
    def __repr__(self):
        return self.id()
        
    def __hash__(self):
        return hash(self.id())
        
        
class PytablesNodeElement(object):
    'A track element that also includes references to its neighbors as other NodeElements'
    def __init__(self, track_view, index, graph_view):
        if track_view._weightsList is None:
            self._has_weights = False
        else:
            self._has_weights = True
        # Weak proxy is used to remove memory leak caused by circular reference when GraphView is deleted
        self._graph_view = weakref.proxy(graph_view)
        self.color = None

        genome = track_view.genomeAnchor.genome
        track_name = track_view._track_name
        allow_overlaps = track_view.allowOverlaps

        db_filename = get_database_filename(genome, track_name, allow_overlaps)
        db_reader = DatabaseReader(db_filename)
        table_node_names = get_track_table_node_names(genome, track_name, allow_overlaps)
        table = db_reader.get_table(table_node_names)

        # offset must be set to start of track_view since we work directly on the db.
        index = index + track_view.cached_start_and_end_indices[0]
        self._row = table[index]

    def getNeighborIter(self):
        'Allows iteration through neighbors in the form of Edge objects'
        edges = self._row['edges']
        weights = self._row['weights'] if self._has_weights else None
        #numNeighbors = len(edgeList)

        for i, neighbor_id in enumerate(edges[edges != '']):          
            if self._graph_view.hasNode(neighbor_id):
                to_node = self._graph_view.getNode(neighbor_id)
                yield Edge(self, to_node, weights[i] if weights is not None else None, self._graph_view.isDirected())

    def __repr__(self):
        return self._row['id']

    def __hash__(self):
        return hash(self._row['id'])

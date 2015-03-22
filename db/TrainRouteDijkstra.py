import pqdict
import tornado.web
import json
class TrainRouteDijkstra(tornado.web.RequestHandler):
    def initialize(self):
        with open('db/graph.json') as f:
            self.graph = json.load(f)


    def dijkstra(self, graph, source, target=None):
        """
        Computes the shortests paths from a source vertex to every other vertex in
        a graph

        """
        # The entire main loop is O( (m+n) log n ), where n is the number of
        # vertices and m is the number of edges. If the graph is connected
        # (i.e. the graph is in one piece), m normally dominates over n, making the
        # algorithm O(m log n) overall.

        dist = {}   
        pred = {}

        # Store distance scores in a priority queue dictionary
        pq = pqdict.PQDict()
        for node in graph:
            if node == source:
                pq[node] = 0
            else:
                pq[node] = float('inf')

        # Remove the head node of the "frontier" edge from pqdict: O(log n).
        for node, min_dist in pq.iteritems():
            # Each node in the graph gets processed just once.
            # Overall this is O(n log n).
            dist[node] = min_dist
            if node == target:
                break

            # Updating the score of any edge's node is O(log n) using pqdict.
            # There is _at most_ one score update for each _edge_ in the graph.
            # Overall this is O(m log n).
            for neighbor in graph[node]:
                if neighbor in pq:
                    new_score = dist[node] + graph[node][neighbor]
                    if new_score < pq[neighbor]:
                        pq[neighbor] = new_score
                        pred[neighbor] = node

        return dist, pred

    def _shortest_path(self, graph, source, target):
        dist, pred = self.dijkstra(graph, source, target)
        end = target
        path = [end]
        while end != source:
            end = pred[end]
            path.append(end)        
        path.reverse()
        return {'steps': path, 'dist': max(dist.values())}

    def get(self, start, stop):
        self.write(self._shortest_path(self.graph, start, stop))
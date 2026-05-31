import heapq

class RouteGraph:
    def __init__(self):
        self.graph = {}

    def add_stop(self, stop):
        if stop not in self.graph:
            self.graph[stop] = []

    def add_route(self, from_stop, to_stop, distance):
        self.add_stop(from_stop)
        self.add_stop(to_stop)
        self.graph[from_stop].append((to_stop, distance))
        self.graph[to_stop].append((from_stop, distance))

    def dijkstra(self, start, end):
        if start not in self.graph or end not in self.graph:
            return [], float('inf')
        distances = {node: float('inf') for node in self.graph}
        distances[start] = 0
        previous = {node: None for node in self.graph}
        pq = [(0, start)]
        while pq:
            current_dist, current = heapq.heappop(pq)
            if current_dist > distances[current]:
                continue
            for neighbor, weight in self.graph[current]:
                distance = current_dist + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
        path = []
        node = end
        while node is not None:
            path.append(node)
            node = previous[node]
        path.reverse()
        return path, distances[end]

    def bfs(self, start):
        if start not in self.graph:
            return []
        visited = []
        queue = [start]
        seen = set([start])
        while queue:
            node = queue.pop(0)
            visited.append(node)
            for neighbor, _ in self.graph.get(node, []):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        return visited

    def dfs(self, start, visited=None):
        if visited is None:
            visited = []
        if start not in self.graph:
            return visited
        visited.append(start)
        for neighbor, _ in self.graph.get(start, []):
            if neighbor not in visited:
                self.dfs(neighbor, visited)
        return visited

    def get_all_stops(self):
        return list(self.graph.keys())
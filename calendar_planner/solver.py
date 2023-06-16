from typing import Dict, Tuple, List, Set
from dataclasses import dataclass
import abc


@dataclass
class ConstraintSlot:
    slots: List[Tuple[float, float]]
    duration: float


DistanceMatrix = Dict[int, Dict[int, Dict[int, float]]]  # int is location index
GoalContraints = Dict[int, ConstraintSlot]  # int is User index
EdgeSet = Dict[int, Tuple[float, float]]  # travel time, end time

HOME = 0


class DistanceProvider(abc.ABC):
    @abc.abstractmethod
    def get_distance(self, when: int, from_: int, to: int) -> float:
        ...


@dataclass
class GraphNode:
    v: int
    e: Dict[int, Tuple[float, "GraphNode"]]


class Solver:
    def __init__(self, dist_provider: DistanceProvider, cons: GoalContraints):
        self._dist_provider = dist_provider
        self._cons = cons

    def get_edges(self, cons: set[int], where: int, now: float):
        possible_nexts: EdgeSet = {}
        if where != HOME:
            travel_time = self._dist_provider.get_distance(round(now), where, HOME)
            possible_nexts[HOME] = (travel_time, now + travel_time)

        for loc in cons:
            info = self._cons[loc]
            travel_time: float = self._dist_provider.get_distance(
                round(now), where, loc
            )
            new_now = now + travel_time

            possible_nexts[loc] = float("inf"), float("inf")
            for slot in info.slots:
                if new_now + info.duration <= slot[1]:
                    real_travel_time = travel_time
                    if where != HOME:
                        real_travel_time += max(slot[0] - new_now, 0)

                    end_time = max(new_now, slot[0]) + info.duration
                    assert end_time <= slot[1]

                    if real_travel_time < possible_nexts[loc][0]:
                        possible_nexts[loc] = real_travel_time, end_time
            if possible_nexts[loc][0] == float("inf"):
                del possible_nexts[loc]

        return possible_nexts

    def build_graph(self, cons: set[int], where: int, now: float) -> GraphNode:
        possible_nexts = self.get_edges(cons, where, now)

        graph: GraphNode = GraphNode(where, {})

        for loc, (travel_time, end_time) in possible_nexts.items():
            new_cons = cons.copy()
            if loc != HOME:
                new_cons.remove(loc)
                # del new_cons[loc]
            lg = self.build_graph(new_cons, loc, end_time)

            graph.e[loc] = travel_time, lg

        return graph

    def solve(self):
        graph = self.build_graph(set(self._cons.keys()), HOME, 0)

        pq: List[Tuple[Set[int], List[GraphNode]]] = []

        pq.append((set(self._cons.keys()), [GraphNode(HOME, {})]))

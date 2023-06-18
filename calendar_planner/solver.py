import abc
import heapq
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


@dataclass
class ConstraintSlot:
    slots: List[Tuple[float, float]]
    duration: float


GoalContraints = Dict[int, ConstraintSlot]  # int is User index

# v -> travel time, end time
EdgeSet = Dict[int, Tuple[float, float]]

HOME = 0


class DistanceProvider(abc.ABC):
    @abc.abstractmethod
    def get_distance(self, when: int, from_: int, to: int) -> float:
        ...


class MatrixDistanceProvider(DistanceProvider):
    def __init__(self, mat: Dict[int, Dict[int, float]]):
        self._mat = mat

    def get_distance(self, _: int, from_: int, to: int) -> float:
        return self._mat[from_][to]


class Solver:
    def __init__(self, dist_provider: DistanceProvider, cons: GoalContraints):
        self._dist_provider = dist_provider
        self._cons = cons

    def get_edges(self, cons: set[int], where: int, now: float) -> EdgeSet:
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

    def solve(self):
        # cost, time, remaining cons, cur path
        pq: List[Tuple[float, float, Set[int], List[int]]] = []

        pq.append((0.0, 0.0, set(self._cons.keys()), [HOME]))

        while pq:
            cur_cost, cur_time, cons, path = heapq.heappop(pq)

            if not cons:
                return cur_cost, cur_time, path

            u = path[-1]

            next_es = self.get_edges(cons, u, cur_time)

            for v, (v_travel_time, v_end_time) in next_es.items():
                new_cons = cons.copy()
                if v != HOME:
                    new_cons.remove(v)
                new_path = path.copy()
                new_path.append(v)
                heapq.heappush(
                    pq, (cur_cost + v_travel_time, v_end_time, new_cons, new_path)
                )

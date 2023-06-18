from calendar_planner.solver import (
    Solver,
    DistanceProvider,
    MatrixDistanceProvider,
    ConstraintSlot,
    GraphNode,
)
import mock


class MockDistanceProvider(DistanceProvider):
    def __init__(self, mock: mock.MagicMock):
        self._mock = mock

    def get_distance(self, when: int, from_: int, to: int) -> float:
        return self._mock(when, from_, to)


def test_get_next_one():
    pl = mock.MagicMock()
    prov = MockDistanceProvider(pl)
    cons = {1: ConstraintSlot([(10, 15)], 2)}
    s = Solver(prov, cons)

    pl.return_value = 1.0

    r = s.get_edges({1}, 0, 0)

    assert r == {1: (1.0, 12)}


def test_get_next_one_too_late():
    pl = mock.MagicMock()
    prov = MockDistanceProvider(pl)
    s = Solver(prov, {1: ConstraintSlot([(10, 15)], 2)})

    pl.return_value = 1.0

    r = s.get_edges({1}, 0, 14)

    assert r == {}


def test_get_next_one_start_away_from_home():
    pl = mock.MagicMock()
    prov = MockDistanceProvider(pl)
    s = Solver(prov, {1: ConstraintSlot([(10, 15)], 2)})

    pl.return_value = 1.0

    r = s.get_edges({1}, 1, 1)

    assert r == {0: (1.0, 2.0), 1: (9.0, 12)}


def test_get_next_two_slots():
    pl = mock.MagicMock()
    prov = MockDistanceProvider(pl)
    s = Solver(prov, {1: ConstraintSlot([(10, 15), (20, 25)], 2)})

    pl.return_value = 1.0

    r = s.get_edges({1}, 0, 0)

    assert r == {1: (1.0, 12)}


def test_solve_one():
    pl = mock.MagicMock()
    prov = MockDistanceProvider(pl)
    s = Solver(
        prov, {1: ConstraintSlot([(10, 15)], 2), 2: ConstraintSlot([(13, 17)], 3)}
    )

    pl.return_value = 1.0

    cost, end_t, r = s.solve()

    assert [0, 1, 2] == r


def test_solve_asym():
    dist_mat = {
        0: {
            1: 100.0,
            2: 1.0,
        },
        1: {
            0: 1.0,
            2: 1.0,
        },
        2: {
            0: 1.0,
            1: 1.0,
        },
    }
    prov = MatrixDistanceProvider(dist_mat)
    s = Solver(
        prov, {1: ConstraintSlot([(10, 17)], 2), 2: ConstraintSlot([(11, 17)], 3)}
    )

    cost, end_t, r = s.solve()

    assert [0, 2, 1] == r


def test_solve_tight():
    pl = mock.MagicMock()
    prov = MockDistanceProvider(pl)
    s = Solver(
        prov, {1: ConstraintSlot([(10, 15)], 2), 2: ConstraintSlot([(13, 16)], 3)}
    )

    pl.return_value = 1.0

    cost, end_t, r = s.solve()

    assert [0, 1, 2] == r

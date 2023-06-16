from calendar_planner.solver import Solver, DistanceProvider, ConstraintSlot, GraphNode
import mock


class MockDistanceProvider(DistanceProvider):
    def __init__(self, mock: mock.MagicMock):
        self._mock = mock

    def get_distance(self, when: int, from_: int, to: int) -> float:
        return self._mock(when, from_, to)


def test_get_next_one():
    pl = mock.MagicMock()
    prov = MockDistanceProvider(pl)
    s = Solver(prov)

    pl.return_value = 1.0

    r = s.get_edges({1: ConstraintSlot([(10, 15)], 2)}, 0, 0)

    assert r == {1: (1.0, 12)}


def test_get_next_one_too_late():
    pl = mock.MagicMock()
    prov = MockDistanceProvider(pl)
    s = Solver(prov)

    pl.return_value = 1.0

    r = s.get_edges({1: ConstraintSlot([(10, 15)], 2)}, 0, 14)

    assert r == {}


def test_get_next_one_start_away_from_home():
    pl = mock.MagicMock()
    prov = MockDistanceProvider(pl)
    s = Solver(prov)

    pl.return_value = 1.0

    r = s.get_edges({1: ConstraintSlot([(10, 15)], 2)}, 1, 1)

    assert r == {0: (1.0, 2.0), 1: (9.0, 12)}


def test_get_next_two_slots():
    pl = mock.MagicMock()
    prov = MockDistanceProvider(pl)
    s = Solver(prov)

    pl.return_value = 1.0

    r = s.get_edges({1: ConstraintSlot([(10, 15), (20, 25)], 2)}, 0, 0)

    assert r == {1: (1.0, 12)}


def test_graph_one():
    pl = mock.MagicMock()
    prov = MockDistanceProvider(pl)
    s = Solver(prov)

    pl.return_value = 1.0

    r = s.build_graph({1: ConstraintSlot([(10, 15)], 2)}, 0, 0)

    assert r.v == 0
    assert r.e == {
        1: (  # goto 1
            1.0,
            GraphNode(
                v=1,
                e={
                    0: (  # goto 0
                        1.0,
                        GraphNode(
                            v=0,
                            e={},
                        ),
                    ),
                },
            ),
        ),
    }


def test_graph_two():
    pl = mock.MagicMock()
    prov = MockDistanceProvider(pl)
    s = Solver(prov)

    pl.return_value = 1.0

    r = s.build_graph(
        {1: ConstraintSlot([(10, 15)], 2), 2: ConstraintSlot([(13, 17)], 3)}, 0, 0
    )

    assert r.v == 0
    assert r.e == {
        1: (  # goto 1
            1.0,
            GraphNode(
                v=1,  # now t=10
                e={
                    0: (  # goto 0
                        1.0,
                        GraphNode(
                            v=0,  # now t=13
                            e={
                                2: (  # goto 2
                                    1.0,
                                    GraphNode(
                                        v=2,  # now t=14
                                        e={
                                            0: (  # goto 0
                                                1.0,
                                                GraphNode(
                                                    v=0,  # now t=18
                                                    e={},
                                                ),
                                            ),
                                        },
                                    ),
                                ),
                            },
                        ),
                    ),
                    2: (  # goto 2
                        1.0,
                        GraphNode(
                            v=2,
                            e={
                                0: (  # goto 0
                                    1.0,
                                    GraphNode(
                                        v=0,
                                        e={},
                                    ),
                                ),
                            },
                        ),
                    ),
                },
            ),
        ),
        2: (  # goto 2
            1.0,
            GraphNode(
                v=2,
                e={
                    0: (  # goto 0
                        1.0,
                        GraphNode(
                            v=0,
                            e={},
                        ),
                    ),
                },
            ),
        ),
    }


def test_graph_two_tight():
    pl = mock.MagicMock()
    prov = MockDistanceProvider(pl)
    s = Solver(prov)

    pl.return_value = 1.0

    r = s.build_graph(
        {1: ConstraintSlot([(10, 15)], 2), 2: ConstraintSlot([(13, 16)], 3)}, 0, 0
    )

    assert r.v == 0
    assert r.e == {
        1: (  # goto 1
            1.0,
            GraphNode(
                v=1,  # now t=10
                e={
                    0: (  # goto 0
                        1.0,
                        GraphNode(
                            v=0,  # now t=13
                            e={},  # wasted time going 0, can't go to 2
                        ),
                    ),
                    2: (  # goto 2
                        1.0,
                        GraphNode(
                            v=2,
                            e={
                                0: (  # goto 0
                                    1.0,
                                    GraphNode(
                                        v=0,
                                        e={},
                                    ),
                                ),
                            },
                        ),
                    ),
                },
            ),
        ),
        2: (  # goto 2
            1.0,
            GraphNode(
                v=2,
                e={
                    0: (  # goto 0
                        1.0,
                        GraphNode(
                            v=0,
                            e={},
                        ),
                    ),
                },
            ),
        ),
    }

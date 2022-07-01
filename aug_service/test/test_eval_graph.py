"""A unit test file to eval the intersect_edge_ratio function."""
import sys
import logging
import unittest
from evaluation.eval_graph import intersect_edge_ratio
from evaluation.eval_graph import FloorPlan, Room


class TestIntersectEdgeRatioFunction(unittest.TestCase):

    def test_invalid_input(self):
        with self.assertRaises(AssertionError):
            intersect_edge_ratio([0, 0, 1, 1], [0, 0, -1, -1])
        with self.assertRaises(AssertionError):
            intersect_edge_ratio([0, 0, -1, -1], [0, 0, 1, 1])

    def test_no_intersection(self):
        rec1 = [0, 0, 1, 1]

        # Move rec2 to four corners of the rec1.
        for dx, dy in [(0, 0), (2, 0), (2, 2), (0, 2)]:
            rec2 = [-1 + dx, -1 + dy, dx, dy]
            self.assertEqual((None, 0),
                             intersect_edge_ratio(rec1, rec2))

    def test_overlap(self):
        # TODO: catch warnings.

        rec1 = [0, 0, 1, 1]
        rec2 = [0.5, 0.5, 1.5, 1.5]
        self.assertEqual((None, 0),
                         intersect_edge_ratio(rec1, rec2))

        rec1 = [0, 0, 2, 2]
        rec2 = [0, 0, 3, 3]
        self.assertEqual((None, 0),
                         intersect_edge_ratio(rec1, rec2))

    def test_left(self):
        rec1 = [0, 0, 1, 1]

        rec2 = [-0.5, 0.5, 0, 1]
        self.assertEqual(('left', 0.5),
                         intersect_edge_ratio(rec1, rec2))
        self.assertEqual(('right', 1),
                         intersect_edge_ratio(rec2, rec1))

        rec2 = [-0.5, 0, 0, 0.5]
        self.assertEqual(('left', 0.5),
                         intersect_edge_ratio(rec1, rec2))
        self.assertEqual(('right', 1),
                         intersect_edge_ratio(rec2, rec1))

    def test_right(self):
        rec1 = [0, 0, 1, 1]
        rec2 = [1, 0.5, 1.5, 1]
        self.assertEqual(('right', 0.5),
                         intersect_edge_ratio(rec1, rec2))
        self.assertEqual(('left', 1),
                         intersect_edge_ratio(rec2, rec1))

        rec2 = [1, 0, 1.5, 0.5]
        self.assertEqual(('right', 0.5),
                         intersect_edge_ratio(rec1, rec2))
        self.assertEqual(('left', 1),
                         intersect_edge_ratio(rec2, rec1))

    def test_up(self):
        rec1 = [0, 0, 1, 1]
        rec2 = [0, 1, 0.5, 1.5]
        self.assertEqual(('up', 0.5),
                         intersect_edge_ratio(rec1, rec2))
        self.assertEqual(('bottom', 1),
                         intersect_edge_ratio(rec2, rec1))

        rec2 = [0.5, 1, 1, 1.5]
        self.assertEqual(('up', 0.5),
                         intersect_edge_ratio(rec1, rec2))
        self.assertEqual(('bottom', 1),
                         intersect_edge_ratio(rec2, rec1))

    def test_bottom(self):
        rec1 = [0, 0, 1, 1]
        rec2 = [0, -0.5, 0.5, 0]
        self.assertEqual(('bottom', 0.5),
                         intersect_edge_ratio(rec1, rec2))
        self.assertEqual(('up', 1),
                         intersect_edge_ratio(rec2, rec1))

        rec2 = [0.5, -0.5, 1, 0]
        self.assertEqual(('bottom', 0.5),
                         intersect_edge_ratio(rec1, rec2))
        self.assertEqual(('up', 1),
                         intersect_edge_ratio(rec2, rec1))


class TestFloorPlan(unittest.TestCase):
    # Sets commonly used test variable for TestFloorPlanInit.
    def setUp(self):
        self.desired_size = {'CIRC': 100,
                             'OPERATE': 100,
                             'WORK': 100,
                             'ENTRANCE': 100,
                             'MEET': 100,
                             'WASH': 100,
                             'OBS': 100}

    # Tests the FloorPlan.init function.
    # Init also calls build_graph function.
    def test_invalid_RoomList_input(self):
        """Tests the input of room_list."""
        empty_room_list = []
        with self.assertRaises(AssertionError):
            FloorPlan(empty_room_list, self.desired_size)

        non_room_list = [0, 0, 1, 1]
        with self.assertRaises(AssertionError):
            FloorPlan(non_room_list, self.desired_size)

    def test_invalid_DesiredSize_input(self):
        """Tests the input of desired_size_test."""
        room_list = [Room(0, "WORK", [0, 0, 1, 1])]
        empty_desired_size = {}
        with self.assertRaises(AssertionError):
            FloorPlan(room_list, empty_desired_size)

    def test_wall(self):
        # Room edge that does not touch other room will be setting
        # to touch the wall by default.
        room_list = [Room(0, "WORK", [0, 0, 1, 1])]
        ans = {(0, 'WORK'): [('right', 'wall', 1),
                               ('left', 'wall', 1),
                               ('up', 'wall', 1),
                               ('bottom', 'wall', 1)]}
        self.assertEqual(ans, FloorPlan(room_list, self.desired_size).adj_graph)

    def test_adj_graph_full_adj(self):
        # Test if adjacent graph is correct for two rooms that have a full
        # adjacent (Common edge ratio = 1).
        # Room 2 is adjacent to 1 on the right with ratio 1.
        room_list = [Room(0, "WORK", [0, 0, 10, 10]),
                     Room(1, "WORK", [10, 0, 20, 10])]
        ans = {(0, 'WORK'): [('right', 'WORK', 1),
                               ('left', 'wall', 1),
                               ('up', 'wall', 1),
                               ('bottom', 'wall', 1)],
               (1, 'WORK'): [('left', 'WORK', 1),
                               ('right', 'wall', 1),
                               ('up', 'wall', 1),
                               ('bottom', 'wall', 1)]}
        self.assertEqual(ans, FloorPlan(room_list, self.desired_size).adj_graph)

    def test_adj_graph_part_adj(self):
        # Test if adjacent graph is correct for two rooms that have a partial
        # adjacent (Common edge ratio < 1).
        # Room 2 is adjacent to 1 on the right with ratio 0.5.
        room_list = [Room(0, "WORK", [0, 0, 10, 10]),
                     Room(1, "WORK", [10, 5, 20, 15])]
        ans = {(0, 'WORK'): [('right', 'WORK', 0.5),
                               ('right', 'wall', 0.5),
                               ('left', 'wall', 1),
                               ('up', 'wall', 1),
                               ('bottom', 'wall', 1)],
               (1, 'WORK'): [('left', 'WORK', 0.5),
                               ('right', 'wall', 1),
                               ('left', 'wall', 0.5),
                               ('up', 'wall', 1),
                               ('bottom', 'wall', 1)]}
        self.assertEqual(ans, FloorPlan(room_list, self.desired_size).adj_graph)

    def test_alignment(self):
        # Tests alignment score for zero cases.
        rooms = []
        for i in range(1, 10):
            rooms.append(Room(i, 'WORK', [i, 0, 1 + i, 1]))
            floorplan = FloorPlan(rooms, self.desired_size)
            self.assertEqual(0, floorplan._alignment_check())

        # Tests alignment score for non-zero cases.
        rooms = [Room(0, 'ENTRANCE', [0, 0, 10, 10]),
                 Room(1, 'WORK', [10, 0, 20, 5])]
        floorplan = FloorPlan(rooms, self.desired_size)
        self.assertEqual(1, floorplan._alignment_check())

    def test_size(self):
        # All zones are set to 100 as desired size.
        rooms = []
        for i in range(1, 10):
            rooms.append(Room(i, 'WORK', [i, 0, 1 + i, 1]))
            floorplan = FloorPlan(rooms, self.desired_size)
            self.assertEqual(100-i, floorplan._size_check()['WORK'])

        rooms = []
        for i in range(1, 10):
            rooms.append(Room(i, 'ENTRANCE', [i, 0, 1 + i, 1]))
            floorplan = FloorPlan(rooms, self.desired_size)
            self.assertEqual(100-i, floorplan._size_check()['ENTRANCE'])

        rooms = []
        for i in range(1, 10):
            rooms.append(Room(i, 'CIRC', [i, 0, 1 + i, 1]))
            floorplan = FloorPlan(rooms, self.desired_size)
            self.assertEqual(100-i, floorplan._size_check()['CIRC'])

    def test_lounge(self):
        # Fakes ENTRANCE to be adjacent with core area.
        rooms = [Room(0, 'ENTRANCE', [0, 0, 1, 1]),
                 Room(1, 'core', [1, 0, 2, 1])]
        floorplan = FloorPlan(rooms, self.desired_size)
        self.assertEqual({'touch_gv': 3, 'touch_core': 1},
                          floorplan._lounge_check())

        # Tests lounge that not touch core.
        rooms = [Room(0, 'ENTRANCE', [0, 0, 1, 1])]
        floorplan = FloorPlan(rooms, self.desired_size)
        self.assertEqual({'touch_gv': 4, 'touch_core': 0},
                          floorplan._lounge_check())

        # Tests lounge that not touch good view.
        rooms = [Room(0, 'ENTRANCE', [0, 0, 1, 1]),
                 Room(1, 'core', [1, 0, 2, 1]),
                 Room(2, 'WORK', [0, 1, 1, 2]),
                 Room(3, 'CIRC', [-1, 0, 0, 1]),
                 Room(4, 'MEET', [0, -1, 1, 0])]
        floorplan = FloorPlan(rooms, self.desired_size)
        self.assertEqual({'touch_gv': 0, 'touch_core': 1},
                          floorplan._lounge_check())

    def test_access_hw(self):
        # Tests Zones that can access to the hallway.
        rooms = [Room(0, 'WORK', [0, 0, 1, 1]),
                 Room(1, 'CIRC', [1, 0, 2, 1])]
        floorplan = FloorPlan(rooms, self.desired_size)
        self.assertEqual(0, floorplan._access_hw_check())

        rooms = [Room(0, 'ENTRANCE', [0, 0, 1, 1]),
                 Room(1, 'CIRC', [1, 0, 2, 1])]
        floorplan = FloorPlan(rooms, self.desired_size)
        self.assertEqual(0, floorplan._access_hw_check())

        rooms = [Room(0, 'MEET', [0, 0, 1, 1]),
                 Room(1, 'CIRC', [1, 0, 2, 1])]
        floorplan = FloorPlan(rooms, self.desired_size)
        self.assertEqual(0, floorplan._access_hw_check())

        # Tests Zones that can not access to the hallway.
        rooms = [Room(0, 'WORK', [0, 0, 1, 1]),
                 Room(1, 'WORK', [1, 0, 2, 1]),
                 Room(2, 'WORK', [2, 0, 3, 1]),
                 Room(3, 'CIRC', [10, 0, 20, 1])]
        floorplan = FloorPlan(rooms, self.desired_size)
        self.assertEqual(3, floorplan._access_hw_check())

    def test_ext_work(self):
        # Tests WORKS adjacent to the wall.
        rooms = []
        for i in range(1, 10):
            rooms.append(Room(0, 'WORK', [i, 0, 1 + i, 1]))
            floorplan = FloorPlan(rooms, self.desired_size)
            self.assertEqual(i, floorplan._check_ext_work())

        # Tests WORKS not adjacent to the wall.
        rooms = [Room(0, 'WORK', [0, 0, 1, 1]),
                 Room(1, 'core', [1, 0, 2, 1]),
                 Room(2, 'ENTRANCE', [0, 1, 1, 2]),
                 Room(3, 'CIRC', [-1, 0, 0, 1]),
                 Room(4, 'MEET', [0, -1, 1, 0])]
        floorplan = FloorPlan(rooms, self.desired_size)
        self.assertEqual(0, floorplan._check_ext_work())

    def test_meet(self):
        # Tests there is no MEET between WORK and ENTRANCE.
        rooms = [Room(0, 'WORK', [0, 0, 1, 1]),
                 Room(1, 'ENTRANCE', [1, 0, 2, 1])]
        floorplan = FloorPlan(rooms, self.desired_size)
        self.assertEqual(1, floorplan._check_meet())

        # Tests there is a MEET between WORK and ENTRANCE.
        rooms = [Room(0, 'WORK', [0, 0, 1, 1]),
                 Room(1, 'MEET', [1, 0, 2, 1]),
                 Room(2, 'ENTRANCE', [2, 0, 3, 1])]
        floorplan = FloorPlan(rooms, self.desired_size)
        self.assertEqual(0, floorplan._check_meet())

    def test_get_num_hallway(self):
        rooms = []
        for i in range(1, 10):
            rooms.append(Room(i, 'CIRC', [i, 0, 1 + i, 1]))
            floorplan = FloorPlan(rooms, self.desired_size)
            self.assertEqual(i, floorplan._get_num_hallway())


if __name__ == '__main__':
    unittest.main()

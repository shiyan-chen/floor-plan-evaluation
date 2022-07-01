"""Evaluation algorithm using a graph representation."""
import logging
import numpy as np


def intersect_edge_ratio(rec1, rec2):
    """Calculates common edge ratio between two rectangles.
    
    Ratio is defined as
    length-of-overlap-of-rec1-and-rec2 / length-of-overlap-side-of-rec1.
    Rectangles are represented as a list of four elements, x_min, y_min,
    x_max, y_max. If two rectangles are not adjacent or overlap, returns
    None, 0.

    Rectangles are represented as a list of four elements, x_min, y_min,
    x_max, y_max. Two rectangles must be adjacent.

    Args:
        rec1: rectangle 1.
        rec2: rectangle 2.
    Returns:
        Two parameters that shows  common edge direction and ratio.
        example:
        'left', 0.1
        It means rectangle 2 is adjacent to rectangle 1 at the left with
        common edge ratio 0.1.
    """

    # Validation test.
    for rec in [rec1, rec2]:
        assert len(rec) == 4, "Invalid input rectangle."
        assert rec[0] < rec[2], "Invalid input rectangle: x_min < x_max"
        assert rec[1] < rec[3], "Invalid input rectangle: y_min < y_max"

    rec1_xmin = rec1[0]
    rec1_xmax = rec1[2]
    rec1_ymin = rec1[1]
    rec1_ymax = rec1[3]

    rec2_xmin = rec2[0]
    rec2_xmax = rec2[2]
    rec2_ymin = rec2[1]
    rec2_ymax = rec2[3]

    def _is_overlap():
        if rec1_xmin >= rec2_xmax or rec1_xmax <= rec2_xmin:
            return False
        if rec1_ymin >= rec2_ymax or rec1_ymax <= rec2_ymin:
            return False
        return True

    # Two rectangles should not have overlaps.
    if _is_overlap():
        logging.warning('Rectangles are overlapped.')
    
    # Case: rec2 is adjacent on the left.
    if rec2_xmax == rec1_xmin:
        intersect = min(np.abs(rec1_ymax - rec2_ymin),
                        np.abs(rec1_ymin - rec2_ymax),
                        rec1_ymax - rec1_ymin, rec2_ymax - rec2_ymin)
        if rec1_ymax - rec1_ymin != 0 and intersect != 0:
            intersect_ratio = intersect/(rec1_ymax - rec1_ymin)
            return 'left', intersect_ratio
        else:
            return None, 0

    # Case: rec2 is adjacent on the right.
    elif rec2_xmin == rec1_xmax:
        intersect = min(np.abs(rec1_ymax - rec2_ymin),
                        np.abs(rec1_ymin - rec2_ymax),
                        rec1_ymax - rec1_ymin, rec2_ymax - rec2_ymin)
        if rec1_ymax - rec1_ymin != 0 and intersect != 0:
            intersect_ratio = intersect / (rec1_ymax - rec1_ymin)
            return 'right', intersect_ratio
        else:
            return None, 0

    # Case: rec2 is adjacent on the up.
    elif rec2_ymin == rec1_ymax:
        intersect = min(np.abs(rec1_xmax - rec2_xmin),
                        np.abs(rec1_xmin - rec2_xmax),
                        rec1_xmax - rec1_xmin, rec2_xmax - rec2_xmin)
        if rec1_xmax - rec1_xmin != 0 and intersect != 0:
            intersect_ratio = intersect / (rec1_xmax - rec1_xmin)
            return 'up', intersect_ratio
        else:
            return None, 0

    # Case: rec2 is adjacent on the bottom.
    elif rec2_ymax == rec1_ymin:
        intersect = min(np.abs(rec1_xmax - rec2_xmin),
                        np.abs(rec1_xmin - rec2_xmax),
                        rec1_xmax - rec1_xmin, rec2_xmax - rec2_xmin)
        if rec1_xmax - rec1_xmin != 0 and intersect != 0:
            intersect_ratio = intersect / (rec1_xmax - rec1_xmin)
            return 'bottom', intersect_ratio
        else:
            return None, 0

    else:
        return None, 0


class Room:
    """Room represents each physical room from real floor plan.

    Note that during evaluation, we assume the 'wall's are always good views.
    During evluation, the input floorplans do not contain 'good view'
    information. In general, 'wall's are good views, so we make this assumption.

    Attributes:
        room_id: an unique integer to represent the room.
        prog_type: program type, whether "ENTRANCE", "CIRC", "WORK", or other type.
        shape: coords of upper-left point and buttom-right point.
        area: sq.ft size of the room.
    """

    available_prog_types = ['ENTRANCE', "CIRC", 'WORK', 'OPERATE', 'MEET', 'WASH',
                            'OBS', 'core', 'wall']
    
    def __init__(self, room_id, prog_type, shape):
        self.room_id = room_id
        self.prog_type = prog_type
        assert prog_type in Room.available_prog_types, 'Invalid program type.'
        self.shape = [int(round(shape[0])),
                      int(round(shape[1])),
                      int(round(shape[2])),
                      int(round(shape[3]))]
        self.area = (shape[2] - shape[0]) * (shape[3] - shape[1])


class FloorPlan:
    """FloorPlan represents each physical floor plan from real floor plan, it
        made by rooms.

    Attributes:
        room_list: a list of rooms that this floor contains.
        adj_graph: a graph representative of the floor.
        desired_size: desired size of each zone.
    """
    
    def __init__(self, room_list, desired_size):
        """Inits room with parameters."""
        self.room_list = room_list
        # Validation test for room_list.
        assert len(self.room_list) > 0, "Invalid input room list: Empty"
        for room in self.room_list:
            assert type(room).__name__ == 'Room', "Invalid room list: Not a Room class"

        self.desired_size = desired_size
        # Validation test for desired_size.
        assert len(self.desired_size) > 0, "Invalid input desired_size: Empty"

        self.adj_graph = self.build_graph()

    def build_graph(self):
        """Builds floor plan graph by list of rooms."""
        graph = {(i, self.room_list[i].prog_type): []
                 for i in range(len(self.room_list))}

        # Calculate each two rooms adjacency relationships, aka common edge
        # ratio.
        for i, room_self in enumerate(self.room_list):
            for j, room_other in enumerate(self.room_list):
                if i != j:
                    intersection_dir, intersection_ratio = intersect_edge_ratio(room_self.shape,
                                                                                room_other.shape)
                    if intersection_dir:
                        graph[(i, room_self.prog_type)].append(
                            (intersection_dir, room_other.prog_type,
                             intersection_ratio))
        for i, room_self in enumerate(self.room_list):
            for direction in ['right', 'left', 'up', 'bottom']:
                res = 1
                for edge in graph[(i, room_self.prog_type)]:
                    if edge[0] == direction:
                        res -= edge[2]
                if res > 0:
                    graph[(i, room_self.prog_type)].append(
                        (direction, 'wall', res))
        return graph

    def eval(self):
        """Evaluates floor graph by checking multiple rules."""
        align_score = self._alignment_check()
        size_score = self._size_check()
        lounge_score = self._lounge_check()
        hallway_access_score = self._access_hw_check()
        work_ext_score = self._check_ext_work()
        meet_score = self._check_meet()
        num_hallway = self._get_num_hallway()
        return (align_score, size_score, self.desired_size, lounge_score,
                hallway_access_score, work_ext_score, meet_score, num_hallway)

    def _alignment_check(self):
        """Checks alignment score of the floor plan.

        Returns:
            align_score: High align_score means more un-alignment (0 is
                the best score).
        """
        align_score = 0
        for item, val in self.adj_graph.items():
            if item[1] != 'CIRC':
                for edge in val:
                    align_score += np.abs(edge[2] - 1)
        return align_score

    def _size_check(self):
        """Checks size of each program type of the floor plan.

        Returns:
            size_score: High size_score means high deviation from desired area
                        ({0, 0, 0, 0, 0 ...} is the best case which means no
                        deviation).
        """
        size_score = self.desired_size.copy()
        for room in self.room_list:
            size_score[room.prog_type] -= room.area
        return size_score

    def _lounge_check(self):
        """Checks if lounge touch the core area and the good view.

           Note that in evluation, we assume all walls are good views. See
           more details in the Room.
        Return:
            lounge_score: {'touch_gv': 0, 'touch_core': 1}  (0 means not touch,
            >=1 means touch).
        """
        lounge_score = {'touch_gv': 0, 'touch_core': 0}
        max_size = 0
        lounge_index = 0
        for room in self.room_list:
            if room.prog_type == 'ENTRANCE':
                if room.area > max_size:
                    max_size = room.area
                    lounge_index = room.room_id
        for item, val in self.adj_graph.items():
            if item[0] == lounge_index:
                for edge in val:
                    if edge[1] == 'core':
                        lounge_score['touch_core'] += 1
                    elif edge[1] == 'wall':
                        lounge_score['touch_gv'] += 1
        return lounge_score

    def _access_hw_check(self):
        """Checks the accessibility of floor plan.

        Return:
            hallway_access_score: High hallway_access score means more
                un-accessibility. (Best would be 0; it means all rooms are
                connected to hallway.)
        """
        hallway_access_score = 0
        for item, val in self.adj_graph.items():
            if item[1] != 'CIRC':
                num_hallway_touch = 0
                for edge in val:
                    if edge[1] == 'CIRC':
                        num_hallway_touch += 1
                if num_hallway_touch == 0:
                    hallway_access_score += 1
        return hallway_access_score

    def _check_ext_work(self):
        """Checks the rule: 'Work is better put at the wall'.

        Return:
            work_ext_score: High work_ext_score means more area are assigned
            to be work space.
        """
        work_ext_score = 0
        for item, val in self.adj_graph.items():
            if item[1] == 'WORK':
                for edge in val:
                    if edge[1] == 'wall':
                        for room in self.room_list:
                            if room.room_id == item[0]:
                                size = room.area
                                break
                        work_ext_score += size
                        break
        return work_ext_score

    def _check_meet(self):
        """Rule: 'meet should separate lounge and work as much as possible.'.

        Return:
            meet_score: To simplify it we just lower the adjacency between
            lounge and work.
        """
        meet_score = 0
        for item, val in self.adj_graph.items():
            if item[1] == 'ENTRANCE':
                for edge in val:
                    if edge[1] == 'WORK':
                        meet_score += edge[2]
        return meet_score

    def _get_num_hallway(self):
        """Returns the number of circulate.

        Smaller num_hallway means less corner of hallway, the smaller
        the better.
        Return:
            num_hallway: the number of circulate.
        """
        # Count number of circulate: better to be few.
        num_hallway = 0
        for room in self.room_list:
            if room.prog_type == 'CIRC':
                num_hallway += 1
        return num_hallway


def evaluate(floor_plan_json):
    """Converts floor_plan_json to floor plan and evaluate it.

    Args:
        floor_plan_json: A dictionary that specifies each zone's location
        using rectangular representation.
    Returns:
        evaluation scores.
    """
    room_list = []
    index = 0
    total_area = 0
    total_usable_area = 0
    total_used_area = 0
    for key, val in floor_plan_json.items():
        for single_rec in val:
            rec = Room(index, key, single_rec)
            room_list.append(rec)
            index += 1
            total_area += rec.area
            if key != 'OBS':
                total_usable_area += rec.area
                total_used_area += rec.area

    desired_size = {'CIRC': 0.0*total_usable_area,
                    'OPERATE': 0.0*total_usable_area,
                    'WORK': 0.0*total_usable_area,
                    'ENTRANCE': 0.0*total_usable_area,
                    'MEET': 0.0*total_usable_area,
                    'WASH': 0.0*total_usable_area,
                    'OBS': 0.0*total_usable_area}

    fp = FloorPlan(room_list, desired_size)
    return fp.eval(), total_area, total_usable_area, total_used_area

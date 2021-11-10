from typing import List
from typing import Tuple


COLINEAR = 0
CLOCKWISE = 1
COUNTERCLOCKWISE = 2


def orientation(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]):
    value = (p2[1] - p1[1]) * (p3[0] - p2[0]) - (p2[0] - p1[0]) * (p3[1] - p2[1])
    if value < 0:
        return COUNTERCLOCKWISE
    elif value == 0:
        return COLINEAR
    else:
        return CLOCKWISE


def convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Return convex hull of 2D points."""
    # remove duplicates
    points = list(set(points))

    if len(points) < 4:
        return points

    # Gift wrapping algorithm, adapted to Python from
    # https://iq.opengenus.org/gift-wrap-jarvis-march-algorithm-convex-hull/

    hull = []
    leftmost = min(points)
    current = leftmost
    while True:
        hull.append(current)

        best = points[0]

        for point in points:
            # Checking best == current is necessary because orientation function
            # is unreliable if the two points are the same
            if best == current or orientation(current, point, best) == COUNTERCLOCKWISE:
                best = point

        current = best

        if current == leftmost:
            break

    return hull


def point_inside(point: Tuple[float, float], hull: List[Tuple[float, float]]):
    """
    Returns True if a point is inside a convex hull, False otherwise.
    Points located exactly on the edge may return either.
    """
    points = hull + [point]
    return point not in convex_hull(points)

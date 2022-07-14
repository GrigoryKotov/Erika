import math
from statistics import fmean
from typing import List

# Lens constants assuming a 1080p image
f = 714.285714
center = [960, 540]
D = 1.082984  # For image-1, switch to 0.871413 for image-2


def cartesian2sphere(pt):
    x = (pt[0] - center[0]) / f
    y = (pt[1] - center[1]) / f

    r = math.sqrt(x*x + y*y)
    if r != 0:
        x /= r
        y /= r
    r *= D
    sin_theta = math.sin(r)
    x *= sin_theta
    y *= sin_theta
    z = math.cos(r)

    return [x, y, z]


def sphere2cartesian(pt):
    r = math.acos(pt[2])
    r /= D
    if pt[2] != 1:
        r /= math.sqrt(1 - pt[2] * pt[2])
    x = r * pt[0] * f + center[0]
    y = r * pt[1] * f + center[1]
    return [x, y]


def convert_point(point: List[int]) -> List[int]:
    """Convert single points between Cartesian and spherical coordinate systems"""
    if len(point) == 2:
        return cartesian2sphere(point)
    elif len(point) == 3:
        return sphere2cartesian(point)
    else:
        raise ValueError(f'Expected point to be 2 or 3D, got {len(point)} dimensions')


class CartesianBbox:

    def __init__(self, points: List[int], fmt: str):
        assert fmt in ['xyxy', 'xywh', 'cxcywh'], 'Invalid bbox format'
        assert len(points) == 4, 'Cartesian bbox must have 4 values'
        self.points = points
        self.fmt = fmt


class SphericalBbox:

    def __init__(self, points: List[int]):
        assert len(center) == 6, 'SphericalBox must have 3 values'
        self.points = points


def bbox_to_spherical(cartesian: CartesianBbox) -> SphericalBbox:
    
    sb = SphericalBbox()
    if cartesian.fmt == 'xyxy':
        sb.points = cartesian.points
    elif cartesian.fmt == 'xywh':
        x1 = cartesian2sphere(cartesian.points[0])
        y1 = cartesian2sphere(cartesian.points[1])
        x2 = cartesian2sphere(cartesian.points[0]+cartesian.points[2])
        y2 = cartesian2sphere(cartesian.points[1]+cartesian.points[3])
        sb.points = [x1, y1, x2, y2]
    else:
        x1 = cartesian2sphere(cartesian.points[0]-cartesian.points[2]/2)
        y1 = cartesian2sphere(cartesian.points[1]-cartesian.points[3]/2)
        x2 = cartesian2sphere(cartesian.points[0]+cartesian.points[2]/2)
        y2 = cartesian2sphere(cartesian.points[1]+cartesian.points[3]/2)
        sb.points = [x1, y1, x2, y2]
    return sb


class CartesianPolygon:

    def __init__(self, points: List[int]):
        assert len(points) <= 40, 'Polygon must have less than 20 points'
        assert isConvex(points) == True, 'Polygon must be convex'
        assert isRegular(points) == True, 'Polygon must be regular'
        self.points = points


class SphericalPolygon:

    def __init__(self, points: List[int]):        
        self.points = points


def polygon_to_spherical(cartesian: CartesianPolygon) -> SphericalPolygon:
    sp = SphericalPolygon()    
    p = cartesian.points
    ps = []
    for x, y in zip(p[0::2], p[1::2]):
        ps.append(cartesian2sphere(x))
        ps.append(cartesian2sphere(y))
    sp.points = ps
    return sp


def isConvex(points: List[int]):

    sgn = None

    for i in range(len(points)/2):
        dx1 = points[ ((i + 1) % len(points)) * 2] - points[ (i % len(points)) * 2 ]
        dy1 = points[ ((i + 1) % len(points)) * 2 + 1] - points[ (i % len(points)) * 2 + 1]
        dx2 = points[ ((i + 2) % len(points)) * 2] - points[ ((i + 1) % len(points)) * 2 ]
        dy2 = points[ ((i + 2) % len(points)) * 2 + 1] - points[ ((i + 1) % len(points)) * 2 + 1]
        crossproduct = dx1*dy2 - dx2*dy1
        if i != 0 and sgn != crossproduct:
            return False
            
        sgn = math.copysign(1, crossproduct)

    return True


def isRegular(points: List[int]):
    
    for i in range(len(points)/2):
        dx1 = points[ ((i + 1) % len(points)) * 2] - points[ (i % len(points)) * 2 ]
        dy1 = points[ ((i + 1) % len(points)) * 2 + 1] - points[ (i % len(points)) * 2 + 1]
        dx2 = points[ ((i + 2) % len(points)) * 2] - points[ ((i + 1) % len(points)) * 2 ]
        dy2 = points[ ((i + 2) % len(points)) * 2 + 1] - points[ ((i + 1) % len(points)) * 2 + 1]
        
        if (dx1**2 + dy1**2 - dx2**2 - dy2**2) > 1e-5:
            return False

    return True

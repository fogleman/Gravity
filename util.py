import os
from pyglet.gl import *

def load_image(path):
    image = pyglet.resource.image(path)
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2
    return image
    
def load_animation(path, duration, last_duration=None):
    frames = []
    files = os.listdir(path)
    for file in files:
        if file.endswith('.png'):
            image = load_image(path + '/' + file)
            frame = pyglet.image.AnimationFrame(image, duration)
            frames.append(frame)
    frames[-1].duration = last_duration
    return pyglet.image.Animation(frames)
    
def enable_alpha():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
def copy_coords(dest, src):
    dest.x = src.x
    dest.y = src.y
    
def sum_coords(coords):
    if coords:
        x = sum(x for x, y in coords)
        y = sum(y for x, y in coords)
    else:
        x = 0
        y = 0
    return (x, y)
    
def distance(a, b):
    x1, y1, r1 = a
    x2, y2, r2 = b
    dx = x1 - x2
    dy = y1 - y2
    d = (dx * dx + dy * dy) ** 0.5
    return d
    
def collide(a, b):
    x1, y1, r1 = a
    x2, y2, r2 = b
    r = r1 + r2
    if abs(x1 - x2) > r or abs(y1 - y2) > r:
        return False 
    d = distance(a, b)
    return d < r
    
def unit_vector(a, b):
    dx = b.x - a.x
    dy = b.y - a.y
    length = (dx * dx + dy * dy) ** 0.5
    return dx / length, dy / length
    
def min_xyr_spacing(xyr, xyrs):
    def spacing(a, b):
        x1, y1, r1 = a
        x2, y2, r2 = b
        d = distance(a, b)
        d = d - r1 - r2
        return d
    if xyrs:
        return min(spacing(xyr, other) for other in xyrs)
    else:
        return None
        
# Geometry Functions
def dot(a, b, c):
    ab = (b[0]-a[0], b[1]-a[1])
    bc = (c[0]-b[0], c[1]-b[1])
    return ab[0] * bc[0] + ab[1] * bc[1]
    
def cross(a, b, c):
    ab = (b[0]-a[0], b[1]-a[1])
    ac = (c[0]-a[0], c[1]-a[1])
    return ab[0] * ac[1] - ab[1] * ac[0]
        
def line_point_distance(a, b, c, segment=True):
    if a == b:
        return distance(a, c)
    if segment:
        d1 = dot(a, b, c)
        if d1 > 0: return distance(b, c)
        d2 = dot(b, a, c)
        if d2 > 0: return distance(a, c)
    return abs(cross(a, b, c) / distance(a, b))
    
def box(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    l, t = min(x1, x2), min(y1, y2)
    r, b = max(x1, x2), max(y1, y2)
    return l, t, r, b
    
def segment_intersection(pa1, pa2, pb1, pb2):
    a1 = pa2[1] - pa1[1]
    b1 = pa1[0] - pa2[0]
    c1 = a1 * pa1[0] + b1 * pa1[1]
    a2 = pb2[1] - pb1[1]
    b2 = pb1[0] - pb2[0]
    c2 = a2 * pb1[0] + b2 * pb1[1]
    det = float(a1 * b2 - a2 * b1)
    if det == 0: return None
    x = (b2 * c1 - b1 * c2) / det
    y = (a1 * c2 - a2 * c1) / det
    l1, t1, r1, b1 = box(pa1, pa2)
    l2, t2, r2, b2 = box(pb1, pb2)
    if x < l1 or x < l2: return None
    if x > r1 or x > r2: return None
    if y < t1 or y < t2: return None
    if y > b1 or y > b2: return None
    return int(x), int(y)
    
def segments_intersection(segments, p1, p2):
    for segment in segments:
        pa1, pa2 = segment
        intersection = segment_intersection(pa1, pa2, p1, p2)
        if intersection: return intersection
    return None
    
def rectangle_segment_intersection(x, y, w, h, p1, p2):
    r, b = x+w, y+h
    segments = [((x,y),(r,y)), ((r,y),(r,b)), ((r,b),(x,b)), ((x,b),(x,y))]
    for segment in segments:
        pa1, pa2 = segment
        intersection = segment_intersection(pa1, pa2, p1, p2)
        if intersection: return intersection
    return None
    
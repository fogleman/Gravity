import util

G = 8e-6

class Body(object):
    def __init__(self, x, y, r, fixed=True):
        self.x = x
        self.y = y
        self.r = r
        self.fixed = fixed
        self.dx = 0
        self.dy = 0
    @property
    def xyr(self):
        return (self.x, self.y, self.r)
    @property
    def mass(self):
        return self.r ** 3
    def move(self):
        self.x += self.dx
        self.y += self.dy
    def force(self, dx, dy):
        self.dx += dx
        self.dy += dy
        
def update(bodies):
    results = {}
    for body in bodies:
        if body.fixed:
            continue
        tx, ty = 0, 0
        for other in bodies:
            if other == body:
                continue
            dist2 = (body.x - other.x) ** 2 + (body.y - other.y) ** 2
            magnitude = G * other.mass / dist2
            dx, dy = util.unit_vector(body, other)
            dx, dy = dx * magnitude, dy * magnitude
            tx, ty = tx + dx, ty + dy
        # TODO: sound based on G forces
        #tt = abs(tx) + abs(ty)
        #print int(tt / G)
        results[body] = (tx, ty)
    for body, (dx, dy) in results.iteritems():
        body.force(dx, dy)
        body.move()
        
import math
import physics
import random
import util
from pyglet.gl import *

PLANETS = [
    'images/earth.png',
    'images/moon.png',
    'images/callisto.png',
    'images/europa.png',
    #'images/ganymede.png',
    'images/io.png',
]

class Group(pyglet.graphics.OrderedGroup):
    def __init__(self, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)
        self.dx = 0
        self.dy = 0
    def set_state(self):
        glPushMatrix()
        glTranslatef(self.dx, self.dy, 0)
    def unset_state(self):
        glPopMatrix()
        
batch = pyglet.graphics.Batch()
background = Group(0)
planets = Group(1)
waypoints = Group(2)
ships = Group(3)
pointers = Group(4)

class WaypointHit(object):
    def __init__(self, x, y):
        image = util.load_image('images/star_blue.png')
        self.t = 0
        self.x = x
        self.y = y
        sprites = []
        for angle in range(10):
            sprite = pyglet.sprite.Sprite(image, x=x, y=y, batch=batch, group=waypoints)
            sprite._angle = random.randint(0, 359)
            sprite._speed = random.randint(20, 100)
            sprite._rot = random.randint(0, 359)
            sprite._mul = random.randint(-360, 360)
            sprites.append(sprite)
        self.sprites = sprites
        self.update(0)
    def update(self, dt):
        self.t += dt
        t = self.t
        for sprite in self.sprites:
            sprite.opacity = max(0, int(255 - 255 * t))
            sprite.scale = t / 16
            sprite.rotation = sprite._rot + t * sprite._mul
            d = t * sprite._speed
            sprite.x = self.x + math.cos(math.radians(sprite._angle)) * d
            sprite.y = self.y + math.sin(math.radians(sprite._angle)) * d
        if t < 1:
            pyglet.clock.schedule_once(self.update, 0)
        else:
            for sprite in self.sprites:
                sprite.delete()
                
class PlanetHit(object):
    def __init__(self, x, y):
        image = util.load_image('images/smoke.png')
        self.t = 0
        self.x = x
        self.y = y
        sprites = []
        for angle in range(10):
            sprite = pyglet.sprite.Sprite(image, x=x, y=y, batch=batch, group=waypoints)
            sprite._angle = random.randint(0, 359)
            sprite._speed = random.randint(0, 50)
            sprite._rot = random.randint(0, 359)
            sprite._mul = random.randint(-180, 180)
            sprites.append(sprite)
        self.sprites = sprites
        self.update(0)
    def update(self, dt):
        self.t += dt
        t = self.t
        for sprite in self.sprites:
            sprite.opacity = max(0, int(255 - 255 * t))
            sprite.scale = t / 4
            sprite.rotation = sprite._rot + t * sprite._mul
            d = t * sprite._speed
            sprite.x = self.x + math.cos(math.radians(sprite._angle)) * d
            sprite.y = self.y + math.sin(math.radians(sprite._angle)) * d
        if t < 1:
            pyglet.clock.schedule_once(self.update, 0)
        else:
            for sprite in self.sprites:
                sprite.delete()
                
class Ship(object):
    def __init__(self, x, y):
        image_on = util.load_image('images/ship2-on.png')
        image_off = util.load_image('images/ship2-off.png')
        self.sprite_on = pyglet.sprite.Sprite(image_on, x=x, y=y, batch=batch, group=ships)
        self.sprite_off = pyglet.sprite.Sprite(image_off, x=x, y=y, batch=batch, group=ships)
        self.sprite = self.sprite_off
        self.body = physics.Body(x, y, 12, fixed=False)
        self.fuel_usage = 0
    def thrust(self, dx, dy):
        # set sprite
        if dx or dy:
            self.sprite_on.visible = True
            self.sprite_off.visible = False
            self.fuel_usage += 1
        else:
            self.sprite_on.visible = False
            self.sprite_off.visible = True
        # update body
        power = 1e-4
        fx = dx * power
        fy = dy * power
        self.body.force(fx, fy)
        # set rotation
        mapping = {
            (0, 1): 0,
            (1, 1): 45,
            (1, 0): 90,
            (1, -1): 135,
            (0, -1): 180,
            (-1, -1): 225,
            (-1, 0): 270,
            (-1, 1): 315,
        }
        if (dx, dy) in mapping:
            rotation = mapping[(dx, dy)]
            self.sprite_on.rotation = rotation
            self.sprite_off.rotation = rotation
    @property
    def xyr(self):
        return self.body.xyr
        
class Planet(object):
    def __init__(self, x, y, r):
        image = util.load_image(random.choice(PLANETS))
        self.sprite = pyglet.sprite.Sprite(image, x=x, y=y, batch=batch, group=planets)
        self.sprite.scale = float(r) / (image.width / 2)
        self.sprite.rotation = random.randint(0, 359)
        self.body = physics.Body(x, y, r)
    @property
    def xyr(self):
        return self.body.xyr
        
class Waypoint(object):
    def __init__(self, x, y, r):
        self.r = r
        #image = util.load_image('images/waypoint.png')
        image = util.load_animation('images/waypoint', 0.01, 0.5)
        self.sprite = pyglet.sprite.Sprite(image, x=x, y=y, batch=batch, group=waypoints)
    def __del__(self):
        self.sprite.delete()
    @property
    def xyr(self):
        return (self.sprite.x, self.sprite.y, self.r)
        
class Level(object):
    def __init__(self):
        self.ships = []
        self.planets = []
        self.waypoints = []
        self.stars = create_stars(200, 4, 14)
        self.offset = (0, 0)
    def clear_cache(self):
        if hasattr(self, '_entities'):
            del self._entities
        if hasattr(self, '_bodies'):
            del self._bodies
        if hasattr(self, '_sprites'):
            del self._sprites
    @property
    def entities(self):
        if not hasattr(self, '_entities'):
            self._entities = self.planets + self.waypoints + self.ships
        return self._entities
    @property
    def bodies(self):
        if not hasattr(self, '_bodies'):
            self._bodies = [entity.body for entity in self.entities if hasattr(entity, 'body')]
        return self._bodies
    @property
    def sprites(self):
        if not hasattr(self, '_sprites'):
            self._sprites = [entity.sprite for entity in self.entities]
        return self._sprites
    def update(self):
        physics.update(self.bodies)
        self.do_collisions()
    def draw(self):
        for ship in self.ships:
            util.copy_coords(ship.sprite_on, ship.body)
            util.copy_coords(ship.sprite_off, ship.body)
            if 1:
                left = 960 / 3
                right = 960 - left
                top = 640 / 3
                bottom = 640 - top
                dx, dy = self.offset
                sx, sy = int(ship.body.x), int(ship.body.y)
                if sx + dx < left:
                    dx += left - sx - dx
                if sx + dx > right:
                    dx -= sx - right + dx
                if sy + dy < top:
                    dy += top - sy - dy
                if sy + dy > bottom:
                    dy -= sy - bottom + dy
                self.offset = (dx, dy)
                for group in [planets, waypoints, ships]:
                    #group.dx = 960 / 2 - ship.body.x
                    #group.dy = 640 / 2 - ship.body.y
                    group.dx = dx
                    group.dy = dy
                for group in [background]:
                    group.dx = dx / 8
                    group.dy = dy / 8
        pointers = self.create_pointers()
        batch.draw()
    def create_pointers(self):
        sprites = []
        image = util.load_image('images/pointer.png')
        x, y = 50, 50
        w, h = 960 - x * 2, 640 - y * 2
        ox, oy = self.offset
        for ship in self.ships:
            sx, sy = ship.sprite.x, ship.sprite.y
            for waypoint in self.waypoints:
                wx, wy = waypoint.sprite.x, waypoint.sprite.y
                dx, dy = wx - sx, wy - sy
                angle = -math.degrees(math.atan2(dy, dx))
                p2 = (int(sx + ox), int(sy + oy))
                p1 = (int(wx + ox), int(wy + oy))
                intersection = util.rectangle_segment_intersection(x, y, w, h, p1, p2)
                if intersection:
                    ix, iy = intersection
                    sprite = pyglet.sprite.Sprite(image, x=ix, y=iy, batch=batch, group=pointers)
                    sprite.rotation = angle
                    sprites.append(sprite)
        return sprites
    def do_collisions(self):
        for ship in self.ships:
            for planet in self.planets:
                if util.collide(ship.xyr, planet.xyr):
                    self.on_planet_collision(ship, planet)
            for waypoint in self.waypoints:
                if util.collide(ship.xyr, waypoint.xyr):
                    self.on_waypoint_collision(ship, waypoint)
    def on_planet_collision(self, ship, planet):
        print ship, planet
        self.ships.remove(ship)
        self.clear_cache()
        x1, y1 = ship.body.x, ship.body.y
        x2, y2 = planet.body.x, planet.body.y
        x = x1 + (x2 - x1) / 3
        y = y1 + (y2 - y1) / 3
        PlanetHit(x, y)
    def on_waypoint_collision(self, ship, waypoint):
        print ship, waypoint
        self.waypoints.remove(waypoint)
        self.clear_cache()
        WaypointHit(waypoint.sprite.x, waypoint.sprite.y)
        
def create_stars(count, min_size, max_size):
    sprites = []
    image = util.load_image('images/star.png')
    pad = 100
    for i in range(count):
        size = random.randint(min_size, max_size)
        x = random.randint(0 - pad, 960 + pad)
        y = random.randint(0 - pad, 640 + pad)
        sprite = pyglet.sprite.Sprite(image, x=x, y=y, batch=batch, group=background)
        sprite.scale = float(size) / image.width
        sprite.rotation = random.randint(0, 359)
        p = float(size - min_size) / float(max_size - min_size)
        sprite.opacity = (255 - 64) * p + 64
        sprites.append(sprite)
    return sprites
    
def random_level(width, height, padding, n_ships, n_planets, n_waypoints):
    xyrs = []
    # Ships
    ships = []
    for i in range(n_ships): # TODO: handle multiple?
        x = width / 2
        y = height / 2
        ship = Ship(x, y)
        ships.append(ship)
        xyr = (x, y, 100)
        xyrs.append(xyr)
    # Planets
    planets = []
    for i in range(n_planets):
        while True:
            r = random.randint(30, 60)
            p = r + padding
            x = random.randint(p, width - p)
            y = random.randint(p, height - p)
            xyr = (x, y, r)
            if util.min_xyr_spacing(xyr, xyrs) < padding:
                continue
            planet = Planet(x, y, r)
            planets.append(planet)
            xyrs.append(xyr)
            break
    # Waypoints
    waypoints = []
    for i in range(n_waypoints):
        while True:
            r = 20
            p = r + padding
            x = random.randint(p, width - p)
            y = random.randint(p, height - p)
            xyr = (x, y, r)
            if util.min_xyr_spacing(xyr, xyrs) < padding:
                continue
            waypoint = Waypoint(x, y, r)
            waypoints.append(waypoint)
            xyrs.append(xyr)
            break
    # Level
    level = Level()
    level.ships = ships
    level.planets = planets
    level.waypoints = waypoints
    return level
    
def level1():
    width = 960
    height = 640
    mx = width / 2
    my = height / 2
    # Ships
    ships = []
    for i in range(1): # TODO: handle multiple?
        x = width / 2
        y = height / 2
        ship = Ship(x, y)
        ships.append(ship)
    # Planets
    planets = []
    planets.append(Planet(mx - 200, my, 50))
    planets.append(Planet(mx + 200, my, 50))
    # Waypoints
    waypoints = []
    waypoints.append(Waypoint(mx - 300, my, 20))
    waypoints.append(Waypoint(mx + 300, my, 20))
    waypoints.append(Waypoint(mx, my - 200, 20))
    waypoints.append(Waypoint(mx, my + 200, 20))
    # Level
    level = Level()
    level.ships = ships
    level.planets = planets
    level.waypoints = waypoints
    return level
    
from pyglet.gl import *
from pyglet.window import key
import model
import overlay
import pyglet
import time
import util

WIDTH = 960
HEIGHT = 640

KEY_MAPPING = {
    key.UP: (0, 1),
    key.DOWN: (0, -1),
    key.LEFT: (-1, 0),
    key.RIGHT: (1, 0),
}

class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.reset()
        self.thrusts = set()
        self.mask1 = self.load_mask('images/mask1.jpg', 48)
        self.mask2 = self.load_mask('images/mask2.png', 64)
        pyglet.clock.schedule(self.update)
    def reset(self):
        self.level = model.random_level(WIDTH, HEIGHT, 25, 1, 5, 5)
        #self.level = model.level1()
        # gravity overlay
        bodies = [planet.body for planet in self.level.planets]
        self.overlay = None#overlay.gravity_map(bodies, (0, 0, WIDTH, HEIGHT), 8)
        self.elapsed = 0
        self.start_time = time.clock()
    def load_mask(self, path, opacity):
        image = pyglet.image.load(path)
        sprite = pyglet.sprite.Sprite(image)
        sprite.opacity = opacity
        return sprite
    def get_ship(self):
        return self.level.ships[0] if self.level.ships else None
    def update(self, dt):
        # tick for each millisecond elapsed
        millis = int(round(dt * 1000))
        for i in range(millis):
            self.level.update()
            # apply ship thrust
            ship = self.get_ship()
            if ship:
                ship.thrust(*util.sum_coords(self.thrusts))
            # update elapsed time
            if ship and self.level.waypoints:
                self.elapsed = time.clock() - self.start_time
    def on_draw(self):
        self.clear()
        if self.overlay:
            self.overlay.blit(0, 0)
        self.mask1.draw()
        self.level.draw()
        self.mask2.draw()
        # Fuel Label
        ship = self.get_ship()
        fuel_usage = ship.fuel_usage if ship else 0
        label = pyglet.text.Label('Fuel: %d' % fuel_usage, x=WIDTH-10-25, y=HEIGHT-10-25, font_size=18, bold=True, anchor_x='right', anchor_y='top')
        label.draw()
        # Time Label
        label = pyglet.text.Label('Time: %.1f' % self.elapsed, x=10+25, y=HEIGHT-10-25, font_size=18, bold=True, anchor_y='top')
        label.draw()
    def on_key_press(self, symbol, modifiers):
        if symbol in KEY_MAPPING:
            self.thrusts.add(KEY_MAPPING[symbol])
        if symbol == key.SPACE:
            self.reset()
    def on_key_release(self, symbol, modifiers):
        if symbol in KEY_MAPPING:
            self.thrusts.discard(KEY_MAPPING[symbol])
            
def main():
    window = Window(width=WIDTH, height=HEIGHT, caption='Gravity')
    util.enable_alpha()
    pyglet.app.run()
    
if __name__ == '__main__':
    main()
    

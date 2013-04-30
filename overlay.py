import Image
import ImageDraw
import math
import physics
import pyglet
import util

def gravity_map(bodies, box, step):
    left, top, right, bottom = box
    width, height = right - left, bottom - top
    image = Image.new('L', (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(top, bottom + 1, step):
        for x in range(left, right + 1, step):
            tx = 0
            ty = 0
            cx = x + step / 2
            cy = y + step / 2
            body = physics.Body(cx, cy, 0, True)
            for other in bodies:
                dist2 = (body.x - other.x) ** 2 + (body.y - other.y) ** 2
                if dist2 == 0:
                    continue # TODO: max out
                magnitude = physics.G * other.mass / dist2
                dx, dy = util.unit_vector(body, other)
                dx, dy = dx * magnitude, dy * magnitude
                tx, ty = tx + dx, ty + dy
            length = (tx * tx + ty * ty) ** 0.5
            value = int(math.log10(length / physics.G) * 128)
            value = min(255, value)
            value = max(0, value)
            draw.rectangle((x, y, x + step, y + step), fill=value)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    return pyglet.image.ImageData(width, height, 'L', image.tostring(), width * -1)
    
class DiagonalAlgorithm(object):

    def process(self, sprite):
        x = y = 0
        for image in sprite.images:
            image.x = x
            image.y = y
            x += image.absolute_width
            y += image.absolute_height

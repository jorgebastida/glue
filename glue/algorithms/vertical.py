class VerticalAlgorithm(object):

    def process(self, sprite):
        y = 0
        for image in sprite.images:
            image.x = 0
            image.y = y
            y += image.absolute_height

class HorizontalAlgorithm(object):

    def process(self, sprite):
        x = 0
        for image in sprite.images:
            image.y = 0
            image.x = x
            x += image.absolute_width

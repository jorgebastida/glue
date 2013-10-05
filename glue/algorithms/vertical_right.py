class VerticalRightAlgorithm(object):

    def process(self, sprite):
        max_width = max([i.width for i in sprite.images])
        y = 0
        for image in sprite.images:
            image.x = max_width - image.width
            image.y = y
            y += image.absolute_height

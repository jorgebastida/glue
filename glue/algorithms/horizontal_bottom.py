class HorizontalBottomAlgorithm(object):

    def process(self, sprite):
        max_height = max([i.height for i in sprite.images])
        x = 0
        for image in sprite.images:
            image.y = max_height - image.height
            image.x = x
            x += image.absolute_width

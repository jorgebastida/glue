import copy


class SquareAlgorithmNode(object):

    def __init__(self, x=0, y=0, width=0, height=0, used=False,
                 down=None, right=None):
        """Node constructor.

        :param x: X coordinate.
        :param y: Y coordinate.
        :param width: Image width.
        :param height: Image height.
        :param used: Flag to determine if the node is used.
        :param down: Down :class:`~Node`.
        :param right Right :class:`~Node`.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.used = used
        self.right = right
        self.down = down

    def find(self, node, width, height):
        """Find a node to allocate this image size (width, height).

        :param node: Node to search in.
        :param width: Pixels to grow down (width).
        :param height: Pixels to grow down (height).
        """
        if node.used:
            return self.find(node.right, width, height) or self.find(node.down, width, height)
        elif node.width >= width and node.height >= height:
            return node
        return None

    def grow(self, width, height):
        """ Grow the canvas to the most appropriate direction.

        :param width: Pixels to grow down (width).
        :param height: Pixels to grow down (height).
        """
        can_grow_d = width <= self.width
        can_grow_r = height <= self.height

        should_grow_r = can_grow_r and self.height >= (self.width + width)
        should_grow_d = can_grow_d and self.width >= (self.height + height)

        if should_grow_r:
            return self.grow_right(width, height)
        elif should_grow_d:
            return self.grow_down(width, height)
        elif can_grow_r:
            return self.grow_right(width, height)
        elif can_grow_d:
            return self.grow_down(width, height)

        return None

    def grow_right(self, width, height):
        """Grow the canvas to the right.

        :param width: Pixels to grow down (width).
        :param height: Pixels to grow down (height).
        """
        old_self = copy.copy(self)
        self.used = True
        self.x = self.y = 0
        self.width += width
        self.down = old_self
        self.right = SquareAlgorithmNode(x=old_self.width,
                                         y=0,
                                         width=width,
                                         height=self.height)

        node = self.find(self, width, height)
        if node:
            return self.split(node, width, height)
        return None

    def grow_down(self, width, height):
        """Grow the canvas down.

        :param width: Pixels to grow down (width).
        :param height: Pixels to grow down (height).
        """
        old_self = copy.copy(self)
        self.used = True
        self.x = self.y = 0
        self.height += height
        self.right = old_self
        self.down = SquareAlgorithmNode(x=0,
                                        y=old_self.height,
                                        width=self.width,
                                        height=height)

        node = self.find(self, width, height)
        if node:
            return self.split(node, width, height)
        return None

    def split(self, node, width, height):
        """Split the node to allocate a new one of this size.

        :param node: Node to be splitted.
        :param width: New node width.
        :param height: New node height.
        """
        node.used = True
        node.down = SquareAlgorithmNode(x=node.x,
                                        y=node.y + height,
                                        width=node.width,
                                        height=node.height - height)
        node.right = SquareAlgorithmNode(x=node.x + width,
                                         y=node.y,
                                         width=node.width - width,
                                         height=height)
        return node


class SquareAlgorithm(object):

    def process(self, sprite):

        root = SquareAlgorithmNode(width=sprite.images[0].absolute_width,
                                   height=sprite.images[0].absolute_height)

        # Loot all over the images creating a binary tree
        for image in sprite.images:
            node = root.find(root, image.absolute_width, image.absolute_height)
            if node:  # Use this node
                node = root.split(node, image.absolute_width, image.absolute_height)
            else:  # Grow the canvas
                node = root.grow(image.absolute_width, image.absolute_height)

            image.x = node.x
            image.y = node.y

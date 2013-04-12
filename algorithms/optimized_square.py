import math
import copy


class LineSizeExceededError(Exception):
    """Raised if the size of a line is exceeded."""
    pass


class OptimizedSquareAlgorithm(object):

    MAX_WIDTH = 1200
    MIN_WIDTH = 0

    def __init__(self, max_width=None, min_with=None):

        self._min_width = min_with or self.MIN_WIDTH
        self._max_width = max_width or self.MAX_WIDTH

        # optimized_area min optimized area = total area of the image list
        self._optimized_area = 0

        # real area of the list
        self._real_area = 0

        # optimizedwidth
        self._optimized_width = 0
        self._real_width = 0
        self._min_width = 0

        # optimized height
        self._optimized_height = 0
        self._real_height = 0
        self._min_height = 0

        # placement matrix
        self._matrix = None

        # sprite
        self._sprite = None

    def generate_optimize_datas(self):

        for image in self._sprite.images:
            # getting the optimized area
            img_area = image.absolute_width * image.absolute_height
            self._optimized_area += img_area

            # getting the min width of the sprite
            if self._min_width < image.absolute_width:
                self._min_width = image.absolute_width

            # getting the min height
            if self._min_height < image.absolute_height:
                self._min_height = image.absolute_height

        # getting the optimized width / height
        sqrt = math.sqrt(self._optimized_area)
        tmp = min(self._max_width, math.floor(sqrt))
        self._optimized_width = max(self._min_width, tmp)
        ceil = math.ceil(self._optimized_area / self._optimized_width)
        self._optimized_height = max(self._min_height, ceil)

    def process(self, sprite):
        self._sprite = sprite
        self.generate_optimize_datas()

        self._matrix = OptimizedSquareSpriteMatrix(self._optimized_width,
                                                   self._optimized_height)

        for image in self._sprite.images:
            rp = self._matrix.find_a_place(image)
            image.x = rp.x
            image.y = rp.y

        self._real_width = self._matrix.real_width
        self._real_height = self._matrix.real_height
        self._real_area = self._real_width * self._real_height


class OptimizedSquareSpriteMatrix(object):

    def __init__(self, x=0, y=0, min_x=0, min_y=0):

        # _width_left remaining width left on a line
        self._width_left = {}

        # _current_width position of the last pixel on the line
        self._current_width = {}

        # _rectangle_position_list Rectangle positionned list
        self._rectangle_position_list = []

        self._max_x = int(x)
        self._max_y = int(y)
        self._min_x = int(min_x)
        self._min_y = int(min_y)

    @property
    def real_width(self):
        """get the real width of the sprite """
        width = self._max_x
        for rp in self._rectangle_position_list:
            width = max(rp.x + rp.width, width)

        return width

    @property
    def real_height(self):
        """get the real height of the sprite """
        height = self._max_y
        for rp in self._rectangle_position_list:
            height = max(rp.y + rp.height, height)
        return height

    def _push_rectangle(self, rp):
        """Insert a rectangle in the matrix
            :param rp: SpriteRectanglePosition to add.
        """
        # add th rectangle
        self._rectangle_position_list.append(rp)

        # update cursors
        yh = rp.y + rp.height
        for j in xrange(rp.y, yh):
            if self._current_width[j] < (rp.x + rp.width):
                self._current_width[j] = rp.x + rp.width

            if j not in self._width_left or self._width_left[j] == 0:
                self._width_left[j] = self._max_x - rp.width
            else:
                self._width_left[j] -= rp.width

    def is_free(self, x, y, nb=1):
        """is_free checking if the place is free
            :param x: x.
            :param y: y.
            :param nb: nb place to check.
            return True / False
            """

        # if the size is superior than the max, it is not free
        if (x + nb) > self._max_x:
            raise LineSizeExceededError

        for rp in self._rectangle_position_list:
            if ((x >= rp.x) and
                    ((x + nb) <= (rp.x + rp.width)) and
                    (y >= rp.y) and
                    (y < (rp.y + rp.height))):
                return False

        return True

    def _is_rectangle_free(self, rp):
        """
        isRectangeFree Check is a zone is free
            :param rp SpriteRectanglePosition to test
            :return boolean True if free"""
        wx = rp.width + rp.x
        hy = rp.height + rp.y

        for j in range(rp.y, hy):
            if (j not in self._current_width):
                self._current_width[j] = 0

            if (rp.x < self._current_width[j]):
                return self._current_width[j]

        return True

    def optimize_position(self, rp):
        """
        Optimize the position to avoid white space
            :param rp: positionned rectangle
            :return rectangle with new position"""

        # We check the all image height,
        # if we can not put the image a little lower to put it on the right
        for j in range(rp.y, rp.y + rp.height):
            if ((rp.x > 0) and
                    (self._current_width[j] < (rp.x - (rp.width / 2)))):
                # There is a lot of space behind, we put down the image
                tmp_rp = copy.deepcopy(rp)
                tmp_rp.x = self._current_width[j]
                tmp_rp.y = j
                if (self._is_rectangle_free(tmp_rp) is True):
                    return self.optimize_position(tmp_rp)
        return rp

    def find_a_place(self, r, put_it_in=True):
        """
        find a place for a rectange
            :param r: Rectangle
            :param put_it_in: put in if a place is found
            :return RectanglePosition if found"""

        # for each line of the matrix
        j = self._min_y
        while j < self._max_y:
            start = 0

            # let's find a place on the width
            x = self._find_width_in_line(j, r.absolute_width, start)

            while x is not False:
                # if a place is found
                # we make a rectanglePosition
                rp = SpriteRectanglePosition(r.filename, r.absolute_width,
                                             r.absolute_height, x, j)

                # room is free
                blocking_pos = self._is_rectangle_free(rp)
                if blocking_pos:
                    # let's optimize position
                    rp = self.optimize_position(rp)
                    if put_it_in:
                        self._push_rectangle(rp)
                    return rp
                else:
                    # not available, we increment and retest
                    start = blocking_pos

                x = self._find_width_in_line(j, r.absolute_width, start)

            if self._max_y == j + 1:
                self._max_y += 1
            j += 1

        return False

    def _find_width_in_line(self, y, w, start=0):
        """
        _find_width_in_line find a white space in a line
            :param y: line
            :param w: width
            :param start: start of the line"""

        # let's check if there is available space on the line
        if y in self._width_left and w > self._width_left[y]:
            return False

        # for each column
        if y not in self._current_width:
            self._current_width[y] = 0

        i = max(self._min_x, self._current_width[y], start)
        while i < self._max_x:
            try:
                # if the place is free,
                # we keep the position, if not already found
                if (self.is_free(i, y, w)):
                    return i
                else:
                    start += 1
                i = max(self._min_x, self._current_width[y], start)
            except LineSizeExceededError:
                return False
        return False


class SpriteRectangle (object):

    def __init__(self, id, width=1, height=1):

        self.id = id
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.w * self.h

    @property
    def perimeter(self):
        return 2 * self.w + 2 * self.h


class SpriteRectanglePosition (SpriteRectangle):

    def __init__(self, id, width=1, height=1, x=0, y=0):
        super(SpriteRectanglePosition, self).__init__(id, width, height)
        self.x = x
        self.y = y

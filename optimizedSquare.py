#!/usr/bin/env python
import math

class OptimizedSquareAlgorithm (object):
    MAX_WIDTH = 1200
    MIN_WIDTH = 0

    # optimizedArea min optimized area = total area of the image list
    optimizedArea = 0

    # real area of the list
    realArea = 0

    # optimizedWidth
    optimizedWidth = 0
    realWidth = 0
    minWidth = 0

    # optimizedHeight
    optimizedHeight = 0
    realHeight = 0
    minHeight = 0

    # placement matrix
    matrix = None

    # sprite
    sprite = None

    def __init__(self):
        """Node constructor.

        :param sprite: sprite.
        """
        self.minWidth = self.MIN_WIDTH


    def generateOptimizedDatas(self):
        """Generate the optimized datas
        """
        
        for image in self.sprite.images:
            # getting the optimized area
            imgArea = image.absolute_width * image.absolute_height
            self.optimizedArea += imgArea
        
            # getting the min width of the sprite
            if (self.minWidth < image.absolute_width):
                self.minWidth = image.absolute_width

            # getting the min height
            if (self.minHeight < image.absolute_height):
                self.minHeight = image.absolute_height

        
        # getting the optimized width / height
        sqrt = math.sqrt(self.optimizedArea)
        self.optimizedWidth = max(self.minWidth, min(self.MAX_WIDTH, math.floor(sqrt)))
        self.optimizedHeight = max(self.minHeight, math.ceil(self.optimizedArea / self.optimizedWidth))


    def process(self, sprite):
        self.sprite = sprite
        self.generateOptimizedDatas()

        self.matrix = OptimizedSquareSpriteMatrix(self.optimizedWidth, self.optimizedHeight)

        for image in self.sprite.images:
            self.matrix.findAPlace(image)

        self.realWidth = self.matrix.getRealWidth()
        self.realHeight = self.matrix.getRealHeight()
        self.realArea = self.realWidth * self.realHeight



class OptimizedSquareSpriteMatrix (object):
    minX = 0
    maxX = 0
    minY = 0
    maxY = 0

    # widthLeft Taille restante par ligne
    widthLeft = []
    # currentWidth Taille du dernier pixel par ligne
    currentWidth = 0

    # rectanglePositionList Liste des rectangles positionnes
    rectanglePositionList = []

    def __init__(self, x, y, minX = 0, minY = 0):
        self.maxX = int(x)
        self.maxY = int(y)
        self.minX = int(minX)
        self.minY = int(minY)

    def getRealWidth(self):
        """ get the real width of the sprite
        """
        w = self.maxX
        for rp in self.rectanglePositionList:
            w = max(rp.x + rp.w, w)
        
        return w

    def getRealHeight(self):
        """ get the real height of the sprite
        """
        h = self.maxY
        for rp in self.rectanglePositionList:
            h = max(rp.y + rp.h, h)
        return h

    def pushRectangle(self, rp):
        """ pushRectangle insert a rectangle in the matrix
            :param rp: SpriteRectanglePosition to add.
        """
        # add th rectangle
        self.rectanglePositionList.append(rp)

        # update cursors
        yh = rp.y + rp.h
        for j in range(rp.y, yh):
            if (self.currentWidth[j] < (rp.x + rp.w)):
                self.currentWidth[j] = rp.x + rp.w
            
            if (not self.widthLeft[j]):
                self.widthLeft[j] = self.maxX - rp.w
            else:
                self.widthLeft[j] -= rp.w

    def isFree (self, x, y, nb = 1):
        """ isFree checking if the place is free
            :param x: x.
            :param y: y.
            :param nb: nb place to check.
            return True / False
            """

        # if the size is superior than the max, it is not free
        if ((x + nb) > self.maxX):
            raise LineSizeExceeded

        for rp in self.rectanglePositionList:
            if ((x >= rp.x) and ((x + nb) <= (rp.x + rp.w)) and (y >= rp.y) and (y < (rp.y + rp.h))):
                return False

        return True


    def isRectangleFree(self, rp):
        """ isRectangeFree Check is a zone is free
                :param rp SpriteRectanglePosition to test
                :return boolean True if free
        """
        wx = rp.w + rp.x
        hy = rp.h + rp.y

        for j in range(rp.y, hy):
            if (rp.x < self.currentWidth[j]):
                return self.currentWidth[j]

        return True

    def optimizePosition(self, rp):
        """ optimizePosition optimizt the position to avoid white space
                :param rp: positionned rectangle
                :return rectangle with new position
        """
        # We check the all image height, if we can not put the image a little lower to put it on the right
        for j in range(rp.y, rp.y + rp.h) :
            if ((rp.x > 0) and (self.currentWidth[j] < (rp.x - (rp.w / 2)))):
                # There is a lot of space behind, we put down the image
                tmpRp = copy(rp)
                tmpRp.x = self.currentWidth[j]
                tmpRp.y = j
                if (self.isRectangleFree(tmpRp)):
                    return self.optimizePosition(tmpRp)
            return rp

    def findAPlace(self, r, putItIn = True):
        """ find a place for a rectange 
             :param r: Rectangle
             :param putItIn: put in if a place is found
             :return array($x, $y) if found
        """
        # for each line of the matrix
        for j in range(self.minY, self.maxY):
            start = 0

            # let's find a place on the width
            x = self.findWidthInLine(j, r.absolute_width, start)
            print 'thiiii'
            while x != False:
                # if a place is found
                if (x != False):
                    # we make a rectanglePosition
                    rp = SpriteRectanglePosition(r.id, r.w, r.h, x, j)

                    # room is free
                    posBloquante = self.isRectangleFree(rp)
                    if (posBloquante == True):
                        # let's optimize position
                        rp = self.optimizePosition(rp)
                        if (putItIn):
                            self.pushRectangle(rp)
                        return rp
                    else:
                        # not available, we increment and retest
                        start = posBloquante
                else:
                    # no place found
                    break;
                x = self.findWidthInLine(j, r.w, start)

            if (self.maxY == j + 1):
                self.maxY += 1

        return False

    def findWidthInLine(self, y, w, start = 0) :
        """ findWidthInLine find a white space in a line
            :param y: line 
            :param w: width
            :param start: start of the line
            :return void
        """
        # on teste si il reste de la place sur la ligne 
        try:
            if (w > self.widthLeft[y]):
                return False
        except IndexError, e:
		    plop = None

        # variables init
        freeSpace = 0 # free space needed

        # pour chaque colonne
        try:
            cw = self.currentWidth[y]
        except IndexError, e:
		    self.currentWidth[y] = 0

        for i in range(max(self.minX, self.currentWidth[y], start), self.maxX):
            try:
                if (self.isFree(i, y, w)): # if the place is free, we keep the position, if not already found
                    return i
                else:
                    start += 1
            except LineSizeExceeded as e :
				return False
        return False


import Globals
from CanvasV2 import *
import math


class Ngon(DesignObject):
    def customExecute(self):
        n = getParam("n",4)
        r = getParam("r",100)

        angle = 2 * math.pi / n
        points = []
        lines = []
        for i in range(1, n + 1):
            points.append(Point(Globals.origin.x + r * math.cos(angle * i), Globals.origin.y + r * math.sin(angle * i), name=f"point{i}"))
        for i in range(0, n):
            lines.append(Line(points[i - 1], points[i], name=f"line{i}"))
        for i in range(1, n):
            Equal(lines[i - 1], lines[i])
        Line(points[-1], origin, name='ding')





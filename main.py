
import Globals 
from CanvasV2 import *
import math
import test

P5 = Point(0.000, 99.000)

a = test.Test(origin=P5)

# print(globals()['origin'].coordinates())
# fourgon = ngon.Ngon(n=4, r=150, origin=Point(100,100))
# print(globals()['origin'].coordinates())

# n = getParam("n",4)
# r = getParam("r",100)

# angle = 2 * math.pi / n
# points = []
# lines = []
# for i in range(1, n + 1):
#     points.append(Point(origin.x + r * math.cos(angle * i), origin.y + r * math.sin(angle * i), name=f"point{i}"))
# for i in range(0, n):
#     lines.append(Line(points[i - 1], points[i], name=f"line{i}"))
# for i in range(1, n):
#     Equal(lines[i - 1], lines[i])
# Line(points[-1], origin, name='ding')


print(R.output())
printLocals(list(locals().items()))
# print(vars(fourgon).keys())

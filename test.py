import Globals
from CanvasV2 import *
import math

class Test(DesignObject):

	def customExecute(self):
		print("customexecute")
		print(Globals.origin)
		print(Globals.origin.coordinates())
		P2 = Point(-169.500, -21.500)
		P3 = Point(8.000, 231.500)
		L1 = Line(P2, P3)
		P4 = Point(162.000, -40.000)
		L2 = Line(P3, P4)
		L3 = Line(P4, Globals.origin)
		L4 = Line(Globals.origin, P2)
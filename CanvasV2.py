# Author: flx
from enum import Enum

currentObject = None
origin = None

def getParam(name, default):
    global currentObject
    if currentObject == None:
        return default
    else:
        try: 
            a = getattr(currentObject,name)
            return a
        except:
            return default

def printLocals(locallist):
    for k, v in locallist:
        if isinstance(v, DesignObject):
            print(f'#{v.name()}:{k}')

class Recorder:
    def __init__(self):
        self.names = {}
        self.currentSketch = None
        self.sequence = []

    def getCurrentSktech(self):
        if self.currentSketch == None:
            self.currentSketch = Sketch()
        return self.currentSketch

    def appendToSequence(self, el):
        self.sequence.append(el)

    def output(self):
        ostring = ""
        for item in self.sequence:
            ostring += item.output() + "\n"
        return ostring

R = Recorder()

def newNameFu(namestring):
    x = -1
    def nameFu():
        nonlocal x
        x = x + 1
        return namestring + str(x)
    return nameFu


newSketchName = newNameFu("Sketch")
newLineName = newNameFu("L")
newPointName = newNameFu("P")
newCircleName = newNameFu("C")
newObjectName = newNameFu("O")


class DesignObject:
    def __init__(self, **kwargs):
        global currentObject
        if 'addtosequence' in kwargs:
            if kwargs['addtosequence'] == True:
                R.appendToSequence(self)
            else:
                pass
        else:
            R.appendToSequence(self)
        for name, arg in kwargs.items():
            if name == 'name':
                self.nameSuffix = arg
            elif name == 'parent':
                self.parent = arg
                assert isinstance(arg, DesignObject), 'parent parameter must be DesignObject'
                self.parent.insertObject(self)
            else:
                setattr(self, name, arg)
        if 'parent' in kwargs:
            pass
        else:
            if currentObject != None:
                self.parent = currentObject
                assert isinstance(currentObject, DesignObject), 'current Object parameter must be DesignObject'
                self.parent.insertObject(self)
        if 'name' in kwargs:
            pass
        else:
            self.nameSuffix = newObjectName()
        setattr(self,"newLineName",newNameFu("L"))
        setattr(self,"newPointName",newNameFu("P"))
        setattr(self,"newCircleName",newNameFu("C"))
        setattr(self,"newObjectName",newNameFu("O"))
        setattr(self,"newConstraintName",newNameFu("co"))

        if 'origin' in kwargs:
            pass
        else:
            self.origin = origin
        self.swapGlobalsIn()
        self.execute()
        self.swapGlobalsOut()

    def swapGlobalsIn(self):
        global currentObject
        self.swapCurrentObject = currentObject
        currentObject = self

    def swapGlobalsOut(self):
        global currentObject
        currentObject = self.swapCurrentObject

    def execute(self):
        pass
    
    def output(self):
        return f"# DesignObject {self.name()}"

    def name(self):
        if getattr(self, "parent", "notset") == "notset":
            return self.nameSuffix
        else:
            return self.parent.name() + "." + self.nameSuffix
    
    def insertObject(self, object):
        if getattr(object, 'nameSuffix', 'notset') == 'notset':
            setattr(object, 'nameSuffix', self.newConstraintName())
        if getattr(self, object.nameSuffix, "notset") == "notset":
            setattr(self, object.nameSuffix, object)
        else:
            assert False, "object inserted more than once"


class Id(DesignObject):
    def __init__(self, name):
        self.nameSuffix = name


class Sketch(DesignObject):
    def __init__(self, *args):
        self.nameSuffix = newSketchName()
        self.points = []
        self.lines = []
        self.circles = []
        for el in args:
            if isinstance(el, Point):
                self.points += [el]
            elif isinstance(el, Line):
                self.lines += [el]
            else:
                assert False, "Sketch needs to be created with a point and a line"
        R.currentSketch = self
        DesignObject.__init__(self)

    def output(self):
        ostring = f"{self.nameSuffix} = sketch " + " ".join(map(lambda x: x.name, self.points)) + " ".join(
                map(lambda x: x.name, self.lines))
        return ostring

    def switch(self):
        R.print(f"sketch {self.name()}")


class SketchObject(DesignObject):
    def __init__(self, **kwargs):
        DesignObject.__init__(self, **kwargs)
        self.sketch = R.currentSketch
        for name, arg in kwargs.items():
            if name == "sketch":
                assert isinstance(arg, Sketch), "sketch parameter must be sketch object"
                self.sketch = arg


class Point(SketchObject):
    def __init__(self, x, y, **kwargs):
        if "name" in kwargs.keys():
            pass
        else:
            if "parent" in kwargs.keys():
                kwargs["name"] = kwargs['parent'].newPointName()
            else:
                kwargs["name"] = newPointName()
        SketchObject.__init__(self, **kwargs)
        self.sketch = R.getCurrentSktech()
        self.x = x
        self.y = y

    def output(self):
        return f"{self.name()} = point {self.x} {self.y}"

    def coordinates(self):
        return f"{self.x} {self.y}"



class Line(SketchObject):
    def __init__(self, p1, p2, **kwargs):
        if "name" in kwargs.keys():
            pass
        else:
            if "parent" in kwargs.keys():
                kwargs["name"] = kwargs['parent'].newLineName()
            else:
                kwargs["name"] = newLineName()
        SketchObject.__init__(self, **kwargs)
        self.p1 = p1
        self.p2 = p2

    def output(self):
        return f"{self.name()} = line {self.p1.name()} {self.p2.name()}"


class Circle(SketchObject):
    def __init__(self, center, radius, **kwargs):
        if "name" in kwargs.keys():
            pass
        else:
            if "parent" in kwargs.keys():
                kwargs["name"] = kwargs['parent'].newCircleName()
            else:
                kwargs["name"] = newCircleName()
        SketchObject.__init__(self, **kwargs)
        self.center = center
        self.radius = radius
        self.sketch = R.getCurrentSktech()

    def output(self):
        return f"{self.name()} = circle {self.center.name()} {self.radius}"


class Dir(Enum):
    yPlus = "yPlus"
    yMinus = "yMinus"
    xPlus = "xPlus"
    xMinus = "xMinus"
    Point = "Point"


class Op(Enum):
    union = "union"
    difference = "difference"
    intersection = "intersection"


class Constraint(SketchObject):
    def __init__(self, *args):
        self.constraintName = "GenericConstraint"
        self.points = []
        self.lines = []
        self.circles = []
        self.ids = []
        for el in args:
            if isinstance(el, Point):
                self.points += [el]
            elif isinstance(el, Line):
                self.points += [el]
            elif isinstance(el, Circle):
                self.points += [el]
            elif isinstance(el, Id):
                self.ids += [el]
            else:
                assert False, "Non-sketch element used for sketch constraint"
        SketchObject.__init__(self)

    def output(self):
        retstring = self.constraintName
        for p in self.ids:
            retstring = retstring + " " + p.name()
        for p in self.points:
            retstring = retstring + " " + p.name()
        for p in self.lines:
            retstring = retstring + " " + p.name()
        for p in self.circles:
            retstring = retstring + " " + p.name()
        return retstring


# class ParallelToAxisConstraint(Constraint):
#     def __init__(self, *args):
#         Constraint.__init__(self, *args)
#         self.constraintName = "ParallelToAxisConstraint"


# class RefDifference(Constraint):
#     def __init__(self, *args):
#         Constraint.__init__(self, *args)
#         self.constraintName = "RefDifference"


# class PointPlaneCoincident(Constraint):
#     def __init__(self, *args):
#         Constraint.__init__(self, *args)
#         self.constraintName = "coincident"


# class PointLineDistance(Constraint):
#     def __init__(self, *args):
#         Constraint.__init__(self, *args)
#         self.constraintName = "distance"


class Distance(Constraint):
    def __init__(self, *args):
        self.constraintName = "distance"
        self.points = []
        self.lines = []
        self.circles = []
        self.distance = 100.0
        for el in args:
            if isinstance(el, Point):
                self.points += [el]
            elif isinstance(el, Line):
                self.points += [el]
            elif isinstance(el, Circle):
                self.points += [el]
            else:
                self.distance = el
        SketchObject.__init__(self)

    def output(self):
        retstring = self.constraintName
        for p in self.points:
            retstring = retstring + " " + p.name
        for p in self.lines:
            retstring = retstring + " " + p.name
        for p in self.circles:
            retstring = retstring + " " + p.name
        retstring = retstring + f" {self.distance}"
        return retstring


# class SymmetryConstraint(Constraint):
#     def __init__(self, *args):
#         Constraint.__init__(self, *args)
#         self.constraintName = "SymmetryConstraint"


class Collinear(Constraint):
    def __init__(self, *args):
        Constraint.__init__(self, *args)
        self.constraintName = "collinear"


class Concentric(Constraint):
    def __init__(self, *args):
        Constraint.__init__(self, *args)
        self.constraintName = "concentric"


# class FractionConstraint(Constraint):
#     def __init__(self, *args):
#         Constraint.__init__(self, *args)
#         self.constraintName = "FractionConstraint"


# class RefMultiplication(Constraint):
#     def __init__(self, *args):
#         Constraint.__init__(self, *args)
#         self.constraintName = "RefMultiplication"


class Perpendicular(Constraint):
    def __init__(self, *args):
        Constraint.__init__(self, *args)
        self.constraintName = "perpendicular"


class Angle(Constraint):
    def __init__(self, *args):
        self.constraintName = "angle"
        self.points = []
        self.lines = []
        self.circles = []
        self.angle = 10.0
        for el in args:
            if isinstance(el, Point):
                self.points += [el]
            elif isinstance(el, Line):
                self.points += [el]
            elif isinstance(el, Circle):
                self.points += [el]
            else:
                self.angle = el
        SketchObject.__init__(self)

    def output(self):
        retstring = self.constraintName
        for p in self.points:
            retstring = retstring + " " + p.name
        for p in self.lines:
            retstring = retstring + " " + p.name
        for p in self.circles:
            retstring = retstring + " " + p.name
        retstring = retstring + f" {self.angle}"
        return retstring

class Parallel(Constraint):
    def __init__(self, *args):
        Constraint.__init__(self, *args)
        self.constraintName = "parallel"


# class EqualRadius(Constraint):
#     def __init__(self, *args):
#         Constraint.__init__(self, *args)
#         self.constraintName = "EqualRadius"


class Equal(Constraint):
    def __init__(self, *args):
        Constraint.__init__(self, *args)
        self.constraintName = "equal"


class Tangent(Constraint):
    def __init__(self, *args):
        Constraint.__init__(self, *args)
        self.constraintName = "tangent"


class CircleTangentCircle(Constraint):
    def __init__(self, *args):
        Constraint.__init__(self, *args)
        self.constraintName = "tangent"


class LineTangentCircle(Constraint):
    def __init__(self, *args):
        Constraint.__init__(self, *args)
        self.constraintName = "tangent"


class PointLineCoincident(Constraint):
    def __init__(self, *args):
        Constraint.__init__(self, *args)
        self.constraintName = "coincident"


class Horizontal(Constraint):
    def __init__(self, *args):
        Constraint.__init__(self, *args)
        self.constraintName = "horizontal"


class Vertical(Constraint):
    def __init__(self, *args):
        Constraint.__init__(self, *args)
        self.constraintName = "vertical"


class Length(Constraint):
    def __init__(self, *args):
        self.constraintName = "length"
        self.points = []
        self.lines = []
        self.circles = []
        self.distance = 100.0
        for el in args:
            if isinstance(el, Point):
                self.points += [el]
            elif isinstance(el, Line):
                self.points += [el]
            elif isinstance(el, Circle):
                self.points += [el]
            else:
                self.distance = el
        SketchObject.__init__(self)

    def output(self):
        retstring = self.constraintName
        for p in self.points:
            retstring = retstring + " " + p.name
        for p in self.lines:
            retstring = retstring + " " + p.name
        for p in self.circles:
            retstring = retstring + " " + p.name
        retstring = retstring + f" {self.distance}"
        return retstring


class Extrusion(DesignObject):
    def __init__(self, sketch, elements, height, distance, direction):
        self.nameSuffix = newObjectName()
        self.sketch = sketch
        self.elements = elements
        self.height = height
        self.distance = distance
        self.direction = direction
        SketchObject.__init__(self)

    def output(self):
        return f"{self.nameSuffix} = extrude {self.sketch.name} {self.height} {self.distance} {self.direction.name} " + " ".join(
                map(lambda x: x.name, self.elements))


class Revolution(DesignObject):
    def __init__(self, sketch, elements, direction, axis):
        self.nameSuffix = newObjectName()
        self.sketch = sketch
        self.elements = elements
        self.axis = axis
        self.direction = direction
        SketchObject.__init__(self)

    def output(self):
        return f"{self.nameSuffix} = revolve {sketch.name} {self.axis.name}  {self.direction.name} " + " ".join(
            map(lambda x: x.name, self.elements))


origin = Point(0, 0, name=f'origin', addtosequence=False)

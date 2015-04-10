#!/usr/bin/python

import lldb
import fblldbbase as fb
import re

def lldbcommands():
    return [
        VisualizeRect(),
        VisualizePoint()
    ]

class VisualizeRect(fb.FBCommand):
    def name(self):
        return "vrect"

    def description(self):
        return "Visualizes a CGRect in a view."

    def args(self):
        return [
            fb.FBCommandArgument(arg="rect", type="CGRect", help="The rect that should be visualized."),
            fb.FBCommandArgument(arg="coordinateReferenceView", type="UIView *", help="The rect should be specified in the coordinate system of this view.")
        ]

    def run(self, arguments, options):
        visualizeRect(arguments[0], arguments[1])

class VisualizePoint(fb.FBCommand):
    def name(self):
        return "vpoint"

    def description(self):
        return "Visualizes a CGPoint in a view."

    def args(self):
        return [
            fb.FBCommandArgument(arg="point", type="CGPoint", help="The point that should be visualized."),
            fb.FBCommandArgument(arg="coordinateReferenceView", type="UIView *", help="The point should be specified in the coordinate system of this view.")
        ]

    def run(self, arguments, options):
        visualizePoint(arguments[0], arguments[1])

def visualizePoint(point, referenceView):
    refView = fb.evaluateObjectExpression(referenceView)
    targetPointExpression = "(CGPoint)[(UIView*){:s} convertPoint:(CGPoint){:s} toView:(UIView*)[{:s} window]]".format(refView, point, refView)
    viewFrame = "(CGRect)CGRectMake(0, 0, 4, 4)"
    overlayView = fb.evaluateObjectExpression("(UIView*)[[UIView alloc] initWithFrame:{:s}]".format(viewFrame))
    lldb.debugger.HandleCommand("exp (void)[(UIView*){:s} setCenter:(CGPoint){:s}]".format(overlayView, targetPointExpression))
    lldb.debugger.HandleCommand("exp (void)[(UIView*)[{} window] addSubview:(UIView*){}]".format(refView, overlayView))
    lldb.debugger.HandleCommand("exp (void)[(UIView*){} setUserInteractionEnabled:NO]".format(overlayView))
    lldb.debugger.HandleCommand("border {:s}".format(overlayView))
    print "Visualized {:s} using {}".format(point, overlayView)

def visualizeRect(rect, referenceView):
    refView = fb.evaluateObjectExpression(referenceView)
    targetRectExpression = "(CGRect)[(UIView*){:s} convertRect:(CGRect){:s} toView:(UIView*)[{:s} window]]".format(refView, rect, refView)
    overlayView = fb.evaluateObjectExpression("(UIView*)[[UIView alloc] initWithFrame:(CGRect){:s}]".format(targetRectExpression))
    lldb.debugger.HandleCommand("exp (void)[(UIView*)[{} window] addSubview:(UIView*){}]".format(refView, overlayView))
    lldb.debugger.HandleCommand("exp (void)[(UIView*){} setUserInteractionEnabled:NO]".format(overlayView))
    lldb.debugger.HandleCommand("border {:s}".format(overlayView))
    lldb.debugger.HandleCommand("caflush")

    print "Visualized {:s} using {}".format(rect, overlayView)

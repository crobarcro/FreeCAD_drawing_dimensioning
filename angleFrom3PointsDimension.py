# This Python file uses the following encoding: utf-8
from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *

dimensioning = DimensioningProcessTracker()

def angleFrom3PointsDimensionSVG( p1x, p1y, p2x, p2y, p3x, p3y, x_baseline, y_baseline,
                                  x_text=None, y_text=None, 
                                  textFormat='%3.1f°',
                                  gap_datum_points = 2,
                                  dimension_line_overshoot=1,
                                  arrowL1=3, arrowL2=1, arrowW=2, svgTag='g', svgParms='', strokeWidth=0.5, lineColor='blue', 
                                  textRenderer=defaultTextRenderer ):
    """
    Create an angle dimension by specifying three points, the center and two others
    """

    XML = []
    #x_int, y_int = lineIntersection(line1, line2)
    #XML.append( '<circle cx ="%f" cy ="%f" r="4" stroke="none" fill="rgb(0,0,255)" /> ' % (x_int, y_int) ) #for debugging
    p_center = numpy.array([ p1x, p1y ] )
    p1 = numpy.array( [p1x, p1y] )
    p2 = numpy.array( [p2x, p2y] )
    p3 = numpy.array( [p1x, p1y] )
    p4 = numpy.array( [p3x, p3y] )
    #XML.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,255,0);stroke-width:3" />' % (p1[0],p1[1],p2[0],p2[1]) )
    #XML.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,255,0);stroke-width:3" />' % (p3[0],p3[1],p4[0],p4[1]) )

    p5 = numpy.array([ x_baseline, y_baseline ])
    r_P5 = norm( p5 -p_center )

    # function to determine the correct arrow position
    def arrowPosition( d ):
        cand1 = p_center + d*r_P5
        cand2 = p_center - d*r_P5
        return cand1 if norm( cand1 - p5) < norm( cand2 - p5) else cand2

    p_arrow1 = arrowPosition(directionVector(p1,p2))
    p_arrow2 = arrowPosition(directionVector(p3,p4))

    # function used to generate line from the desired
    # position to the arrow tip
    def line_to_arrow_point( a, b, c): # where a=p1,b=p2 or a=p3,b=p4 and c=p_arrow1 or c=p_arrow2
        if abs( norm(a -b) - (norm(a-c) + norm(b-c))) < norm(a -b)/1000:
            return
        s = a if norm(a-c) < norm(b-c) else b #start_point
        d = directionVector( s, c)
        v = s + gap_datum_points*d
        w = c + dimension_line_overshoot*d
        XML.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%f" />' % (v[0],v[1],w[0],w[1], lineColor, strokeWidth) )

    line_to_arrow_point( p1, p2, p_arrow1)
    line_to_arrow_point( p3, p4, p_arrow2)

    d1 = directionVector(p_center, p_arrow1)
    d2 = directionVector(p_center, p_arrow2)

    largeArc = False # given the selection method for the arrow heads (points and line1 and line2 used for measuring the angle)
    angle_1 = arctan2( d2[1], d2[0] )
    angle_2 = arctan2( d1[1], d1[0] )
    if abs(angle_1 - angle_2) < pi: #modulo correction required, since arctan2 return [-pi, pi]
        if angle_2 < angle_1:
            angle_2 = angle_2 + 2*pi
        else:
            angle_1 = angle_1 + 2*pi
    sweep = angle_2 > angle_1
    #rX, rY, xRotation, largeArc, sweep, _end_x, _end_y =
    XML.append('<path d = "M %f %f A %f %f 0 %i %i %f %f" style="stroke:%s;stroke-width:%1.2f;fill:none" />' % (p_arrow1[0],p_arrow1[1], r_P5, r_P5, largeArc, sweep, p_arrow2[0],p_arrow2[1],lineColor, strokeWidth))

    s = 1 if angle_2 > angle_1 else -1
    XML.append( arrowHeadSVG( p_arrow1, rotate2D(d1, s*pi/2), arrowL1, arrowL2, arrowW, lineColor ) )
    XML.append( arrowHeadSVG( p_arrow2, rotate2D(d2,-s*pi/2), arrowL1, arrowL2, arrowW, lineColor ) )

    if x_text <> None and y_text <> None:
        v = arccos( numpy.dot(d1, d2) )/ pi * 180
        textRotation = numpy.arctan2( y_text - p1y, x_text - p1x)
        textXML = textRenderer( x_text, y_text, dimensionText(v,textFormat), textRotation)
        textXML = textXML + '\n <!--%s-->' % v
        textXML = textXML + '\n <!--%s-->' % textFormat
        XML.append( textXML )
    XML = '''<%s  %s >
 %s
</%s> ''' % ( svgTag, svgParms, '\n'.join(XML), svgTag )
    return XML


def selectFun( event, referer, elementXML, elementParms, elementViewObject ):
    x, y = elementParms['x'], elementParms['y']
    debugPrint(2, 'selecting point %i with x=%3.1f y=%3.1f' % (dimensioning.stage, x,y) )
    referer.lockSelection()
    if dimensioning.stage == 0: #then select line1
        dimensioning.point1 = x,y
        dimensioning.stage = 1
    elif dimensioning.stage == 1:
        dimensioning.point2 = x,y
        dimensioning.stage = 2
    else:
        dimensioning.point3 = x,y
        dimensioning.stage = 3
        selectionOverlay.hideSelectionGraphicsItems()
        previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )

def clickFunPreview( x, y ):
    if dimensioning.stage == 3:
        dimensioning.point4 = x, y
        debugPrint(2, 'base-line point set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 4
        return None, None
    else:
        XML = angleFrom3PointsDimensionSVG( dimensioning.point1[0], dimensioning.point1[1],
                                            dimensioning.point2[0], dimensioning.point2[1],
                                            dimensioning.point3[0], dimensioning.point3[1],
                                            dimensioning.point4[0], dimensioning.point4[1],
                                            x, y,
                                            **dimensioning.dimensionConstructorKWs)

        return findUnusedObjectName('dim'), XML

def hoverFunPreview( x, y ):
    if dimensioning.stage == 3:
        # at this point we've picked the two lines and are
        # preparing to select where the angle dimension will
        # be shown
        return angleFrom3PointsDimensionSVG( dimensioning.point1[0], dimensioning.point1[1],
                                             dimensioning.point2[0], dimensioning.point2[1],
                                             dimensioning.point3[0], dimensioning.point3[1],
                                             x, y,
                                             **dimensioning.svg_preview_KWs)
    else:
        return angleFrom3PointsDimensionSVG( dimensioning.point1[0], dimensioning.point1[1],
                                             dimensioning.point2[0], dimensioning.point2[1],
                                             dimensioning.point3[0], dimensioning.point3[1],
                                             dimensioning.point4[0], dimensioning.point4[1],
                                             x, y,
                                             **dimensioning.svg_preview_KWs )

#selection variables for angular dimensioning
maskBrush  =   QtGui.QBrush( QtGui.QColor(0,160,0,100) )
maskPen =      QtGui.QPen( QtGui.QColor(0,160,0,100) )
maskPen.setWidth(0.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(0.0)

class angleFrom3PointsDimension:
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate(V, ['strokeWidth','arrowL1','arrowL2','arrowW','gap_datum_points', 'dimension_line_overshoot'], ['lineColor'], ['textRenderer'] )
        commonArgs = dict(
            onClickFun=selectFun,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene,
            pointWid=1.0,
            maskPen=maskPen,
            maskHoverPen=maskHoverPen,
            maskBrush = maskBrush
            )
        selectionOverlay.generateSelectionGraphicsItems(
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim') and not obj.Name.startswith('center')],
            doPoints=True,
            **commonArgs
            )
        selectionOverlay.generateSelectionGraphicsItems(
            [obj for obj in V.page.Group if obj.Name.startswith('center')],
            clearPreviousSelectionItems = False,
            doPathEndPoints=True,
            **commonArgs
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)

    def GetResources(self):
        return {
            'Pixmap' : os.path.join( iconPath , 'angleFrom3PointsDimension.svg' ) ,
            'MenuText': 'Angular Dimension From Points',
            'ToolTip': 'Creates an angular dimension from 3 points'
            }

FreeCADGui.addCommand('dd_angleFrom3PointsDimension', angleFrom3PointsDimension())

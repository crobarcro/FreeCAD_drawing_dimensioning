
from dimensioning import *
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *

dimensioning = DimensioningProcessTracker()

def radiusDimensionInnerSVG( center_x, center_y,
                             radius,
                             radialLine_x=None, radialLine_y=None,
                             radialLine2_x=None, radialLine2_y=None,
                             tail_x=None, tail_y=None,
                             text_x=None, text_y=None,
                             textFormat='R%3.3f', centerPointDia = 1, arrowL1=3, arrowL2=1, arrowW=2, svgTag='g', svgParms='', strokeWidth=0.5, dimScale=1.0, lineColor='blue', textRenderer=defaultTextRenderer):
    """
    Creates a radial dimension with the label drawn on the 'inside' of the radius,
    and control over the length of the tail towards the centre point of the radius
    """
    # initialise the svg with a
    XML_body = []
    #XML_body = [ ' <circle cx ="%f" cy ="%f" r="%f" stroke="none" fill="%s" /> ' % (center_x, center_y, centerPointDia*0.5, lineColor) ]

    if radialLine_x <> None and radialLine_y <> None:
        # second stage of drawing, the radial line
        # here we need to draw the arrow and a line going from the base of the
        # arrow towards the centre of the circle, of length determined by the
        # cursor position
        theta = numpy.arctan2( radialLine_y - center_y, radialLine_x - center_x )

        # create two vectors to be used to determine the direction the arrow should be
        A = numpy.array([ center_x + radius*numpy.cos(theta) , center_y + radius*numpy.sin(theta) ])
        B = numpy.array([ center_x - radius*numpy.cos(theta) , center_y - radius*numpy.sin(theta) ])

        XML_body.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (center_x + radius*numpy.cos(theta), center_y + radius*numpy.sin(theta),
                                                                                                            radialLine_x, radialLine_y,
                                                                                                            lineColor, strokeWidth) )
        if radius > 0:

            s = 1 if radius > arrowL1 + arrowL2 + 0.5*centerPointDia else -1

            XML_body.append( arrowHeadSVG( A, s*directionVector(A,B), arrowL1, arrowL2, arrowW, lineColor ) )

        if radialLine2_x <> None and radialLine2_y <> None:

            # find the circle around the last point with radius where
            # the cursor is
            thisradius = sqrt ( (radialLine2_x  - radialLine_x)**2 + (radialLine2_y  - radialLine_y)**2 )
            print ('thisradius {}'.format (thisradius))

            if thisradius > 0:

                # create two vectors to be used to determine the direction the arrow should be
                A = numpy.array([ radialLine_x, radialLine_y ])
                B = numpy.array([ center_x, center_y ])
                vec = directionVector(A,B)

                vec = vec * thisradius

                # draw line from the last point to that radius in the
                # direction of the last line
                XML_body.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % ( radialLine_x, radialLine_y,
                                                                                                                     radialLine_x + vec[0], radialLine_y + vec[1],
                                                                                                                     lineColor, strokeWidth) )

        if tail_x <> None and tail_y <> None:
            # horizontal tail
            XML_body.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % ( radialLine_x + vec[0], radialLine_y + vec[1],
                                                                                                                 tail_x, radialLine_y + vec[1],
                                                                                                                 lineColor, strokeWidth) )

    if text_x <> None and text_y <> None:

        XML_body.append( textRenderer( text_x, text_y, dimensionText(radius*dimScale,textFormat)) )
        XML_body.append( '<!--%s-->' % (radius) )
        XML_body.append( '<!--%s-->' % (textFormat) )
    XML = '''<%s  %s >
%s
</%s> ''' % ( svgTag, svgParms, "\n".join(XML_body), svgTag )

    return XML


def selectFun(  event, referer, elementXML, elementParms, elementViewObject ):
    x,y = elementParms['x'], elementParms['y']
    dimensioning.point1 = x, y
    debugPrint(2, 'center selected at x=%3.1f y=%3.1f' % (x,y))
    dimensioning.radius = elementParms['r']
    dimensioning.dimScale = 1/elementXML.rootNode().scaling() / UnitConversionFactor()
    dimensioning.stage = 1
    selectionOverlay.hideSelectionGraphicsItems()
    previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )

def clickFunPreview( x, y ):
    if dimensioning.stage == 1:
        dimensioning.point2 = x,y
        debugPrint(2, 'dimension radial direction point set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 2
        return None, None
    elif dimensioning.stage == 2:
        dimensioning.point3 = x, y
        debugPrint(2, 'radius dimension tail defining point set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 3
        return None, None
    elif dimensioning.stage == 3:
        dimensioning.point4 = x, y
        debugPrint(2, 'radius dimension tail defining point set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 4
        return None, None
    else:
        XML = radiusDimensionInnerSVG( dimensioning.point1[0], dimensioning.point1[1],
                                       dimensioning.radius,
                                       dimensioning.point2[0], dimensioning.point2[1],
                                       dimensioning.point3[0], dimensioning.point3[1],
                                       dimensioning.point4[0], dimensioning.point4[1],
                                       x, y,
                                       dimScale=dimensioning.dimScale,
                                       **dimensioning.dimensionConstructorKWs )

        return findUnusedObjectName('dim'), XML

def hoverFunPreview( x, y):
    if dimensioning.stage == 1:
        # radius has been chosen, and the angle of first line is being selected
        return radiusDimensionInnerSVG( dimensioning.point1[0], dimensioning.point1[1],
                                        dimensioning.radius,
                                        x, y,
                                        dimScale=dimensioning.dimScale, **dimensioning.svg_preview_KWs )
    elif dimensioning.stage == 2:
        # radius selected and radial line drawn, now drawing
        # horizontal line
        return radiusDimensionInnerSVG( dimensioning.point1[0], dimensioning.point1[1],
                                        dimensioning.radius,
                                        dimensioning.point2[0], dimensioning.point2[1],
                                        x, y,
                                        dimScale=dimensioning.dimScale, **dimensioning.svg_preview_KWs )
    elif dimensioning.stage == 3:
        # radius selected and radial line drawn, now drawing
        # horizontal line
        return radiusDimensionInnerSVG( dimensioning.point1[0], dimensioning.point1[1],
                                        dimensioning.radius,
                                        dimensioning.point2[0], dimensioning.point2[1],
                                        dimensioning.point3[0], dimensioning.point3[1],
                                        x, y,
                                        dimScale=dimensioning.dimScale, **dimensioning.svg_preview_KWs )
    else:
        # all lines drawn, now positioning text
        return radiusDimensionInnerSVG( dimensioning.point1[0], dimensioning.point1[1],
                                        dimensioning.radius,
                                        dimensioning.point2[0], dimensioning.point2[1],
                                        dimensioning.point3[0], dimensioning.point3[1],
                                        dimensioning.point4[0], dimensioning.point4[1],
                                        x, y,
                                        dimScale=dimensioning.dimScale, **dimensioning.svg_preview_KWs )


maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
maskPen.setWidth(2.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(2.0)

class radiusDimensionInner:
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate(V, ['strokeWidth','arrowL1','arrowL2','arrowW','centerPointDia'], ['lineColor'], ['textRenderer'])
        selectionOverlay.generateSelectionGraphicsItems(
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim')],
            selectFun ,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene,
            doCircles=True, doFittedCircles=True,
            maskPen=maskPen,
            maskHoverPen=maskHoverPen,
            maskBrush = QtGui.QBrush() #clear
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)

    def GetResources(self):
        return {
            'Pixmap' : ':/dd/icons/radiusDimensionInner.svg',
            'MenuText': 'Radius Dimension',
            'ToolTip': 'Creates an internal radius dimension'
            }

FreeCADGui.addCommand('dd_radiusDimensionInner', radiusDimensionInner())

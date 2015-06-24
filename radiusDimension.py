
from dimensioning import *
import selectionOverlay, previewDimension
from dimensionSvgConstructor import *

d = DimensioningProcessTracker()

def radiusDimensionSVG( center_x, center_y, radius, radialLine_x=None, radialLine_y=None, tail_x=None, tail_y=None, text_x=None, text_y=None, 
                        textFormat_radial='R%3.3f', centerPointDia = 1, arrowL1=3, arrowL2=1, arrowW=2, strokeWidth=0.5, scale=1.0, lineColor='blue', 
                        textRenderer=defaultTextRenderer):
    XML_body = [ ' <circle cx ="%f" cy ="%f" r="%f" stroke="none" fill="%s" /> ' % (center_x, center_y, centerPointDia*0.5, lineColor) ]
    if radialLine_x <> None and radialLine_y <> None:
        theta = numpy.arctan2( radialLine_y - center_y, radialLine_x - center_x )
        A = numpy.array([ center_x + radius*numpy.cos(theta) , center_y + radius*numpy.sin(theta) ])
        B = numpy.array([ center_x - radius*numpy.cos(theta) , center_y - radius*numpy.sin(theta) ])
        XML_body.append( svgLine(radialLine_x, radialLine_y, center_x, center_y, lineColor, strokeWidth) )
        if radius > 0:
            s = 1 if radius > arrowL1 + arrowL2 + 0.5*centerPointDia else -1
            XML_body.append( arrowHeadSVG( A, s*directionVector(A,B), arrowL1, arrowL2, arrowW, lineColor ) )
        if tail_x <> None and tail_y <> None:
            XML_body.append( svgLine(radialLine_x, radialLine_y, tail_x, radialLine_y, lineColor, strokeWidth) )
    if text_x <> None and text_y <> None:
        XML_body.append( textRenderer( text_x, text_y, dimensionText(radius*scale,textFormat_radial)) )
    return '<g> %s </g>' % "\n".join(XML_body)

d.dialogWidgets.append( unitSelectionWidget )
d.registerPreference( 'textFormat_radial', 'R%3.3f', 'format mask')
d.registerPreference( 'centerPointDia')
d.registerPreference( 'arrowL1')
d.registerPreference( 'arrowL2')
d.registerPreference( 'arrowW')
d.registerPreference( 'strokeWidth')
d.registerPreference( 'lineColor')
d.registerPreference( 'textRenderer' )

def radiusDimensionSVG_preview(mouseX, mouseY):
    args = d.args + [ mouseX, mouseY ] if len(d.args) < 9 else d.args
    return radiusDimensionSVG( *args, scale=d.viewScale*d.unitConversionFactor, **d.dimensionConstructorKWs )

def radiusDimensionSVG_clickHandler( x, y ):
    d.args = d.args + [ x, y ]
    d.stage = d.stage + 1
    if d.stage == 4 :
        return 'createDimension:%s' % findUnusedObjectName('dim')

def selectFun(  event, referer, elementXML, elementParms, elementViewObject ):
    x,y = elementParms['x'], elementParms['y']
    debugPrint(2, 'center selected at x=%3.1f y=%3.1f' % (x,y))
    d.args = [x, y, elementParms['r']]
    d.viewScale = 1/elementXML.rootNode().scaling()
    d.stage = 1
    selectionOverlay.hideSelectionGraphicsItems()
    previewDimension.initializePreview( d, radiusDimensionSVG_preview, radiusDimensionSVG_clickHandler)

maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
maskPen.setWidth(2.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(2.0)

class RadiusDimension:
    def Activated(self):
        V = getDrawingPageGUIVars()
        d.activate(V, 'Add Radial Dimension', dialogIconPath=os.path.join( iconPath , 'radiusDimension.svg' ), endFunction=self.Activated)
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
            'Pixmap' : os.path.join( iconPath , 'radiusDimension.svg' ) ,
            'MenuText': 'Radius Dimension',
            'ToolTip': 'Creates a radius dimension'
            }

FreeCADGui.addCommand('dd_radiusDimension', RadiusDimension())

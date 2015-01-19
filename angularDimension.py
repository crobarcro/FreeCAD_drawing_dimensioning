
from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import selectionOverlay, previewDimension
from dimensionSvgConstructor import angularDimensionSVG

dimensioning = DimensioningProcessTracker()

def selectFun( event, referer, elementXML, elementParms, elementViewObject ):
    x1,y1,x2,y2 = [ elementParms[k] for k in [ 'x1', 'y1', 'x2', 'y2' ] ]
    debugPrint(2, 'selecting line %i with x1=%3.1f y1=%3.1f, x2=%3.1f y2=%3.1f' % (dimensioning.stage, x1,y1,x2,y2) )
    referer.lockSelection()
    if dimensioning.stage == 0: #then select line1
        dimensioning.line1 = x1,y1,x2,y2
        dimensioning.stage = 1
    else:
        dimensioning.line2 = x1,y1,x2,y2
        dimensioning.stage = 2
        selectionOverlay.hideSelectionGraphicsItems()
        previewDimension.initializePreview( dimensioning.drawingVars, clickFunPreview, hoverFunPreview )

def clickFunPreview( x, y ):
    if dimensioning.stage == 2 :
        dimensioning.point3 = x, y
        debugPrint(2, 'base-line point set to x=%3.1f y=%3.1f' % (x,y))
        dimensioning.stage = 3
        return None, None
    else:
        XML = angularDimensionSVG( dimensioning.line1,
                                   dimensioning.line2,
                                   dimensioning.point3[0], dimensioning.point3[1],
                                   x, y, **dimensioning.dimensionConstructorKWs)

        return findUnusedObjectName('dim'), XML

def hoverFunPreview( x, y ):
    if dimensioning.stage == 2 :
        # at this point we've picked the two lines and are
        # preparing to select where the angle dimension will
        # be shown
        return angularDimensionSVG( dimensioning.line1, dimensioning.line2, x, y, **dimensioning.svg_preview_KWs)
    else:
        # here the dimension is fixed
        return angularDimensionSVG( dimensioning.line1,
                                    dimensioning.line2,
                                    dimensioning.point3[0], dimensioning.point3[1],
                                    x, y, **dimensioning.svg_preview_KWs )

#selection variables for angular dimensioning
maskPen =      QtGui.QPen( QtGui.QColor(0,255,0,100) )
maskPen.setWidth(2.0)
maskHoverPen = QtGui.QPen( QtGui.QColor(0,255,0,255) )
maskHoverPen.setWidth(2.0)

class angularDimension:
    def Activated(self):
        V = getDrawingPageGUIVars()
        dimensioning.activate(V, ['strokeWidth','fontSize','arrowL1','arrowL2','arrowW','gap_datum_points', 'dimension_line_overshoot'], ['lineColor','fontColor'] )
        selectionOverlay.generateSelectionGraphicsItems(
            [obj for obj in V.page.Group  if not obj.Name.startswith('dim')],
            selectFun,
            transform = V.transform,
            sceneToAddTo = V.graphicsScene,
            doLines=True,
            maskPen=maskPen,
            maskHoverPen=maskHoverPen,
            maskBrush = QtGui.QBrush() #clear
            )
        selectionOverlay.addProxyRectToRescaleGraphicsSelectionItems( V.graphicsScene, V.graphicsView, V.width, V.height)

    def GetResources(self):
        return {
            'Pixmap' : os.path.join( iconPath , 'angularDimension.svg' ) ,
            'MenuText': 'Angular Dimension',
            'ToolTip': 'Creates a angular dimension from 2 lines'
            }

FreeCADGui.addCommand('angularDimension', angularDimension())

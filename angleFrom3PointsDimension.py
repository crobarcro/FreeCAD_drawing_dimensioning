
from dimensioning import *
from dimensioning import iconPath # not imported with * directive
import selectionOverlay, previewDimension
from dimensionSvgConstructor import angleFrom3PointsDimensionSVG

dimensioning = DimensioningProcessTracker()

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

FreeCADGui.addCommand('angleFrom3PointsDimension', angleFrom3PointsDimension())

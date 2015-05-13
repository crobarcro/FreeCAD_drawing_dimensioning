
class DrawingDimensioningWorkbench (Workbench):
    # Icon generated using by converting linearDimension.svg to xpm format using Gimp
    Icon = '''
/* XPM */
static char * linearDimension_xpm[] = {
"32 32 10 1",
"       c None",
".      c #000000",
"+      c #0008FF",
"@      c #0009FF",
"#      c #000AFF",
"$      c #00023D",
"%      c #0008F7",
"&      c #0008EE",
"*      c #000587",
"=      c #000001",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".      +@@             +       .",
".    @+@@+            +@@+@    .",
". +@+@@@@@@          @@@@@@@#  .",
"$%@@@@@@@@@+@@@@@@@@@@@@@@@@@@&$",
". #@@@@@@@@         #+@@@@@@@@*=",
".    @+@@+            +@@@@@   .",
".      +@             #@++     .",
".                      #       .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              .",
".                              ."};
'''
    MenuText = 'Drawing Dimensioning'
    def Initialize(self):
        import importlib, os
        from dimensioning import __dir__, debugPrint, iconPath
        import linearDimension
        import halfLinearDimension
        import deleteDimension
        import circularDimension
        import grabPointAdd
        import textAdd
        import textEdit
        import textMove
        import escapeDimensioning
        import angularDimension
        import angleFrom3PointsDimension
        import radiusDimension
        import radiusDimensionInner
        import centerLines
        import noteCircle
        import toleranceAdd
        commandslist = [
            'linearDimension',
            'halfLinearDimension',
            'circularDimension',
            'radiusDimension',
            'radiusDimensionInner',
            'angularDimension',
            'angleFrom3PointsDimension',
            'DrawingDimensioning_centerLines',
            'DrawingDimensioning_centerLine', 
            'noteCircle', 
            'grabPoint',
            'textAddDimensioning',
            'textEditDimensioning',
            'textMoveDimensioning',
            'toleranceAdd', 
            'deleteDimension', 
            'escapeDimensioning',
            ]
        self.appendToolbar('Drawing Dimensioning', commandslist)
        import unfold
        import unfold_bending_note
        import unfold_export_to_dxf
        self.appendToolbar('Drawing Dimensioning Folding', [
                'drawingDimensioning_unfold',
                'drawingDimensioning_bendingNote',
                'drawingDimensioning_exportToDxf',
                ])
        import weldingSymbols
        self.appendToolbar('Drawing Dimensioning Welding Symbols', weldingSymbols.weldingCmds)
        FreeCADGui.addIconPath(iconPath)
        FreeCADGui.addPreferencePage( os.path.join( __dir__, 'Resources', 'ui', 'drawing_dimensioing_prefs-base.ui'),'Drawing Dimensioning' )


Gui.addWorkbench(DrawingDimensioningWorkbench())

import dimensioning #QtCore.QResource.registerResource happens in there

class DrawingDimensioningWorkbench (Workbench):
    Icon = ':/dd/icons/linearDimension.svg'
    MenuText = 'Drawing Dimensioning'
    def Initialize(self):
        import linearDimension
        import linearDimension_stack
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
        from drawing_wb_shortcuts import newpageShortcuts
        self.appendToolbar('Drawing workbench shortcuts', newpageShortcuts + [
                    'dd_new_drawing_page_preferences',
                    'dd_Drawing_OrthoViews',                    
                    ] )

        commandslist = [
            'dd_linearDimension', #where dd is short-hand for drawing dimensioning
            'dd_linearDimensionStack',
            'dd_circularDimension',
            'dd_radiusDimension',
            'dd_radiusDimensionInner',
            'dd_angularDimension',
            'dd_angleFrom3PointsDimension',
            'dd_centerLines',
            'dd_centerLine', 
            'dd_noteCircle', 
            'dd_grabPoint',
            'dd_addText',
            'dd_editText',
            'dd_moveText',
            'dd_addTolerance', 
            'dd_deleteDimension', 
            'dd_escapeDimensioning',
            ]
        self.appendToolbar('Drawing Dimensioning', commandslist)
        import unfold
        import unfold_bending_note
        import unfold_export_to_dxf
        unfold_cmds = [
            'dd_unfold',
            'dd_bendingNote',
            'dd_exportToDxf'
            ]
        self.appendToolbar( 'Drawing Dimensioning Folding', unfold_cmds )
        import weldingSymbols
        if int( FreeCAD.Version()[1] > 15 ) and  int( FreeCAD.Version()[2].split()[0] ) > 5165:
            weldingCommandList = ['dd_weldingGroupCommand']
        else:
            weldingCommandList = weldingSymbols.weldingCmds
        self.appendToolbar('Drawing Dimensioning Welding Symbols', weldingCommandList)
        self.appendToolbar('Drawing Dimensioning Help', [ 'dd_help' ])
        FreeCADGui.addIconPath(':/dd/icons')
        FreeCADGui.addPreferencePage( ':/dd/ui/drawing_dimensioing_prefs-base.ui','Drawing Dimensioning' )


Gui.addWorkbench(DrawingDimensioningWorkbench())



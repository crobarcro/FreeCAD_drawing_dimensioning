# This Python file uses the following encoding: utf-8
'''
library containing commonly used SVGs construction functions
'''


import numpy
from numpy import dot, pi, arctan2, sin, cos, arccos, sqrt
from numpy.linalg import norm
from textSvg import SvgTextRenderer

def directionVector( A, B ):
    if norm(B-A) == 0:
        return numpy.array([0.0,0.0])
    else:
        return (B-A)/norm(B-A)

def dimensionSVG_trimLine(A,B,trimA, trimB):
    d = directionVector( A, B)
    return (A + d*trimA).tolist() + (B - d*trimB).tolist()

def rotate2D( v, angle ):
    return numpy.dot( [[ cos(angle), -sin(angle)],[ sin(angle), cos(angle)]], v)

def arrowHeadSVG( tipPos, d, L1, L2, W, clr='blue'):
    d2 = numpy.dot( [[ 0, -1],[ 1, 0]], d) #same as rotate2D( d, pi/2 )
    R = numpy.array( [d, d2]).transpose()
    p2 = numpy.dot( R, [ L1,    W/2.0 ]) + tipPos
    p3 = numpy.dot( R, [ L1+L2, 0     ]) + tipPos
    p4 = numpy.dot( R, [ L1,   -W/2.0 ]) + tipPos
    return '<polygon points="%f,%f %f,%f %f,%f %f,%f" style="fill:%s;stroke:%s;stroke-width:0" />' % (tipPos[0], tipPos[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1], clr, clr)


def dimensionText( V, formatStr, roundingDigit=6):
    s1 = (formatStr % V).rstrip('0').rstrip('.')
    Vrounded = numpy.round(V, roundingDigit)
    s2 = (formatStr % Vrounded).rstrip('0').rstrip('.')
    return s2 if len(s2) < len(s1) else s1

defaultTextRenderer = SvgTextRenderer(font_family='Verdana', font_size='5pt', fill="red")


def svgLine(  x1, y1, x2, y2, lineColor, strokeWidth):
    return '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%1.2f" />' % (x1, y1, x2, y2, lineColor, strokeWidth )

def lineIntersection(line1, line2):
    x1,y1 = line1[0:2]
    dx1 = line1[2] - x1
    dy1 = line1[3] - y1
    x2,y2 = line2[0:2]
    dx2 = line2[2] - x2
    dy2 = line2[3] - y2
    # x1 + dx1*t1 = x2 + dx2*t2
    # y1 + dy1*t1 = y2 + dy2*t2
    A = numpy.array([
            [ dx1, -dx2 ],
            [ dy1, -dy2 ],
            ])
    b = numpy.array([ x2 - x1, y2 - y1])
    t1,t2 = numpy.linalg.solve(A,b)
    x_int = x1 + dx1*t1
    y_int = y1 + dy1*t1
    #assert x1 + dx1*t1 == x2 + dx2*t2
    return x_int, y_int


def _centerLineSVG( x1, y1, x2, y2, len_dot, len_dash, len_gap, start_with_half_dot=False):
    start = numpy.array( [x1, y1] )
    end = numpy.array( [x2, y2] )
    d = directionVector(start, end)
    dCode = ''
    pos = start
    step = len_dot*0.5 if start_with_half_dot else len_dot
    while norm(pos - start) + 10**-6 < norm(end - start):
        dCode = dCode + 'M %f,%f' %  (pos[0], pos[1])
        pos = pos + d*step
        if norm(pos - start) > norm(end - start):
            pos = end
        dCode = dCode + ' L %f,%f ' % (pos[0], pos[1])
        pos = pos + d*len_gap
        step = len_dash if step < len_dash else len_dot
    if dCode <> '':
        return '<path d="%s"/>' % dCode
    else:
        return ''


def _centerLinesSVG( center, topLeft, bottomRight, dimScale, centerLine_len_dot, centerLine_len_dash, centerLine_len_gap, svgTag, svgParms, strokeWidth, lineColor, doVertical, doHorizontal ):
    XML_body = []
    center = numpy.array( center ) / dimScale
    topLeft = numpy.array( topLeft ) / dimScale
    if bottomRight <> None: bottomRight =  numpy.array( bottomRight ) / dimScale
    commonArgs =  centerLine_len_dot / dimScale,  centerLine_len_dash / dimScale,  centerLine_len_gap / dimScale
    if doVertical: XML_body.append( _centerLineSVG(center[0], center[1], center[0], topLeft[1], *commonArgs ) )
    if doHorizontal: XML_body.append( _centerLineSVG(center[0], center[1], topLeft[0], center[1], *commonArgs ) )
    if bottomRight <> None:
        if doVertical: XML_body.append( _centerLineSVG(center[0], center[1], center[0], bottomRight[1], *commonArgs ) )
        if doHorizontal: XML_body.append( _centerLineSVG(center[0], center[1], bottomRight[0], center[1], *commonArgs ) )
    return '''<%s %s transform="scale(%f,%f)" stroke="%s"  stroke-width="%f" >
%s
</%s> ''' % ( svgTag, svgParms, dimScale, dimScale, lineColor, strokeWidth/ dimScale, "\n".join(XML_body), svgTag )


def centerLinesSVG( center, topLeft, bottomRight=None, dimScale=1.0, centerLine_len_dot=2.0, centerLine_len_dash=6.0, centerLine_len_gap=2.0, svgTag='g', svgParms='', centerLine_width=0.5, centerLine_color='blue'):
    return _centerLinesSVG( center, topLeft, bottomRight, dimScale, centerLine_len_dot, centerLine_len_dash, centerLine_len_gap, svgTag, svgParms, centerLine_width, centerLine_color, True, True )

def centerLineSVG( center, topLeft, bottomRight=None,  dimScale=1.0, centerLine_len_dot=2.0, centerLine_len_dash=6.0, centerLine_len_gap=2.0, svgTag='g', svgParms='', centerLine_width=0.5, centerLine_color='blue'):
    v = abs(center[0] - topLeft[0]) < abs(center[1] - topLeft[1]) #vertical
    return _centerLinesSVG( center, topLeft, bottomRight, dimScale, centerLine_len_dot, centerLine_len_dash, centerLine_len_gap, svgTag, svgParms, centerLine_width, centerLine_color, v, not v )


def distanceBetweenParallelsSVG( line1, line2, x_baseline, y_baseline, x_text=None, y_text=None, textFormat='%3.3f', scale=1.0, gap_datum_points = 2, dimension_line_overshoot=1,
                                 arrowL1=3, arrowL2=1, arrowW=2, svgTag='g', svgParms='', strokeWidth=0.5, lineColor='blue', textRenderer=defaultTextRenderer):
    XML = []
    p1 = numpy.array( [line1[0], line1[1]] )
    p2 = numpy.array( [line1[2], line1[3]] )
    p3 = numpy.array( [line2[0], line2[1]] )
    p4 = numpy.array( [line2[2], line2[3]] )
    p5 = numpy.array([ x_baseline, y_baseline ])
    d = directionVector(p1,p2)
    # arrow positions
    p_arrow1 = p1 + d*dot(d, p5-p1)
    p_arrow2 = p3 + d*dot(d, p5-p3)
    p_center = (p_arrow1 + p_arrow2)/2
    def line_to_arrow_point( a, b, c): # where a=p1,b=p2 or a=p3,b=p4 and c=p_arrow1 or c=p_arrow2
        if abs( norm(a -b) - (norm(a-c) + norm(b-c))) < norm(a -b)/1000:
            return
        if norm(a-c) < norm(b-c): #then closer to a
            d_a =  directionVector(a, c)
            v = a + gap_datum_points*d_a
            w = c + dimension_line_overshoot*d_a
        else:
            d_b =  directionVector(b, c)
            v = b + gap_datum_points*d_b
            w = c + dimension_line_overshoot*d_b
        XML.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%f" />' % (v[0],v[1],w[0],w[1], lineColor, strokeWidth) )
    line_to_arrow_point( p1, p2, p_arrow1)
    line_to_arrow_point( p3, p4, p_arrow2)
    XML.append( '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:%f" />' % ( p_arrow1[0], p_arrow1[1], p_arrow2[0], p_arrow2[1], lineColor, strokeWidth) )
    dist = norm(p_arrow1 - p_arrow2)
    if dist > 0:
        s = -1 if dist > 2.5*(arrowL1 + arrowL2) else 1
    XML.append( arrowHeadSVG( p_arrow1,  directionVector(p_center, p_arrow1)*s, arrowL1, arrowL2, arrowW, lineColor ) )
    XML.append( arrowHeadSVG( p_arrow2,  directionVector(p_center, p_arrow2)*s, arrowL1, arrowL2, arrowW, lineColor ) )
    if x_text <> None and y_text <> None:
        textRotation = numpy.arctan2( d[1], d[0]) / numpy.pi * 180 + 90
        if textRotation > 90:
            textRotation = textRotation - 180
        if textRotation > 88:
            textRotation = textRotation - 180
        elif textRotation > 12 :
            textRotation = textRotation - 90
        elif textRotation < -92:
            textRotation = textRotation + 90
        textXML = textRenderer( x_text, y_text, dimensionText(dist*scale,textFormat), rotation=textRotation)
        XML.append( textXML )
    XML = '''<%s  %s >
 %s
</%s> ''' % ( svgTag, svgParms, '\n'.join(XML), svgTag )
    return XML


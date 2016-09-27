title_codes = {
0x01 : ['parent_id', '>I',],
0x03 : ['lock', '>h',],
0x04 : ['bbox', '>hhhh',],
0x05 : ['fill_color', '>HHH',],
0x06 : ['border_color', '>HHH',],
0x07 : ['shadow_color', '>HHH',],
0x08 : ['fill_alpha', '>H',],
0x09 : ['border_alpha', '>H',],
0x0A : ['shadow_alpha', '>H',],
0x0B : ['line_width', '>H',],
0x0C : ['shadow_mode', '>H',],
0x0D : ['shadow_depth', '>H',],
0x0F : ['bbox', '>hhhh',],
0x10 : ['arrow_type', '>H',],
0x11 : ['arrow_desc', '>hhhhhhhh',],
0x19 : ['corner_roundness', '>H',],
0x24 : ['justify', '>H',],
0x25 : ['kerning', '>H',],
0x26 : ['video_bg', '>H',],
0x27 : ['bg_color', '>HHH',],
0x2A : ['??', '>H',],
0x2B : ['color1', '>HHH',],
0x2C : ['??', '>H',],
0x2D : ['??', '>H',],
0x2E : ['fill_gradient_end_transparencey', '>H',],
0x2F : ['fill_gradient_dir', '>H',],
0x30 : ['??', '>H',],
0x31 : ['color2', '>HHH',],
0x32 : ['??', '>H',],
0x33 : ['??', '>H',],
0x34 : ['border_gradient_end_transparencey', '>H',],
0x35 : ['border_gradiant_dir', '>H',],
0x3B : ['text_formating', -1],
0x3F : ['border_width', '>H',],
0x40 : ['leading', '>H',],
0x41 : ['kerning_data', -1,],
0x4A : ['shadow_blur', '>H',],
0x0E : ['shadow_dir', '>hh', ],
0x3C : ['font_list', -1,] ,
0x42 : ['??', '>I'],
}

# these codes are from imagemagick
pict_codes = {
0x00 : ['NOP', 0, 'nop' ],
0x01 : ['Clip', 0, 'clip' ],
0x02 : ['BkPat', 8, 'background pattern' ],
0x03 : ['TxFont', 2, 'text font (word)' ],
0x04 : ['TxFace', 1, 'text face (byte)' ],
0x05 : ['TxMode', 2, 'text mode (word)' ],
0x06 : ['SpExtra', 4, 'space extra (fixed point)' ],
0x07 : ['PnSize', 4, 'pen size (point)' ],
0x08 : ['PnMode', 2, 'pen mode (word)' ],
0x09 : ['PnPat', 8, 'pen pattern' ],
0x0A : ['FillPat', 8, 'fill pattern' ],
0x0B : ['OvSize', 4, 'oval size (point)' ],
0x0C : ['Origin', 4, 'dh, dv (word)',  ],
0x0D : ['TxSize', 2, 'text size (word)' ],
0x0E : ['FgColor', 4, 'foreground color (ssize_tword)' ],
0x0F : ['BkColor', 4, 'background color (ssize_tword)' ],
0x10 : ['TxRatio', 8, 'numerator (point), denominator (point)' ],
0x11 : ['Version', 1, 'version (byte)' ],
0x12 : ['BkPixPat', 0, 'color background pattern' ],
0x13 : ['PnPixPat', 0, 'color pen pattern' ],
0x14 : ['FillPixPat', 0, 'color fill pattern' ],
0x15 : ['PnLocHFrac', 2, 'fractional pen position' ],
0x16 : ['ChExtra', 2, 'extra for each character' ],
0x17 : ['reserved', 0, 'reserved for Apple use' ],
0x18 : ['reserved', 0, 'reserved for Apple use' ],
0x19 : ['reserved', 0, 'reserved for Apple use' ],
0x1A : ['RGBFgCol', 6, 'RGB foreColor' ],
0x1B : ['RGBBkCol', 6, 'RGB backColor' ],
0x1C : ['HiliteMode', 0, 'hilite mode flag' ],
0x1D : ['HiliteColor', 6, 'RGB hilite color' ],
0x1E : ['DefHilite', 0, 'Use default hilite color' ],
0x1F : ['OpColor', 6, 'RGB OpColor for arithmetic modes' ],
0x20 : ['Line', 8, 'pnLoc (point), newPt (point)' ],
0x21 : ['LineFrom', 4, 'newPt (point)' ],
0x22 : ['ShortLine', 6, 'pnLoc (point, dh, dv (-128 .. 127))' ],
0x23 : ['ShortLineFrom', 2, 'dh, dv (-128 .. 127)' ],
0x24 : ['reserved', -1, 'reserved for Apple use' ],
0x25 : ['reserved', -1, 'reserved for Apple use' ],
0x26 : ['reserved', -1, 'reserved for Apple use' ],
0x27 : ['reserved', -1, 'reserved for Apple use' ],
0x28 : ['LongText', 0, 'txLoc (point), count (0..255), text' ],
0x29 : ['DHText', 0, 'dh (0..255), count (0..255), text' ],
0x2A : ['DVText', 0, 'dv (0..255), count (0..255), text' ],
0x2B : ['DHDVText', 0, 'dh, dv (0..255), count (0..255), text' ],
0x2C : ['reserved', -1, 'reserved for Apple use' ],
0x2D : ['reserved', -1, 'reserved for Apple use' ],
0x2E : ['reserved', -1, 'reserved for Apple use' ],
0x2F : ['reserved', -1, 'reserved for Apple use' ],
0x30 : ['frameRect', 8, 'rect' ],
0x31 : ['paintRect', 8, 'rect' ],
0x32 : ['eraseRect', 8, 'rect' ],
0x33 : ['invertRect', 8, 'rect' ],
0x34 : ['fillRect', 8, 'rect' ],
0x35 : ['reserved', 8, 'reserved for Apple use' ],
0x36 : ['reserved', 8, 'reserved for Apple use' ],
0x37 : ['reserved', 8, 'reserved for Apple use' ],
0x38 : ['frameSameRect', 0, 'rect' ],
0x39 : ['paintSameRect', 0, 'rect' ],
0x3A : ['eraseSameRect', 0, 'rect' ],
0x3B : ['invertSameRect', 0, 'rect' ],
0x3C : ['fillSameRect', 0, 'rect' ],
0x3D : ['reserved', 0, 'reserved for Apple use' ],
0x3E : ['reserved', 0, 'reserved for Apple use' ],
0x3F : ['reserved', 0, 'reserved for Apple use' ],
0x40 : ['frameRRect', 8, 'rect' ],
0x41 : ['paintRRect', 8, 'rect' ],
0x42 : ['eraseRRect', 8, 'rect' ],
0x43 : ['invertRRect', 8, 'rect' ],
0x44 : ['fillRRrect', 8, 'rect' ],
0x45 : ['reserved', 8, 'reserved for Apple use' ],
0x46 : ['reserved', 8, 'reserved for Apple use' ],
0x47 : ['reserved', 8, 'reserved for Apple use' ],
0x48 : ['frameSameRRect', 0, 'rect' ],
0x49 : ['paintSameRRect', 0, 'rect' ],
0x4A : ['eraseSameRRect', 0, 'rect' ],
0x4B : ['invertSameRRect', 0, 'rect' ],
0x4C : ['fillSameRRect', 0, 'rect' ],
0x4D : ['reserved', 0, 'reserved for Apple use' ],
0x4E : ['reserved', 0, 'reserved for Apple use' ],
0x4F : ['reserved', 0, 'reserved for Apple use' ],
0x50 : ['frameOval', 8, 'rect' ],
0x51 : ['paintOval', 8, 'rect' ],
0x52 : ['eraseOval', 8, 'rect' ],
0x53 : ['invertOval', 8, 'rect' ],
0x54 : ['fillOval', 8, 'rect' ],
0x55 : ['reserved', 8, 'reserved for Apple use' ],
0x56 : ['reserved', 8, 'reserved for Apple use' ],
0x57 : ['reserved', 8, 'reserved for Apple use' ],
0x58 : ['frameSameOval', 0, 'rect' ],
0x59 : ['paintSameOval', 0, 'rect' ],
0x5A : ['eraseSameOval', 0, 'rect' ],
0x5B : ['invertSameOval', 0, 'rect' ],
0x5C : ['fillSameOval', 0, 'rect' ],
0x5D : ['reserved', 0, 'reserved for Apple use' ],
0x5E : ['reserved', 0, 'reserved for Apple use' ],
0x5F : ['reserved', 0, 'reserved for Apple use' ],
0x60 : ['frameArc', 12, 'rect, startAngle, arcAngle' ],
0x61 : ['paintArc', 12, 'rect, startAngle, arcAngle' ],
0x62 : ['eraseArc', 12, 'rect, startAngle, arcAngle' ],
0x63 : ['invertArc', 12, 'rect, startAngle, arcAngle' ],
0x64 : ['fillArc', 12, 'rect, startAngle, arcAngle' ],
0x65 : ['reserved', 12, 'reserved for Apple use' ],
0x66 : ['reserved', 12, 'reserved for Apple use' ],
0x67 : ['reserved', 12, 'reserved for Apple use' ],
0x68 : ['frameSameArc', 4, 'rect, startAngle, arcAngle' ],
0x69 : ['paintSameArc', 4, 'rect, startAngle, arcAngle' ],
0x6A : ['eraseSameArc', 4, 'rect, startAngle, arcAngle' ],
0x6B : ['invertSameArc', 4, 'rect, startAngle, arcAngle' ],
0x6C : ['fillSameArc', 4, 'rect, startAngle, arcAngle' ],
0x6D : ['reserved', 4, 'reserved for Apple use' ],
0x6E : ['reserved', 4, 'reserved for Apple use' ],
0x6F : ['reserved', 4, 'reserved for Apple use' ],
0x70 : ['framePoly', 0, 'poly' ],
0x71 : ['paintPoly', 0, 'poly' ],
0x72 : ['erasePoly', 0, 'poly' ],
0x73 : ['invertPoly', 0, 'poly' ],
0x74 : ['fillPoly', 0, 'poly' ],
0x75 : ['reserved', 0, 'reserved for Apple use' ],
0x76 : ['reserved', 0, 'reserved for Apple use' ],
0x77 : ['reserved', 0, 'reserved for Apple use' ],
0x78 : ['frameSamePoly', 0, 'poly (NYI)' ],
0x79 : ['paintSamePoly', 0, 'poly (NYI)' ],
0x7A : ['eraseSamePoly', 0, 'poly (NYI)' ],
0x7B : ['invertSamePoly', 0, 'poly (NYI)' ],
0x7C : ['fillSamePoly', 0, 'poly (NYI)' ],
0x7D : ['reserved', 0, 'reserved for Apple use' ],
0x7E : ['reserved', 0, 'reserved for Apple use' ],
0x7F : ['reserved', 0, 'reserved for Apple use' ],
0x80 : ['frameRgn', 0, 'region' ],
0x81 : ['paintRgn', 0, 'region' ],
0x82 : ['eraseRgn', 0, 'region' ],
0x83 : ['invertRgn', 0, 'region' ],
0x84 : ['fillRgn', 0, 'region' ],
0x85 : ['reserved', 0, 'reserved for Apple use' ],
0x86 : ['reserved', 0, 'reserved for Apple use' ],
0x87 : ['reserved', 0, 'reserved for Apple use' ],
0x88 : ['frameSameRgn', 0, 'region (NYI)' ],
0x89 : ['paintSameRgn', 0, 'region (NYI)' ],
0x8A : ['eraseSameRgn', 0, 'region (NYI)' ],
0x8B : ['invertSameRgn', 0, 'region (NYI)' ],
0x8C : ['fillSameRgn', 0, 'region (NYI)' ],
0x8D : ['reserved', 0, 'reserved for Apple use' ],
0x8E : ['reserved', 0, 'reserved for Apple use' ],
0x8F : ['reserved', 0, 'reserved for Apple use' ],
0x90 : ['BitsRect', 0, 'copybits, rect clipped' ],
0x91 : ['BitsRgn', 0, 'copybits, rgn clipped' ],
0x92 : ['reserved', -1, 'reserved for Apple use' ],
0x93 : ['reserved', -1, 'reserved for Apple use' ],
0x94 : ['reserved', -1, 'reserved for Apple use' ],
0x95 : ['reserved', -1, 'reserved for Apple use' ],
0x96 : ['reserved', -1, 'reserved for Apple use' ],
0x97 : ['reserved', -1, 'reserved for Apple use' ],
0x98 : ['PackBitsRect', 0, 'packed copybits, rect clipped' ],
0x99 : ['PackBitsRgn', 0, 'packed copybits, rgn clipped' ],
0x9A : ['DirectBitsRect', 0, 'PixMap, srcRect, dstRect, mode, PixData' ],
0x9B : ['DirectBitsRgn', 0, 'PixMap, srcRect, dstRect, mode, maskRgn, PixData' ],
0x9C : ['reserved', -1, 'reserved for Apple use' ],
0x9D : ['reserved', -1, 'reserved for Apple use' ],
0x9E : ['reserved', -1, 'reserved for Apple use' ],
0x9F : ['reserved', -1, 'reserved for Apple use' ],
0xA0 : ['ShortComment', 2, 'kind (word)'  ],
0xA1 : ['LongComment', 0, 'kind (word), size (word), data' ]
}

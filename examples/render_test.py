import pct_titles
import os
import cythonmagick
from StringIO import StringIO

def escape(s):
    s = s.replace("&", "\&amp;")
    s = s.replace("<", "\&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    s = s.replace("'", '&#39;')
    return s

def convert_color(c, alpha):
    a =  1.0 - (alpha / 100.0)
    r = c[0] / 65535.0
    g = c[1] / 65535.0
    b = c[2] / 65535.0

    c = '#%04X%04X%04X%04X' % ( int(r*65535.0), int(g*65535.0), int(b*65535.0),
                                int(a*65535.0))

    return c

def render_item(pct, img, item ,out_dir):
    bbox = item.bbox
    img.fill_color = 'white'
    img.stroke_color = 'white'

    min_x = min(bbox[1], bbox[3])
    min_y = min(bbox[0], bbox[2])

    max_x = max(bbox[1], bbox[3])
    max_y = max(bbox[0], bbox[2])

    width  = max_x - min_x
    height = max_y - min_y

    rad_x =  width/2.0
    rad_y =  height/2.0

    origin_x = min_x + rad_x
    origin_y = min_y + rad_y

    fill_color   = convert_color(item.fill_color, item.fill_alpha)
    stroke_color = convert_color(item.border_color, item.border_alpha)
    shadow_color = convert_color(item.shadow_color, item.shadow_alpha)

    img.fill_color = fill_color
    img.stroke_width = item.border_width
    img.stroke_color = stroke_color

    if item.border_width:
        img.stroke_color = stroke_color
    else:
        img.stroke_color = fill_color

    if isinstance(item, pct_titles.TitleLine):
        img.stroke_width  = item.line_width
        img.stroke_color = 'white'

        line = cythonmagick.Line(bbox[1], bbox[0],  bbox[3],  bbox[2])
        img.draw([line])

    elif isinstance(item, pct_titles.TitleRectangle):
        roundness = item.corner_roundness / 2.0
        rect = cythonmagick.RoundRectangle(min_x, min_y, max_x, max_y, roundness,roundness)
        img.draw([rect])

    elif isinstance(item, pct_titles.TitleOval):
        origin_x = min_x + rad_x
        origin_y = min_y + rad_y
        oval = cythonmagick.Ellipse(origin_x, origin_y, rad_x, rad_y, 0, 360)
        img.draw([oval])

    elif isinstance(item, pct_titles.TitleText):

        font_size = item.text_formating[0].font_size
        font_id = item.text_formating[0].font_id

        font_style_id = item.text_formating[0].style
        font = pct.title_page.fonts[font_id].replace(" ", '-')

        style = 'normal'
        if font_style_id in (0x0200, 0x0300):
            style = 'italic'

        caption_size = "%dx%d" % (width, 0) # zero for auto height
        caption = cythonmagick.Image(size=caption_size)

        caption.font = font
        caption.density = "72x72"
        caption.font_point_size = font_size

        caption.background = 'none'
        caption.fill_color = fill_color
        caption.stroke_width = item.border_width
        caption.stroke_color = stroke_color
        caption.font_style = style

        # bold
        if font_style_id in (0x0100, 0x0300):
            caption.font_weight = 1
        else:
            caption.font_weight = 0

        text = item.text
        caption.read("caption:{text}".format(text=text))

        grow = 200
        original_size = caption.size()
        caption.extent("%dx%d!" % (width+grow, height+grow), 'center')

        offset_x = min_x - (caption.size().width - original_size.width) / 2
        offset_y = min_y - (caption.size().height - original_size.height) / 2
        position = cythonmagick.Geometry(0, 0, offset_x, offset_y)

        if item.shadow_depth or item.shadow_blur:
            alpha = caption.channel("alpha")
            alpha.negate()
            # alpha.write(os.path.join(out_dir, "alpha.png"))
            shadow = cythonmagick.Image(size=alpha.size(), color=shadow_color)
            shadow.composite(alpha, compose = "copyopacity")

            if item.shadow_blur:
                shadow.blur(1, item.shadow_blur)

            shadow_pos = cythonmagick.Geometry(0, 0, offset_x + item.shadow_dir[1], offset_y + item.shadow_dir[0])
            shadow.artifacts["compose:args"] = "%d" % (100-item.shadow_alpha)
            img.composite(shadow, "dissolve", shadow_pos)

        img.composite(caption, "over", position,)

def render_pct(src, dst):
    pct = pct_titles.PctFile()
    pct.read(src)
    size = "860x486" # this seems to be the base resolution

    img = cythonmagick.Image(size=size, color="grey")
    #convert -list font

    for i, item in enumerate(pct.elements):
        render_item(pct, img, item, os.path.dirname(dst))

    img.resize("720x486!")


    name, ext =  os.path.splitext(dst)
    if ext and ext.lower() in (".pict", '.pct',):
        img.magick = 'pict'
        data = StringIO(img.tostring())
        f = open(dst, 'wb')
        pct.embed(data, f)

    else:
        img.write(dst)




if __name__ == "__main__":

    from optparse import OptionParser

    parser = OptionParser()

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("not enough args")

    render_pct(args[0], args[1])

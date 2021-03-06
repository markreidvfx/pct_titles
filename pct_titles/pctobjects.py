from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )

from struct import pack, unpack
import io
from io import BytesIO
from . import codes

def update_size(f, pos):
    cur = f.tell()
    f.seek(pos)
    write_uint16(f, cur - pos - 2)
    f.seek(cur)

def update_size_aaf(f, pos):
    cur = f.tell()
    f.seek(pos)
    size = cur - pos
    # aaf put a little endian data size at the beginning for some reason
    f.write(pack(b'<H', size))
    f.seek(cur)

def write_byte(f, value):
    f.write(pack(b'>B', value))

def read_byte(f):
    return unpack(b">B", f.read(1))[0]

def write_uint16(f, value):
    f.write(pack(b'>H', value))
def write_int16(f, value):
    f.write(pack(b'>h', value))

def write_uint32(f, value):
    f.write(pack(b'>I', value))

def write_color_prop(f, prop_id, color):
    write_uint16(f, prop_id)
    write_uint16(f, 6)
    for x in range(3):
        write_uint16(f, color[x])

def write_uint16_prop(f, prop_id, value):
    write_uint16(f, prop_id)
    write_uint16(f, 2)
    write_uint16(f, value)

def write_int16_prop(f, prop_id, value):
    write_uint16(f, prop_id)
    write_uint16(f, 2)
    write_int16(f, value)

def read_uint16(f):
    return unpack(b'>H', f.read(2))[0]

def read_int16(f):
    return unpack('>h', f.read(2))[0]

def read_uint32(f):
    return unpack('>I', f.read(4))[0]

def read_pict_header(f, pct_file):

    data_size = read_uint16(f)
    data_size_pos = f.tell()
    if not data_size:
        f.read(510)
        data_size = read_uint16(f)
        data_size_pos = f.tell()

    image_rect = []
    for i in xrange(4):
        image_rect.append(read_int16(f))

    pct_file.width  = image_rect[3]
    pct_file.height = image_rect[2]

    c = 0
    while c == 0:
        c = read_byte(f)

    if c != 0x11:
        raise Exception()

    version = read_uint16(f)

    if version != 0x02FF:
        raise Exception()

    pict_info_op = read_uint16(f)

    if pict_info_op != 0x0C00:
        raise Exception()

    for x in range(12):
        v = read_uint16(f)
        # print "0x%04X" % read_uint16(f)

    return data_size_pos

def read_pct_file(f, pct_file=None):
    if not pct_file:
        pct_file = PctFile()

    read_pict_header(f, pct_file)

    while True:

        if f.tell() % 2 != 0:
            code = read_byte(f)
        else:
            d = f.read(2)
            if d is None:
                return
            if len(d) == 0:
                return
            code = unpack(b">H", d)[0]


        if code > 0x00A1:
            continue
        # print "code 0x%04X" % code
        if code == 0x00A1:

            comment_type = read_uint16(f)
            size = read_uint16(f)
            if comment_type == 0x0064:
                obj = read_title_comment(f, size)

                if isinstance(obj, TitlePage):
                    pct_file.title_page = obj
                else:
                    pct_file.add_element(obj)
            else:
                pass
                # f.read(size)

        elif code in codes.pict_codes:
            pict_code =  codes.pict_codes[code]
            # print pict_code, pict_code[1]
            # skip ahead on known sizes
            if pict_code[1] == -1:
                pass
                # print "-1", read_uint16(f)

            if pict_code[1] > 0:
                f.read(pict_code[1])

    return pct_file

def read_title_comment(f, length):
    start = f.tell()
    assert f.read(4) == b"AVID"
    assert read_uint16(f) == 1

    type_name_size = read_uint16(f)
    type_name = f.read(type_name_size)
    if type_name == b"TitlePage":
        obj = TitlePage()
    elif type_name == b"TitleText":
        obj = TitleText()
    elif type_name == b"TitleLine":
        obj = TitleLine()
    elif type_name == b"TitleOval":
        obj = TitleOval()
    # this has a null for some reason
    elif type_name == b"TitleRectangle\x00":
        obj = TitleRectangle()
    else:
        raise Exception("unknown title type: %s" % type_name)

    assert read_byte(f) == 0 #always 0
    assert read_uint16(f) == 0 #always 0

    layer_size = read_uint16(f) # size of next should be 4
    assert layer_size == 4

    obj.layer_id = read_uint32(f)

    while True:
        ret = read_title_property(f, obj)
        if not ret:
            break

        if f.tell() - start >= length:
            break

    return obj

def read_title_property(f, obj):
    code = f.read(2)

    if not code:
        return False

    code = read_uint16(BytesIO(code))
    # print '0x%2X' % code
    size = read_uint16(f)
    data = f.read(size)

    # pname= codes.title_codes[code][0]
    # print "%05d %s.%s 0x%02X size: %d "  % (f.tell(), obj.__class__.__name__,pname, code, size)

    obj.read_property_value(code, data)

    return True

class PctFile(object):
    def __init__(self):
        self.elements = []
        self.title_page = TitlePage()
        self.width = 16
        self.height = 16
        self.aaf_mode = False

    def add_element(self, element):
        self.elements.append(element)

    def write(self, dst_file):
        # looks like a file object
        if hasattr(dst_file, 'read') and hasattr(dst_file, 'tell') and hasattr(dst_file, 'seek'):
            f = dst_file
        else:
            f = io.open(dst_file, 'wb')

        # embed aaf doesn't have header padding
        if not self.aaf_mode:
            for i in xrange(512):
                write_byte(f, 0)

        data_size_pos = self.write_header(f)
        self.write_comment_tags(f)
        write_byte(f, 0)
        write_byte(f, 0xFF)

        if self.aaf_mode:
            update_size_aaf(f, data_size_pos)
        else:
            update_size(f, data_size_pos)

    def read(self, src_file):
        # looks like a file object
        if hasattr(src_file, 'read') and hasattr(src_file, 'tell'):
            f = src_file
        else:
            f = io.open(src_file, 'rb')

        read_pct_file(f, self)

    def embed(self, src_file, dst_file):
        """
        embed titles in a existing pict file
        """
        tmp = PctFile()

        pos = src_file.tell()
        data_size_pos = read_pict_header(src_file, tmp)
        header_size = src_file.tell() - pos
        src_file.seek(pos)
        if header_size > 512:
            dst_file.write(src_file.read(header_size))

        self.write_comment_tags(dst_file)

        while True:
            data = src_file.read(1024)
            if not data:
                break
            dst_file.write(data)

    def write_header(self, f):
        data_size_pos = f.tell()
        write_uint16(f, 0)

        write_uint16(f, 0x0000)
        write_uint16(f, 0x0000)

        width = self.width
        height = self.height

        if self.aaf_mode:
            width = 16
            height = 16

        write_uint16(f, height)
        write_uint16(f, width)

        write_byte(f, 0)
        write_byte(f, 0x11)
        write_byte(f, 0x02) # version
        write_byte(f, 0xFF)
        write_uint16(f, 0x0C00) # info op
        write_uint16(f, 0xFFFE)
        write_uint16(f, 0x0000)

        write_uint16(f, 0x0048) # 72 dpI
        write_uint16(f, 0x0000)
        write_uint16(f, 0x0048) # 72 dpI
        write_uint16(f, 0x0000)

        write_uint16(f, 0x0000)
        write_uint16(f, 0x0000)
        write_uint16(f, height)
        write_uint16(f, width)
        write_uint16(f, 0x0000)
        write_uint16(f, 0x0000)

        return data_size_pos

    def write_comment_tags(self, f):
        self.write_desc_commnet(f)

        self.write_comment(f, self.title_page)
        for i, item in enumerate(self.elements):
            item.parent_id = self.title_page.layer_id
            item.layer_id = i + 9
            self.write_comment(f, item)

    def write_desc_commnet(self, f):
        # write 0x0065 avid tag
        f.write("00A10065000E41564944000131204D4143204D43".decode("hex"))

    def write_comment(self, f, obj):
        # comment
        write_uint16(f, 0x00A1)
        # comment type
        write_uint16(f, 0x0064)

        # size
        data_size_pos = f.tell()
        write_uint16(f, 0)

        obj.write(f)

        update_size(f, data_size_pos)


class TitleBase(object):
    def __init__(self):
        self.layer_id = None
        self.parent_id = None
        self.prop_ids = [0x01, 0x04, 0x03, 0x42]

        # 0,0--------|
        # |          |
        # |          |
        # |          |
        # ----------485, 865

        # top_y, left_x, bottom_y, right_x

        self.bbox = [0, 0, 485, 865]
        self.lock = False

    def read_value(self, prop_id, value):
        if not prop_id in self.prop_ids:
            raise ValueError("incorrect prop_id")

    def write(self, f):

        f.write(b"AVID")
        write_uint16(f, 0x01)

        #name size
        data_size_pos = f.tell()
        write_uint16(f, 0x00)
        name = self.__class__.__name__
        f.write(name)

        # TitleRectangle has a extra null byte at end
        if name in (b'TitleRectangle',):
            write_byte(f, 0)
        update_size(f, data_size_pos)

        write_byte(f, 0) # always 0
        write_uint16(f, 0) # always 0

        write_uint16(f, 4) # layer_id size
        write_uint32(f, self.layer_id)
        self.write_props(f)

    def write_props(self, f):
        prop_ids = [0x01, 0x04, 0x03, 0x42]
        i = 0
        # parent_id 0x01
        p = prop_ids[i]
        write_uint16(f, p)
        write_uint16(f, 4)
        write_uint32(f, self.parent_id)
        i+=1

        # bbox 0x04
        p = prop_ids[i]
        write_uint16(f, p)
        write_uint16(f, 8)
        for x in range(4):
            write_int16(f, self.bbox[x])
        i+=1

        # lock 0x03
        p = prop_ids[i]
        write_uint16(f, p)
        write_uint16(f, 2)
        write_uint16(f, self.lock)
        i+=1

        # unknown 0x42
        p = prop_ids[i]
        write_uint16(f, p)
        write_uint16(f, 4)
        write_uint32(f, 0)
        i+=1

    def read_property_value(self, code, raw_data):
        # print "0x%02X" % code
        if not code in self.prop_ids:
            raise Exception("unknown code 0x%02X" % code)

        desc = codes.title_codes[code]
        pack_format = desc[1]
        if pack_format == -1:
            # print "varable code 0x%02X" % code
            return

        name = desc[0]
        if name.startswith(b"?"):
            value = unpack(pack_format, raw_data)
            # print '??', self.__class__.__name__, name, "0x%02X" % code,  value
            return

        if not hasattr(self, name):
            # print self.__dict__.keys()
            raise Exception("undefined attr %s code 0x%02X" % (name, code))

        value = unpack(pack_format, raw_data)
        if len(value) == 1:
            value = value[0]

        # print self.__class__.__name__, name, "0x%02X" % code,  value
        setattr(self, name, value)


class TitlePage(TitleBase):
    def __init__(self):
        super(TitlePage , self).__init__()
        self.prop_ids += [0x27, 0x26, 0x3C]
        self.fonts = {}
        self.fonts[0x0003] = b"Geneva"
        self.layer_id = 7
        self.parent_id = 0
        self.bg_color = (0,0,0)
        self.video_bg = False

    def write_props(self, f):
        super(TitlePage , self).write_props(f)
        prop_ids  = [0x27, 0x26, 0x3C]
        i = 0

        # bg color 0x27
        p = prop_ids[i]
        write_uint16(f, p)
        write_uint16(f, 6)
        for x in range(3):
            write_int16(f, self.bbox[x])
        i+=1

        # video bg 0x26
        p = prop_ids[i]
        write_uint16(f, p)
        write_uint16(f, 2)
        write_uint16(f, self.video_bg)
        i+=1

        # fonts 0x3C
        p = prop_ids[i]
        write_uint16(f, p)
        data_size_pos = f.tell()
        write_uint16(f, 0)
        self.write_fonts(f)
        update_size(f, data_size_pos)

    def write_fonts(self, f):

        write_uint16(f, 0)
        write_uint16(f, len(self.fonts))
        for font_id, font_name in sorted(self.fonts.items()):
            self.write_font(f, font_id, font_name)

    def write_font(self, f, font_id, font_name):
        buf = bytearray(260)
        font = BytesIO(buf)

        write_byte(font, len(font_name))
        font.write(font_name)
        font.seek(260-2)
        write_uint16(font, font_id)
        f.write(font.getvalue())

    def read_font_list(self, raw_data):
        f = BytesIO(raw_data)

        size = read_uint16(f)
        array_count = read_uint16(f)

        for i in range(array_count):
            font_data = f.read(260)
            font_reader = BytesIO(font_data)
            font_name_size = read_byte(font_reader)
            font_name = font_reader.read(font_name_size)
            font_reader.seek(260-2)
            font_id = read_uint16(font_reader)
            self.fonts[font_id] = font_name
            # print "0x%04X" % font_id, font_name

    def read_property_value(self, code, raw_data):
        if code == 0x3C:
            self.read_font_list(raw_data)
        else:
            super(TitlePage, self).read_property_value(code, raw_data)

class TitleElement(TitleBase):
    def __init__(self):
        super(TitleElement , self).__init__()
        self.prop_ids += [0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x3F, 0x0C, 0x0D,
                          0x4A, 0x0E, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30,
                          0x31, 0x32, 0x33, 0x34, 0x35]
        self.fill_color = [65535, 65535, 65535]
        self.border_color = [65535, 65535, 65535]
        self.shadow_color = [65535, 65535, 65535]
        self.fill_alpha = 0
        self.border_alpha = 0
        self.shadow_alpha = 0
        self.border_width = 0
        self.shadow_mode = 2
        self.shadow_depth = 0
        self.shadow_blur = 0
        self.shadow_dir = [1,1]

        self.color1 = [65535, 65535, 65535]

        self.fill_gradient_end_transparencey = 100
        self.fill_gradient_dir = 4

        self.color2 = [65535, 65535, 65535]

        self.border_gradient_end_transparencey = 100
        self.border_gradiant_dir = 4

    def write_props(self, f):
        super(TitleElement , self).write_props(f)
        prop_ids = [0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x3F, 0x0C, 0x0D,
                          0x4A, 0x0E, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30,
                          0x31, 0x32, 0x33, 0x34, 0x35]
        i = 0

        # fill_color 0x05
        p = prop_ids[i]
        write_color_prop(f, p, self.fill_color)
        i+=1

        # fill_color 0x06
        p = prop_ids[i]
        write_color_prop(f, p, self.border_color)
        i+=1

        # fill_color 0x07
        p = prop_ids[i]
        write_color_prop(f, p, self.shadow_color)
        i+=1

        # fill_alpha 0x08
        p = prop_ids[i]
        write_uint16_prop(f, p, self.fill_alpha)
        i+=1

        # border_alpha 0x09
        p = prop_ids[i]
        write_uint16_prop(f, p, self.border_alpha)
        i+=1

        # shadow_alpha 0x0A
        p = prop_ids[i]
        write_uint16_prop(f, p, self.shadow_alpha)
        i+=1

        # stroke_width 0x3F
        p = prop_ids[i]
        write_uint16_prop(f, p, self.border_width)
        i+=1

        # shadow_mode
        p = prop_ids[i]
        write_uint16_prop(f, p, self.shadow_mode)
        i+=1

        # shadow_depth
        p = prop_ids[i]
        write_uint16_prop(f, p, self.shadow_depth)
        i+=1

        # shadow_blur
        p = prop_ids[i]
        write_uint16_prop(f, p, self.shadow_blur)
        i+=1

        # shadow_dir 0x0E
        p = prop_ids[i]
        write_uint16(f, p)
        write_uint16(f, 4)
        write_int16(f, self.shadow_dir[0])
        write_int16(f, self.shadow_dir[1])
        i+=1

        # ?? 0x2A
        p = prop_ids[i]
        write_uint16_prop(f, p, 0)
        i+=1

        # ?? color1 0x2B
        p = prop_ids[i]
        write_color_prop(f, p, self.color1)
        i+=1

        # ?? 0x2C
        p = prop_ids[i]
        write_uint16_prop(f, p, 4)
        i+=1

        # ?? 0x2D
        p = prop_ids[i]
        write_uint16_prop(f, p, 0)
        i+=1

        # fill_gradient_end_transparencey 0x2E
        p = prop_ids[i]
        write_uint16_prop(f, p, self.fill_gradient_end_transparencey)
        i+=1

        # fill_gradient_dir 0x2F
        p = prop_ids[i]
        write_uint16_prop(f, p, self.fill_gradient_dir)
        i+=1

        # ?? 0x30
        p = prop_ids[i]
        write_uint16_prop(f, p, 0)
        i+=1

        # ?? color2 0x31
        p = prop_ids[i]
        write_color_prop(f, p, self.color2)
        i+=1

        # ?? 0x32
        p = prop_ids[i]
        write_uint16_prop(f, p, 4)
        i+=1

        # ?? 0x33
        p = prop_ids[i]
        write_uint16_prop(f, p, 0)
        i+=1

        # 0x34 border_gradient_end_transparencey
        p = prop_ids[i]
        write_uint16_prop(f, p, self.border_gradient_end_transparencey)
        i+=1

        # 0x35 border_gradiant_dir
        p = prop_ids[i]
        write_uint16_prop(f, p, self.border_gradiant_dir)
        i+=1


class TextFormat(object):
    def __init__(self):
        self.prop0 = 0
        self.start_index = 0
        self.prop1 = 64
        self.prop2 = 48
        self.font_id = 0x0003
        self.style =  0x100
        self.font_size = 48
        self.prop4 = 0
        self.prop5 = 0
        self.prop6 = 0

    def write(self, f):
        write_uint16(f, self.prop0)
        write_uint16(f, self.start_index)
        write_uint16(f, self.prop1)
        write_uint16(f, self.prop2)
        write_uint16(f, self.font_id)
        write_uint16(f, self.style)
        write_uint16(f, self.font_size)
        write_uint16(f, self.prop4)
        write_uint16(f, self.prop5)
        write_uint16(f, self.prop6)

    def read(self, f):
        self.prop0 = read_uint16(f)
        self.start_index = read_uint16(f)
        self.prop1 = read_uint16(f)
        self.prop2 = read_uint16(f)
        self.font_id = read_uint16(f)
        self.style =  read_uint16(f)
        self.font_size = read_uint16(f)
        self.prop4 = read_uint16(f)
        self.prop5 = read_uint16(f)
        self.prop6 = read_uint16(f)

class TitleText(TitleElement):
    def __init__(self, text=None):
        super(TitleText , self).__init__()
        self.prop_ids += [0x3B, 0x24, 0x25, 0x40, 0x41]
        self.text = text
        self.text_formating = []
        self.justify = 0
        self.global_kerning = 1000
        self.leading = 0
        self.kerning = []
        self.justify_types = {0x000: None,
                              0x0001:"center",
                              0xFFFE: "left",
                              0xFFFF: "right" }
        self.styles =  {0x00:None,
                        0x0100:"bold",
                        0x0200:'italic',
                        0x0300:'bold italic'}

    def write_props(self, f):
        super(TitleText , self).write_props(f)
        prop_ids = [0x3B, 0x24, 0x25, 0x40, 0x41]
        i = 0

        # 0x3B text_formats
        p = prop_ids[i]
        write_uint16(f, p)
        data_size_pos = f.tell()
        write_uint16(f, 0)
        self.write_text_formats(f)
        update_size(f, data_size_pos)
        i+=1

        # 0x24 justify
        p = prop_ids[i]
        write_uint16_prop(f, p, self.justify)
        i+=1

        # 0x25 global_kerning
        p = prop_ids[i]
        write_int16_prop(f, p, self.global_kerning)
        i+=1

        # 0x40 leading
        p = prop_ids[i]
        write_int16_prop(f, p, self.leading)
        i+=1

        # 0x41 kerning
        p = prop_ids[i]
        write_uint16(f, p)
        data_size_pos = f.tell()
        write_uint16(f, 0)
        self.write_kerning(f)
        update_size(f, data_size_pos)
        i+=1

    def write_text_formats(self, f):

        write_uint16(f, len(self.text))
        f.write(self.text)
        if f.tell() % 2:
            write_byte(f, 0)

        data_size_pos = f.tell()
        write_uint16(f, 0)

        text_formating = self.text_formating
        if not text_formating:
            text_formating = [TextFormat()]


        write_uint16(f, len(text_formating))
        for item in text_formating:
            item.write(f)

        update_size(f, data_size_pos)

    def write_kerning(self, f):

        char_count = len(self.text)
        write_uint16(f, char_count)

        for i in range(char_count):
            write_byte(f, 0)

        write_uint16(f, 0)
        if f.tell() % 2:
            write_byte(f, 0)

    def read_text_data(self, data):
        f = BytesIO(data)
        text_size = read_uint16(f)
        self.text = f.read(text_size)

        # correct alignment
        if f.tell() % 2:
            read_byte(f)

        size = read_uint16(f)
        array_count = read_uint16(f)

        for i in range(array_count):
            tf = TextFormat()
            tf.read(BytesIO(f.read(20)))
            if not self.text_formating:
                self.text_formating = []
            self.text_formating.append(tf)

        assert len(f.read()) == 0

    def read_kerning_data(self, data):
        f = BytesIO(data)
        char_count = read_uint16(f)
        self.kerning = []
        for i in range(char_count):
            value = unpack(b'b', f.read(1))[0]
            self.kerning.append(value)
    def read_property_value(self, code, raw_data):
        if code == 0x3B:
            self.read_text_data(raw_data)
        elif code == 0x41:
            self.read_kerning_data(raw_data)
        else:
            super(TitleText, self).read_property_value(code, raw_data)

class TitleRectangle(TitleElement):
    def __init__(self):
        super(TitleRectangle , self).__init__()
        self.prop_ids += [0x19]
        self.corner_roundness = 0

    def write_props(self, f):
        super(TitleRectangle , self).write_props(f)
        p = 0x19
        write_uint16_prop(f, p, self.corner_roundness)

class TitleOval(TitleElement):
    def __init__(self):
        super(TitleOval , self).__init__()

class TitleLine(TitleElement):
    def __init__(self):
        super(TitleLine , self).__init__()
        self.prop_ids += [0x0F, 0x0B, 0x10, 0x11]
        self.line_width = 1
        self.arrow_type = 0
        self.arrow_desc = (16400, 0, 0, 0, 16384, 0, 0, 0)

    def write_props(self, f):
        super(TitleLine , self).write_props(f)
        prop_ids = [0x0F, 0x0B, 0x10, 0x11]
        i = 0
        # bbox 0x0F same as 0x04?
        p = prop_ids[i]
        write_uint16(f, p)
        write_uint16(f, 8)
        for x in range(4):
            write_int16(f, self.bbox[x])
        i+=1

        # 0x0B line_width
        p = prop_ids[i]
        write_uint16_prop(f, p, self.line_width)
        i+=1

        # 0x10 arrow_type
        p = prop_ids[i]
        write_uint16_prop(f, p, self.arrow_type)
        i+=1

        # 0x11 something to do with custom arrows
        p = prop_ids[i]
        write_uint16(f, p)
        write_uint16(f, 16)
        for x in range(8):
            write_int16(f, self.arrow_desc[x])

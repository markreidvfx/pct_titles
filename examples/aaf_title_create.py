import os
from StringIO import StringIO
import aaf
import aaf.define
from aaf.util import AUID

import fractions

import pct_titles
import traceback

def setup_avid_extensions(f):
    uint8_typedef = f.dictionary.lookup_typedef("UInt8")
    unit16_typedef = f.dictionary.lookup_typedef("UInt16")
    int32_typedef = f.dictionary.lookup_typedef("Int32")

    # this property seems to stop mastermob from showing up in the bin
    mob_classdef = f.dictionary.lookup_classdef("Mob")
    appcode_id = AUID("urn:uuid:96c46992-4f62-11d3-a022-006094eb75cb")
    mob_classdef.register_optional_propertydef(int32_typedef, appcode_id, 'AppCode')

    bagbit_id = AUID('urn:uuid:ccaa73d1-f538-11d3-a081-006094eb75cb')
    bagbit_typedef = aaf.define.TypeDefVariableArray(f, uint8_typedef, bagbit_id, 'AvidBagOfBits')
    f.dictionary.register_def(bagbit_typedef)

    opdef_id = AUID('urn:uuid:2db619ef-7210-4e89-95d7-970336d72e8c')
    opdef = f.create.OperationDef(opdef_id, 'Title_2', "")
    opdef.media_kind = 'picture'

    # AvidGraphicFXAttr
    param_id = AUID('urn:uuid:1fdd2907-e48c-11d3-a078-006094eb75cb')
    graphic_fx_paramdef = f.create.ParameterDef(param_id, 'AvidGraphicFXAttr', "", bagbit_typedef)
    f.dictionary.register_def(graphic_fx_paramdef)
    opdef.add_parameterdef(graphic_fx_paramdef)

    # AvidParameterByteOrder
    param_id = AUID('urn:uuid:c0038672-a8cf-11d3-a05b-006094eb75cb')
    paramdef = f.create.ParameterDef(param_id, 'AvidParameterByteOrder', "", unit16_typedef)
    f.dictionary.register_def(paramdef)
    opdef.add_parameterdef(paramdef)

    # AvidEffectID
    param_id = AUID('urn:uuid:93994bd6-a81d-11d3-a05b-006094eb75cb')
    effect_id_paramdef = f.create.ParameterDef(param_id, 'AvidEffectID', "", bagbit_typedef)
    f.dictionary.register_def(effect_id_paramdef)
    opdef.add_parameterdef(effect_id_paramdef)

    f.dictionary.register_def(opdef)

def create_cdci_desc(f, rate):
    component_width = 8
    horizontal_subsampling = 2 # 2 means 4:2:2
    vertical_subsampling = 1
    color_range = 255
    width = 1920
    height = 1080
    size = (width, height)
    rect = (width, height, 0, 0)
    desc = f.create.CDCIDescriptor()
    desc.stored_view = (width, height)
    desc.sampled_view = rect
    desc.display_view = rect
    desc.layout = 'FullFrame'
    desc.line_map = (0,)
    desc.component_width = component_width
    desc.horizontal_subsampling = horizontal_subsampling
    desc.vertical_subsampling = vertical_subsampling
    desc.color_range = color_range
    # desc['Compression'].value = aaf.util.AUID.from_urn_smpte_ul(profile_id)
    desc['SampleRate'].value = rate
    desc['ImageAspectRatio'].value = fractions.Fraction(width, height)
    desc['ContainerFormat'].value = f.dictionary.lookup_containerdef("AAFKLV")
    return desc

def create_rgba_desc(f, rate):
    component_width = 8
    horizontal_subsampling = 2 # 2 means 4:2:2
    vertical_subsampling = 1
    color_range = 255
    width = 1920
    height = 1080
    size = (width, height)
    rect = (width, height, 0, 0)
    desc = f.create.RGBADescriptor()
    desc.stored_view = (width, height)
    desc.sampled_view = rect
    desc.display_view = rect
    desc.layout = 'FullFrame'
    desc.line_map = (42,0)
    desc['SampleRate'].value = rate
    desc['ImageAspectRatio'].value = fractions.Fraction(width, height)
    desc['ContainerFormat'].value = f.dictionary.lookup_containerdef("AAFKLV")
    return desc

def create_title(f, pct_data, mob_name=None):
    if not mob_name:
        mob_name = "Generated text"

    clip_length = 2877
    rate = "24000/1001"

    opdef = f.dictionary.lookup_operationdef("Title_2")
    graphic_fx_paramdef = f.dictionary.lookup_parameterdef('AvidGraphicFXAttr')
    effect_id_paramdef = f.dictionary.lookup_parameterdef('AvidEffectID')
    byteorder_paramdef = f.dictionary.lookup_parameterdef('AvidParameterByteOrder')


    # aaf.essence.ImportDescriptor source_mob Untitled
    import_mob = f.create.SourceMob(mob_name)
    desc = f.create.ImportDescriptor()
    import_mob.essence_descriptor = desc

    import_mob.add_nil_ref(1, clip_length, "picture", "24000/1001")
    tc = aaf.util.Timecode(start_frame=86400, fps=24)
    import_mob.append_timecode_slot("24000/1001", 2, tc, clip_length)
    import_mob.add_nil_ref(3, clip_length, "picture", "24000/1001")
    f.storage.add_mob(import_mob)

    # aaf.essence.RGBADescriptor Untitled.PHYS
    source_mob = f.create.SourceMob("%s.PHYS" % mob_name)
    source_mob.essence_descriptor = create_rgba_desc(f, rate)

    timeline = f.create.TimelineMobSlot()
    timeline.editrate = "24000/1001"
    timeline.slot_id = 1
    timeline['PhysicalTrackNumber'].value = 2

    clip = f.create.SourceClip("picture")
    clip.length = clip_length
    clip.slot_id = 3
    clip.mob_id = import_mob.mob_id
    timeline.segment = clip

    source_mob.append_slot(timeline)
    f.storage.add_mob(source_mob)

    rgba_mob = source_mob

    # source_cdci1 aaf.essence.CDCIDescriptor Untitled.PHYS
    source_mob = f.create.SourceMob("%s.PHYS" % mob_name)
    source_mob.essence_descriptor = create_cdci_desc(f, rate)
    timeline = f.create.TimelineMobSlot()
    timeline.editrate = "24000/1001"
    timeline.slot_id = 1
    timeline['PhysicalTrackNumber'].value = 2

    clip = f.create.SourceClip("picture")
    clip.length = clip_length
    clip.slot_id = 3
    clip.mob_id = import_mob.mob_id
    timeline.segment = clip

    source_mob.append_slot(timeline)
    f.storage.add_mob(source_mob)

    source_cdci1= source_mob

    # source_cdci2 aaf.essence.CDCIDescriptor Untitled.PHYS
    source_mob = f.create.SourceMob("%s.PHYS" % mob_name)
    source_mob.essence_descriptor = create_cdci_desc(f, rate)
    timeline = f.create.TimelineMobSlot()
    timeline.editrate = "24000/1001"
    timeline.slot_id = 1
    timeline['PhysicalTrackNumber'].value = 1

    clip = f.create.SourceClip("picture")
    clip.length = clip_length
    clip.slot_id = 1
    clip.mob_id = import_mob.mob_id
    timeline.segment = clip

    source_mob.append_slot(timeline)
    f.storage.add_mob(source_mob)

    source_cdci2= source_mob

    # setup mastermob
    mastermob = f.create.MasterMob(mob_name)
    timeline = f.create.TimelineMobSlot()
    timeline.editrate = "24000/1001"
    timeline.slot_id = 1
    timeline['PhysicalTrackNumber'].value = 1

    # clip 1 CDCIDescriptor
    ess = f.create.EssenceGroup()
    ess.media_kind = "picture"
    ess.length = clip_length
    timeline.segment = ess

    clip = f.create.SourceClip("picture")
    clip.length = clip_length
    clip.slot_id = 1
    clip.mob_id = source_cdci2.mob_id
    ess.append(clip)
    mastermob.append_slot(timeline)

    # clip2 CDCIDescriptor
    timeline = f.create.TimelineMobSlot()
    timeline.editrate = "24000/1001"
    timeline.slot_id = 2
    timeline['PhysicalTrackNumber'].value = 2

    ess = f.create.EssenceGroup()
    ess.media_kind = "picture"
    ess.length = clip_length
    timeline.segment = ess

    clip = f.create.SourceClip("picture")
    clip.length = clip_length
    clip.slot_id = 1
    clip.mob_id = source_cdci1.mob_id
    ess.append(clip)

    #clip3 RGBADescriptor

    clip = f.create.SourceClip("picture")
    clip.length = clip_length
    clip.slot_id = 1
    clip.mob_id = rgba_mob.mob_id
    ess.append(clip)

    mastermob.append_slot(timeline)

    mastermob.usage_code = "Usage_LowerLevel"
    mastermob['AppCode'].value = 1
    f.storage.add_mob(mastermob)

    # setup operation group
    title_op = f.create.OperationGroup("picture", clip_length, opdef)

    # buf = bytearray(os.path.getsize(pct_file_path))
    # pct = open(pct_file_path, 'rb')
    #
    # pct.readinto(buf)

    gfx = f.create.ConstantValue(graphic_fx_paramdef, pct_data)
    effect_id = f.create.ConstantValue(effect_id_paramdef, bytearray(b'EFF2_BLEND_GRAPHIC\x00'))

    title_op.add_parameter(gfx)
    title_op.add_parameter(effect_id)

    seq = f.create.Sequence("picture")
    seq.length = clip_length

    scope = f.create.ScopeReference("picture", 1, 1)
    scope.length = clip_length
    seq.append(scope)

    title_op.append(seq)

    clip = f.create.SourceClip("picture")
    clip.length = clip_length
    clip.slot_id = 1
    clip.mob_id = mastermob.mob_id

    title_op.append(clip)

    clip = f.create.SourceClip("picture")
    clip.length = clip_length
    clip.slot_id = 2
    clip.mob_id = mastermob.mob_id

    title_op.append(clip)

    # setup composition
    comp = f.create.CompositionMob()
    comp.name = mob_name
    comp.usage_code = "Usage_Template"

    timeline = f.create.TimelineMobSlot()
    timeline.editrate = "24000/1001"
    timeline.slot_id = 1
    timeline.segment = title_op
    comp.append_slot(timeline)

    f.storage.add_mob(comp)

def generate_pct_data():
    import write_test

    pct_file = write_test.generate_test_title()
    data = StringIO()

    pct_file.aaf_mode = True
    pct_file.write(data)

    return bytearray(data.getvalue())

def read_pct_data(pct_path):
    pct_file = pct_titles.PctFile()
    try:
        pct_file.read(pct_path)
    except:
        print "error reading %s" % pct_path
        print traceback.format_exc()
        return None

    data = StringIO()

    pct_file.aaf_mode = True
    pct_file.write(data)

    return bytearray(data.getvalue())

if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser()

    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("not enough args")

    aaf_path = None
    pct_paths = []

    for arg in args:
        name, ext = os.path.splitext(arg)
        if ext and ext.lower() in ('.pct', '.pict'):
            pct_paths.append(arg)
        elif ext and ext.lower() in ('.aaf', '.xml'):
            if aaf_path:
                parser.error("multiple aaf specified")
            aaf_path = arg
        else:
            parser.error("unkown file tyep: %s" % arg)
    pct_data = None
    if not pct_paths:
        pct_data = generate_pct_data()

    if not aaf_path:
        aaf_path = os.path.splitext(pct_paths[0])[0] + '.aaf'

    f = aaf.open(aaf_path, 'w')
    try:
        setup_avid_extensions(f)
        if pct_data:
            create_title(f, pct_data)

        for path in pct_paths:
            basename = os.path.basename(path)
            mob_name = os.path.splitext(basename)[0]
            # print "reading", path
            pct_data = read_pct_data(path)
            if pct_data:
                # print "adding to aaf", path
                create_title(f, pct_data, mob_name)
    finally:

        f.save()
        f.close()

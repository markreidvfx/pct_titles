from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
import aaf2
import pct_titles
import io
from aaf2.auid import AUID

def extract_markers(path):
    markers = []
    with aaf2.open(path) as f:
        sequence = next(f.content.toplevel())

        for slot in sequence.slots:
            if isinstance(slot, aaf2.mobslots.EventMobSlot):
                for marker in slot.segment.components:
                    comment = marker['Comment'].value
                    markers.append(comment)
    return markers

def setup_title_operation_def(f):
    opdef_id = AUID('2db619ef-7210-4e89-95d7-970336d72e8c')
    opdef = f.create.OperationDef(opdef_id, 'Title_2', "")
    opdef.media_kind = 'picture'
    opdef['NumberInputs'].value = 3
    opdef['IsTimeWarp'].value = False
    opdef['Bypass'].value = 0
    opdef['OperationCategory'].value = "OperationCategory_Effect"

    bagbit_typedef = f.metadict.lookup_typedef('AvidBagOfBits')

    # AvidGraphicFXAttr
    param_id = AUID('1fdd2907-e48c-11d3-a078-006094eb75cb')
    graphic_fx_paramdef = f.create.ParameterDef(param_id, 'AvidGraphicFXAttr', "", bagbit_typedef)
    f.dictionary.register_def(graphic_fx_paramdef)
    opdef.parameters.append(graphic_fx_paramdef)

    # AvidEffectID
    param_id = AUID('93994bd6-a81d-11d3-a05b-006094eb75cb')
    effect_id_paramdef = f.create.ParameterDef(param_id, 'AvidEffectID', "", bagbit_typedef)
    f.dictionary.register_def(effect_id_paramdef)
    opdef.parameters.append(effect_id_paramdef)

    f.dictionary.register_def(opdef)

def create_rgba_descriptor(f, rate, length):
    width = 1920
    height = 1080

    desc = f.create.RGBADescriptor()
    desc['StoredWidth'].value = width
    desc['StoredHeight'].value = height
    desc['FrameLayout'].value = 'FullFrame'
    desc['VideoLineMap'].value = (0,)
    desc['SampleRate'].value = rate
    desc['ImageAspectRatio'].value = "%d/%d" % (width, height)
    desc['PixelLayout'].value =  [{'Code': 'CompAlpha', 'Size': 8}]
    desc['Length'].value = 0

    return desc

def create_cdci_desc(f, rate, length):
    component_width = 8
    horizontal_subsampling = 2 # 2 means 4:2:2
    vertical_subsampling = 1
    color_range = 255
    width = 1920
    height = 1080

    desc = f.create.CDCIDescriptor()
    desc['StoredWidth'].value = width
    desc['StoredHeight'].value = height
    desc['ComponentWidth'].value = component_width
    desc['HorizontalSubsampling'].value = horizontal_subsampling
    desc['VerticalSubsampling'].value = vertical_subsampling
    desc['ColorRange'].value = color_range
    desc['FrameLayout'].value = 'FullFrame'
    desc['VideoLineMap'].value =  [0,]
    desc['ImageAspectRatio'].value = "%d/%d" % (width, height)
    desc['SampleRate'].value = rate
    desc['Length'].value = 0

    return desc

def encode_indirect(item, key, value, value_typedef):
    item[key].add_pid_entry()
    item[key].data = item['Value'].typedef.encode(value, value_typedef)
    item[key].mark_modified()

def create_title(f, pct_data, text):
    clip_length = 2877
    edit_rate = "24000/1001"

    opdef = f.dictionary.lookup_operationdef("Title_2")
    graphic_fx_paramdef = f.dictionary.lookup_parameterdef('AvidGraphicFXAttr')
    effect_id_paramdef = f.dictionary.lookup_parameterdef('AvidEffectID')

    mob_name = text

    # aaf.essence.ImportDescriptor
    import_mob = f.create.SourceMob(mob_name)
    import_mob.descriptor = f.create.ImportDescriptor()

    import_slot1 = import_mob.create_empty_slot(edit_rate)
    import_slot1.segment.length = clip_length
    import_slot2 = import_mob.create_timecode_slot(edit_rate, 24, drop_frame=False)
    import_slot2.segment.length = clip_length
    import_slot2.segment.start = 86400
    import_slot3 = import_mob.create_empty_slot(edit_rate)
    import_slot3.segment.length = clip_length

    f.content.mobs.append(import_mob)

    # aaf.essence.RGBADescriptor Untitled.PHYS
    rgba_mob = f.create.SourceMob("%s.PHYS" % mob_name)
    rgba_mob.descriptor = create_rgba_descriptor(f, edit_rate, clip_length)

    rgba_slot1 = rgba_mob.create_empty_slot(edit_rate)
    rgba_slot1.segment = import_mob.create_source_clip(3, 0, clip_length)

    f.content.mobs.append(rgba_mob)

    # source_cdci1 aaf.essence.CDCIDescriptor Untitled.PHYS
    source_cdci1 = f.create.SourceMob("%s.PHYS" % mob_name)
    source_cdci1.descriptor = create_cdci_desc(f, edit_rate, clip_length)

    source_cdci1_slot = source_cdci1.create_empty_slot(edit_rate)
    source_cdci1_slot.segment = import_mob.create_source_clip(3, 0, clip_length)

    f.content.mobs.append(source_cdci1)

     # source_cdci2 aaf.essence.CDCIDescriptor Untitled.PHYS
    source_cdci2 = f.create.SourceMob("%s.PHYS" % mob_name)
    source_cdci2.descriptor = create_cdci_desc(f, edit_rate, clip_length)

    source_cdci2_slot = source_cdci2.create_empty_slot(edit_rate)
    source_cdci2_slot.segment = import_mob.create_source_clip(1, 0, clip_length)

    f.content.mobs.append(source_cdci2)

    # mastermob
    mastermob = f.create.MasterMob(mob_name)
    mastermob.usage = 'Usage_LowerLevel'
    mastermob['AppCode'].value = 1

    # clip 1 CDCIDescriptor
    mastermob_slot1 = mastermob.create_picture_slot(edit_rate)

    ess = f.create.EssenceGroup()
    ess.media_kind = "picture"
    ess.length = clip_length
    mastermob_slot1.segment = ess

    ess['Choices'].append(source_cdci2.create_source_clip(1, 0, clip_length))

    # clip2 CDCIDescriptor
    mastermob_slot2 = mastermob.create_picture_slot(edit_rate)

    ess = f.create.EssenceGroup()
    ess.media_kind = "picture"
    ess.length = clip_length
    mastermob_slot2.segment = ess
    ess['Choices'].append(source_cdci1.create_source_clip(1, 0, clip_length))

    # clip3 RGBADescriptor
    ess['Choices'].append(rgba_mob.create_source_clip(1, 0, clip_length))

    f.content.mobs.append(mastermob)

    # setup operation group
    title_op = f.create.OperationGroup(opdef, clip_length)

    # graphic_fx_paramdef, pct_data
    gfx = f.create.ConstantValue(graphic_fx_paramdef, bytearray(pct_data))
    effect_id = f.create.ConstantValue(effect_id_paramdef, bytearray(b'EFF2_BLEND_GRAPHIC\x00'))

    title_op.parameters.append(gfx)
    title_op.parameters.append(effect_id)

    seq = f.create.Sequence("picture")
    seq.length = clip_length

    scope = f.create.ScopeReference("picture")
    scope.length = clip_length
    scope['RelativeScope'].value = 1
    scope['RelativeSlot'].value = 1

    seq.components.append(scope)
    title_op.segments.append(seq)
    title_op.segments.append(mastermob.create_source_clip(1, 0 , clip_length))
    title_op.segments.append(mastermob.create_source_clip(2, 0 , clip_length))

    # setup composition
    comp = f.create.CompositionMob(mob_name)
    comp.usage = "Usage_Template"

    comp_slot = comp.create_timeline_slot(edit_rate)
    comp_slot.segment = title_op

    f.content.mobs.append(comp)

def apply_template(template_path, text):
    pct_file = pct_titles.PctFile()
    pct_data = io.BytesIO()
    with io.open(template_path, 'rb') as f:
        pct_file.read(f)

        for item in pct_file.elements:
            if isinstance(item, pct_titles.TitleText):
                item.text = item.text.replace(b"#MARKER", text.encode('utf-8'))

        pct_file.aaf_mode = True
        pct_file.write(pct_data)

    return bytearray(pct_data.getvalue())

def markers2titles(markers, pct_path, dest):

    with aaf2.open(dest, 'w') as f:
        setup_title_operation_def(f)
        # for text in ('title_01', 'cow', 'pig', 'dog', u'whatever', 'nik', 'mark'):
        for text in markers:
            print(text)
            pct_data = apply_template(pct_path, text)
            create_title(f, pct_data, text)
        # f.content.dump()

if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser()
    (options, args) = parser.parse_args()

    if not args:
        parser.error("not enough arguments")

    path = args[0]
    markers = extract_markers(path)
    markers2titles(markers, './title.pct', 'titles.aaf')

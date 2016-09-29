import pct_titles
import os


def generate_test_title():
    pct = pct_titles.PctFile()

    text = pct_titles.TitleText("text in roughly in the center")

    width = 865
    height = 485

    # min_y, min_x , max_y, max_x
    text.bbox = (107, 217, 379, 647)
    text.fill_color = [65535, 0, 0] # red
    text.justify = 0x0001

    text_format = pct_titles.TextFormat()
    text_format.font_size = 48 * 2
    text.text_formating.append(text_format)

    rect = pct_titles.TitleRectangle()
    rect.fill_color = [0, 65535, 0]

    edge = 10
    rect.bbox = [edge, edge, height - edge, width - edge]

    oval = pct_titles.TitleOval()
    oval.fill_color = [0, 0, 65535]

    line = pct_titles.TitleLine()
    line.line_width = 10

    line2 = pct_titles.TitleLine()
    line2.line_width = 10
    line2.bbox = [height, 0, 0, width]

    pct.add_element(rect)
    pct.add_element(oval)
    pct.add_element(line)
    pct.add_element(line2)
    pct.add_element(text)

    return pct

if __name__ == "__main__":
    pct = generate_test_title()
    pct.write(os.path.join(os.path.dirname(__file__),"write_test.pct"))

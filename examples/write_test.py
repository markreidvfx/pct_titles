import pct_titles

pct = pct_titles.PctFile()
text = pct_titles.TitleText("text addlafjdlsakfjdalskfjdsalkfjldsk")

print text.bbox

text.bbox = [0, 0, 512, 512]

rect = pct_titles.TitleRectangle()
line = pct_titles.TitleLine()
oval = pct_titles.TitleOval()
pct.add_element(text)
# pct.add_element(line)
# pct.add_element(rect)
# pct.add_element(oval)
pct.write("test.pct")

pct.dump()

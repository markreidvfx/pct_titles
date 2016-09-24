import pct_titles
import sys
pct = pct_titles.PctFile()

pct.read(sys.argv[1])


pct.write("rewrite.pct")

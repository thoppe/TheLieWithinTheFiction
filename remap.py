import bs4
import os, shutil
from copy import copy

import brotli
import fontTools
import zopfli

f_otf = 'helvetica-bold.otf'

f_xml  = 'helvetica-bold.ttx'
f_xml2 = 'helvetica-bold-remapped.ttx'
f_otf2 = f_xml2.replace('.ttx','.wotf2')

for f in [f_xml, f_xml2, f_otf2]:
    if os.path.exists(f):
        os.remove(f)


table = {}
s1 = 'Thequickbrownfox'
s2 = 'Onejazzypizzapie'
for a1,a2 in zip(s1,s2):
    if a1 == a2: continue
    
    if a1 in table:
        print "WARNING!: Remapped key twice", a1, a2, table[a1]
    table[a1] = a2

#table = {'q':'j'}
os.system('ttx {}'.format(f_otf))

with open(f_xml, 'rb') as FIN:
    soup = bs4.BeautifulSoup(FIN.read(), 'xml')

salad = copy(soup)

# Scrub the remaining CharStrings not used
keep_keys = set(table.keys())
keep_keys.add('space')
keep_keys.add('nonbreakingspace')
keep_keys.add('.notdef')

'''
for block in salad.find_all("CharString"):
    if 'name' in block.attrs:
        name = block['name']
        if name[0] == '.': continue
        if len(name)>1: continue
        print "EXTRACTING", name
        if name not in keep_keys:
            for item in salad.find_all("", {"name":name}):
                item.extract()
            for item in salad.find_all("", {"glyph":name}):
                item.extract()
'''

# Swap the values
for key, val in table.iteritems():

    print "Swapping key/val", key, val

    # Swap the correct width, lsb
    mtx_key = salad.find('mtx', {"name":key})
    mtx_val = soup.find('mtx', {"name":val})

    mtx_key['width'] = mtx_val['width']
    mtx_key['lsb'] = mtx_val['lsb']

    # Swap the CharString
    contents = soup.find('CharString', {"name":val}).text
    salad.find('CharString', {"name":key}).string = contents

# Delete GPOS, name
#salad.find("GPOS").extract()
#salad.find("name").extract()
#salad.find("cmap_format_0").extract()
#salad.find("cmap_format_4").extract()

with open(f_xml2, 'wb') as FOUT:
    FOUT.write(salad.prettify('utf-8'))

os.system('ttx --with-zopfli --flavor woff2 --recalc-timestamp -b {}'.format(f_xml2))

for f in [f_xml, f_xml2]:
    if os.path.exists(f):
        os.remove(f)


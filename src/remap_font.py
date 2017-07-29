import bs4
import os, subprocess, shutil
from copy import copy
from backports import tempfile

import brotli
import fontTools
from fontTools import ttLib
from tqdm import tqdm


def clean_font(soup, table, charmaps):

    # Keep all characters in the table, find their real names
    keep_names = [charmaps[key] for key in table.keys()]

    # Always save the .notdef
    keep_names.append('.notdef')
    
    # Keep chars with kern information
    for item in soup.find('GPOS').find_all('Glyph', {"value":True}):
        keep_names.append(item['value'])

    for item in soup.find('GPOS').find_all('SecondGlyph', {"value":True}):
        keep_names.append(item['value'])

    glyphID = soup.find("GlyphOrder").find_all
    hmtx = soup.find("hmtx").find_all
    GDEF = soup.find("GDEF").find_all
    CFF  = soup.find("CFF").find_all
    cmap = soup.find("cmap").find_all

    ITR = list(soup.find_all("GlyphID"))

    print "Removing unused glyphs"
    
    for g in tqdm(ITR):
        
        name = g['name']
        if name in keep_names:
            continue

        [x.decompose() for x in CFF('CharString', {"name":name})]
        [x.decompose() for x in cmap('map', {"name":name})]
        [x.decompose() for x in GDEF('ClassDef', {"glyph":name})]
        [x.decompose() for x in hmtx('mtx', {"name":name})]
        [x.decompose() for x in glyphID('GlyphID', {"name":name})]


    # Remove meta information (todo?)

def modify_font(f_otf, f_otf2, table, clean=True):

    font = ttLib.TTFont(f_otf)
    
    charmaps = {}
    for key, vals in font['cmap'].buildReversed().items():
        for val in vals:
            charmaps[unichr(val)] = key

    # nonbreakingspace is not always the same thing
    nbsp_name = charmaps[unichr(160)]

    # Add the space proxy to the table
    for key,val in table.items():
        if val == ' ':
            table[key] = nbsp_name

    org_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        f_xml  = 'font_info.ttx'
        f_xml2  = 'modified_font_info.ttx'
        cmd = 'ttx -q -o {} {}'.format(f_xml, os.path.join(org_dir, f_otf))
        subprocess.call(cmd, shell=True)

        with open(f_xml, 'rb') as FIN:
            soup = bs4.BeautifulSoup(FIN.read(), 'xml')
            salad = copy(soup)

        salad_mtx = salad.find('hmtx')
        soup_mtx  = soup.find('hmtx')

        salad_CFF = salad.find('CFF')
        soup_CFF  = soup.find('CFF')

        # Swap the values
        for key, val in table.iteritems():
            if key == val:
                continue

            if val in unichr(160):
                val = nbsp_name
            
            mtx_key = salad_mtx.find('mtx', {"name":key})
            mtx_val = soup_mtx.find('mtx', {"name":val})

            # If keys are missing, need to use value from charmap
            if mtx_key is None:
                key = charmaps[key]
                mtx_key = salad_mtx.find('mtx', {"name":key})

            if mtx_val is None:
                val = charmaps[val]
                mtx_val = salad_mtx.find('mtx', {"name":val})

            # If keys are still missing, we don't know what the eff this is
            if mtx_key is None:
                raise KeyError("font missing character '%s'"%key)

            if mtx_val is None:
                raise KeyError("font missing character '%s'"%val)
            
            # Swap the correct width, lsb
            mtx_key['width'] = int(mtx_val['width'])
            mtx_key['lsb'] = int(mtx_val['lsb'])

            if key == nbsp_name:
                mtx_key['width'] = int(mtx_key['width']*1.15) 

            # Swap the CharString
            contents = soup_CFF.find('CharString', {"name":val}).text
            salad_CFF.find('CharString', {"name":key}).string = contents
            
        if clean:
            clean_font(salad, table, charmaps)

        with open(f_xml2, 'wb') as FOUT:
            FOUT.write(salad.prettify('utf-8'))

        cmd = 'ttx -q --recalc-timestamp -b {}'.format(f_xml2)
        subprocess.call(cmd, shell=True)
        f_out = f_xml2.replace('.ttx', '.otf')
        
        shutil.move(f_out,os.path.join(org_dir, f_otf2))
        #os.system('bash')
        
    os.chdir(org_dir)

if __name__ == "__main__":
    f_otf  = 'fonts/helvetica-bold.otf'
    f_oft2 = f_otf.replace('.otf','_modified.otf')

    table = {}
    s1 = 'The quick brown'
    s2 = 'One jazzy pizza'
    
    for a1,a2 in zip(s1,s2):
        if a1 in table and a1 != a2:
            print "WARNING!: Remapped key twice", a1, a2, table[a1]
        table[a1] = a2

    print "Modification table", table

    modify_font(f_otf, f_oft2, table)

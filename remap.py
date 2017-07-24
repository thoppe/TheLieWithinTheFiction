import bs4
import os, subprocess, shutil
from copy import copy
from backports import tempfile

import brotli
import fontTools

def modify_font(f_otf, f_woff2, table):

    org_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        f_xml  = 'font_info.ttx'
        f_xml2  = 'modified_font_info.ttx'
        cmd = 'ttx -o {} {}'.format(f_xml, os.path.join(org_dir, f_otf))
        subprocess.call(cmd, shell=True)

        with open(f_xml, 'rb') as FIN:
            soup = bs4.BeautifulSoup(FIN.read(), 'xml')
            salad = copy(soup)

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


        with open(f_xml2, 'wb') as FOUT:
            FOUT.write(salad.prettify('utf-8'))

        cmd = 'ttx --flavor woff2 --recalc-timestamp -b {}'.format(f_xml2)
        subprocess.call(cmd, shell=True)

        f_out = f_xml2.replace('.ttx', '.woff2')
        shutil.move(f_out,os.path.join(org_dir, f_woff2))
        #os.system('bash')
        
    os.chdir(org_dir)

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

    # Scrub the remaining CharStrings not used
    #keep_keys = set(table.keys())
    #keep_keys.add('space')
    #keep_keys.add('nonbreakingspace')
    #keep_keys.add('.notdef')

    # Delete GPOS, name
    #salad.find("GPOS").extract()
    #salad.find("name").extract()
    #salad.find("cmap_format_0").extract()
    #salad.find("cmap_format_4").extract()


if __name__ == "__main__":
    f_otf  = 'fonts/helvetica-bold.otf'
    f_woff2 = f_otf.replace('.otf','_modified.woff2')


    table = {}
    s1 = 'Thequickbrown'
    s2 = 'Onejazzypizza'
    for a1,a2 in zip(s1,s2):
        if a1 == a2: continue
    
        if a1 in table:
            print "WARNING!: Remapped key twice", a1, a2, table[a1]
        table[a1] = a2

    modify_font(f_otf, f_woff2, table)


import bs4, os
from src.remap_font import modify_font

f_html  = "source.html"
f_html2 = "demo.html"

with open(f_html) as FIN:
    soup = bs4.BeautifulSoup(FIN.read(), "html5lib")

search_dict = {"data-hidden-text":True, "data-visible-text":True}
for block in soup.find_all("", search_dict):
    text1 = block['data-hidden-text']
    text2 = block['data-visible-text']
    font_family = block['data-font-family']
    f_otf = block['data-font']

    del block['data-hidden-text']
    del block['data-visible-text']
    del block['data-font-family']
    del block['data-font']
    block.string = text1

    assert(os.path.exists(f_otf))

    table = {}
    for a1,a2 in zip(text1, text2):
        if a1 in table and a1 != a2:
            print "WARNING!: Remapped key twice", a1, a2, table[a1]
        table[a1] = a2

    print "Modification table", table

    # Build the font
    f_woff2 = f_otf.replace('.otf','_modified.woff2')
    modify_font(f_otf, f_woff2, table)

    # Build the font-face remapping
    f_css = f_html2.replace('.html', '_fontface.css')
    style_text = '''
    @font-face {{
       font-family: "{fontfam}";
       src:url({f_otf});
    }}
    @font-face {{
       font-family: "{fontfam}_modified";
       src:url({f_woff2});
    }}
    '''
    args = {
        "fontfam":font_family,
        "f_otf":f_otf,
        "f_woff2":f_woff2,
    }
    with open(f_css, 'w') as FOUT:
        FOUT.write(style_text.format(**args))

    # Add the header block
    style_tag = soup.new_tag('link',
                             rel='stylesheet',
                             href=f_css)
    soup.find('head').insert(0, style_tag)

    with open(f_html2,'w') as FOUT:
        FOUT.write(soup.prettify())

    print "Output written to", f_html2
    


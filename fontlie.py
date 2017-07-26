import bs4, os
from src.multimap_code import translate_tables

f_html  = "source.html"
f_html2 = "demo.html"

with open(f_html) as FIN:
    soup = bs4.BeautifulSoup(FIN.read(), "html5lib")

search_dict = {"data-hidden-text":True, "data-visible-text":True}
for block in soup.find_all("", search_dict):
    text_hidden = block['data-hidden-text']
    text_visible = block['data-visible-text']
    font_family = block['data-font-family']
    f_otf = block['data-font']

    del block['data-hidden-text']
    del block['data-visible-text']
    del block['data-font-family']
    del block['data-font']
    assert(os.path.exists(f_otf))

    T = translate_tables(f_otf, font_family)

    html = T.encode(text_visible, text_hidden)
    #html = T.encode(text_hidden, text_visible)
    
    block.insert(0, html)

    T.build_fonts()
    
    # Build the font-face remapping
    f_css = f_html2.replace('.html', '_fontface.css')
    with open(f_css, 'w') as FOUT:
        FOUT.write(T.build_CSS())
    

    # Add the header block
    style_tag = soup.new_tag('link',
                             rel='stylesheet',
                             href=f_css)
    soup.find('head').insert(0, style_tag)

    with open(f_html2,'w') as FOUT:
        FOUT.write(unicode(soup))

    print "Output written to", f_html2
    


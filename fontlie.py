import bs4, os, shutil
from src.multimap_code import translate_tables

f_html  = "source.html"
f_html2 = "docs/index.html"
working_dir = os.path.dirname(f_html2)

with open(f_html) as FIN:
    soup = bs4.BeautifulSoup(FIN.read(), "html5lib")

search_dict = {"data-hidden-text":True, "data-visible-text":True}
for block in soup.find_all("", search_dict):

    # Extract the info and clean the block
    text_hidden = block['data-hidden-text']
    text_visible = block['data-visible-text']
    font_family = block['data-font-family']
    f_otf = block['data-font']

    del block['data-hidden-text']
    del block['data-visible-text']
    del block['data-font-family']
    del block['data-font']
    assert(os.path.exists(f_otf))
    
    # Add nonbreaking spaces for overlap, spaces for overlap
    th, tv = [], []
    for a1, a2 in zip(text_hidden, text_visible):
        if a1 == a2 == ' ':
            a1 = a2 = ' '
        elif a1 == ' ':
            a1 = unichr(160)
        elif a2 == ' ':
            a2 = unichr(160)
        th.append(a1)
        tv.append(a2)

    T = translate_tables(f_otf, font_family)

    text_hidden  = ''.join(th)
    text_visible = ''.join(tv)

    html = T.encode(text_visible, text_hidden)
    block.insert(0, html)

    T.build_fonts(working_dir=working_dir)

    # Copy base font
    shutil.copyfile(f_otf, os.path.join(working_dir, f_otf))
    
    # Build the font-face remapping
    f_css = f_html2.replace('.html', '_fontface.css')
    with open(f_css, 'w') as FOUT:
        FOUT.write(T.build_CSS())
        
    # Add the header block
    style_tag = soup.new_tag('link',
                             rel='stylesheet',
                             href=os.path.basename(f_css))
    soup.find('head').insert(0, style_tag)

    with open(f_html2,'w') as FOUT:
        html_text = soup.encode_contents(formatter='html')
        FOUT.write(html_text)

    print "Output written to", f_html2
    


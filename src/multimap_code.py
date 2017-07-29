import collections
import bs4
import joblib
from remap_font import modify_font

class translate_tables(object):

    def __init__(self, f_font, name):
        self.tables = collections.defaultdict(dict)
        self.idx = 0
        self.font_tables = None
        self.name = name
        self.f_font = f_font

    def new_table(self):
        self.idx += 1
        return self.tables[self.idx], self.idx

    def get_match(self, a1, a2):
        for k,tx in self.tables.items():
            if a1 not in tx:
                return tx, k
            if tx[a1] == a2:
                return tx, k
            
        return None, None

    def __call__(self, a1, a2):

        # If there is no mapping return 0
        if a1 == a2:
            return 0

        # Try to get a match
        tx, key = self.get_match(a1, a2)

        # If no match is made create a new table
        if tx is None:
            tx, key = self.new_table()
            
        tx[a1] = a2
        return key

    def encode(self, hidden_text, visible_text):

        soup = bs4.BeautifulSoup('','lxml')
        current_tag = None
        current_idx = 0
    
        for a1,a2 in zip(visible_text, hidden_text):
            key = self(a1,a2)           
            #print a1, a2, key

            if key != current_idx:
                # Create a new tag
                if current_tag is not None:
                    soup.append(current_tag)
                    
                current_tag = soup.new_tag("font{}".format(key))
                current_idx = key

            if current_tag.string is None:
                current_tag.string = ''

            current_tag.string += a1

            #if a1 != ' ':
            #    current_tag.string += a1
            #else:
            #    current_tag.string += u'\xa0'

        soup.append(current_tag)
        return soup

    def _get_fontname(self, key):
        return self.f_font.replace('.otf','_m{}.otf'.format(key))

    def build_fonts(self, THREADS=-1, clean=True):
        # We could build the fonts in parallel...
        ITR = self.tables
        func = joblib.delayed(modify_font)

        with joblib.Parallel(THREADS) as MP:
            MP(func(self.f_font,
                    self._get_fontname(key),
                    self.tables[key],
                    clean) for key in ITR)
        
    def build_CSS(self, ):
        template1 = '''
           @font-face {
           font-family: "%s";
           src:url(%s); \n}
        '''.strip()

        template2 = '''
           font%s {font-family: "%s";}
        '''.strip()

        css = []
        css.append(template1%(self.name, self.f_font))

        for key in self.tables:
            namex = self.name+'_'+str(key)
            css.append(template1%(namex, self._get_fontname(key)))
            css.append(template2%(key, namex))
            
        css = '\n\n'.join(css)
        return css           
        

if __name__ == "__main__":
    #hidden_text  = "The quick brown fox."
    #visible_text = "One lazy pizza day o"
    
    #hidden_text  = "abcabc"
    #visible_text = "xyzxxx"

    hidden_text  = "xyzk"
    visible_text = "abcc"

    f_font = 'fonts/helvetica-bold.otf'
    name = "Helvetica"

    T = translate_tables(f_font, name)
    html = T.encode(hidden_text, visible_text)

    #T.build_fonts()
    css = T.build_CSS()
    print html
    print css



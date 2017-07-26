import collections
import bs4

class translate_tables(object):

    def __init__(self):
        self.tables = collections.defaultdict(dict)
        self.idx = 0

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
            print a1, a2, key

            if key != current_idx:
                # Create a new tag
                if current_tag is not None:
                    soup.append(current_tag)
                    
                current_tag = soup.new_tag("font{}".format(key))
                current_idx = key

            if current_tag.string is None:
                current_tag.string = ''
                
            current_tag.string += a1

        soup.append(current_tag)
        return soup
    


        

if __name__ == "__main__":
    #hidden_text  = "The quick brown fox."
    #visible_text = "One lazy pizza day o"
    
    #hidden_text  = "abcabc"
    #visible_text = "xyzxxx"

    hidden_text  = "1234"
    visible_text = "abcc"

    T = translate_tables()
    print T.encode(hidden_text, visible_text)



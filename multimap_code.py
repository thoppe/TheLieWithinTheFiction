import collections

class translate_tables(object):

    def __init__(self):
        self.tables = collections.defaultdict(dict)
        self.idx = -1

    def new_table(self):
        self.idx += 1
        return self.tables[self.idx]

    def get_match(self, a1, a2):
        for k,tx in self.tables.items():
            if a1 not in tx:
                return tx
            if tx[a1] == a2:
                return tx
        return None

    def __call__(self, a1, a2):
        tx = self.get_match(a1, a2)
        
        if tx is None:
            tx = self.new_table()
            
        tx[a1] = a2
        #print self.tables

        

if __name__ == "__main__":
    hidden_text  = "The quick brown fox."
    visible_text = "One lazy pizza day o"
    
    #hidden_text  = "abcabc"
    #visible_text = "xyzxxx"
    
    T = translate_tables()
    for a1,a2 in zip(visible_text, hidden_text):
        T(a1,a2)
        
    print T.tables

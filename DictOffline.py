# -*- coding: utf-8 -*-

#########################################################################
# Alain M. Lafon, preek.aml@gmail.com (c) 2009                          #
#                                                                       #
# Fetches translations from the beolingus offline database              #
#########################################################################

import string
import sqlite3

class DictOffline(object):
    def __init__(self):
        self.conn = sqlite3.connect('data/data.db')
        self.max_results = 50

    def padHash(self, input):
        """Pads a hash at all words that are no attributes."""
        output = ""
        if input:
            if " " in input:
                words = input.split(" ")
            else:
                words = input
            for word in words:
                if word and len(word) > 1:
                    if word[0] not in ["[", "(", "{"]:
                        output += " #" + word
                    else:
                        output += " " + word
        return output

    def search(self, search_word):
        """Searches the database for a matching line."""
        translations = []
        statement = "select data from dictionary where data like " +\
                "'%%%s%%'" % search_word
        self.conn.text_factory = str
        c = self.conn.cursor()
        c.execute(statement)
        for line in c:
            try:
                translation = line[0].split("::")
                if '|' in translation[0]:
                    de_alternatives = string.split(translation[0], '|')
                    en_alternatives = string.split(translation[1], '|')
                    for j in range(len(de_alternatives)):
                        translations.append([self.padHash(de_alternatives[j]),
                            self.padHash(en_alternatives[j])])
                    # Print a separator line between different alternative
                    # translation groups
                    translations.append(["", ""])
                else: 
                    translations.append([self.padHash(translation[0]),
                    self.padHash(translation[1])])
            except:
                # If the user searches for some crazy word like "etw.", he
                # will retrieve a couple of thousand results. This is a bad
                # workaround.
                return translations[:self.max_results+1]
            
        return translations[:self.max_results+1]

if __name__ == "__main__":
    # Testing
    Dict = DictOffline()
    res = Dict.search("foobar")
    print res

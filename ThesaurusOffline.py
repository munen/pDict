# -*- coding: utf-8 -*-

#########################################################################
# Alain M. Lafon, preek.aml@gmail.com (c) 2009                          #
#                                                                       #
# Reads synonym databases and works the data up.                        #
#########################################################################

import string
import sqlite3

class ThesaurusOffline():
    
    def __init__(self):
        """Initializes the thesaurus databases."""
        self.conn = sqlite3.connect('data/data.db')
        self.c = self.conn.cursor()
    
    def swapFirst(self, line, first):
            """Puts the search word up in front."""
            data = []
            try:
                if line:
                  data.append("#" + first)
                  for entry in line:
                      if entry.lower() != "#" + first.lower():
                        data.append(entry)
            except:
                pass
            finally:
              return data

    def search(self, search_word, language='de', suggestions="off"):
        """Searches for synonyms in thesaurus databases.
           English(en) and German(de) may be used."""
        result = []
        # Backup statements are for words that only exist in the db like 'xx
        # (generic term)'
        if language=='de':
            # TODO: Can't find any words with umlauts
            statement = "select data from thesaurus_de where data like " +\
                    "'%%|%s|%%'" % search_word
            backup_statement = "select data from thesaurus_de where data " +\
                    "like '%%|%s%%|%%'" % search_word
        else:
            statement = "select data from thesaurus_en where data like " +\
                    "'%%|%s|%%'" % search_word
            backup_statement = "select data from thesaurus_en where data " +\
                    "like '%%|%s%%|%%'" % search_word

        self.conn.text_factory = str
        # FIXME: The windows version of SQLIte obviously has threading
        # problems. If there was only one prefetch, dictionary and
        # thesaurus won't work anymore. On the Mac it works like a charm,
        # so it must be the sqlite version.
        self.c.execute(statement)
        for line in self.c:
            try:
                for item in map(string.strip, line[0].split("|")):
                    if suggestions == "on":
                        if not item.startswith(search_word):
                            continue
                    if "#" + item not in result:
                        result.append("#" + item)
                if len(result) > 0:
                    if result[len(result)-1]:
                        result.append("")
            except StandardError, e:
                print "DEBUGFEHLER: ", e
        if not result:
            self.c.execute(backup_statement)
            for line in self.c:
                try:
                    for item in map(string.strip, line[0].split("|")):
                        if suggestions == "on":
                            if not item.startswith(search_word):
                                continue
                        if "#" + item not in result:
                            result.append("#" + item)
                except StandardError, e:
                    print "DEBUGFEHLER: ", e
        # If the user has not used the infinitive or the like
        # TODO: Find more endings and make this code more general
        if not result:
            if search_word[-2:] == "ed":
                search_word = search_word[:-2]
            if search_word[-3:] == "ing":
                search_word = search_word[:-3]
            statement = "select data from thesaurus_en where data like " +\
                    "'%%|%s|%%'" % search_word
            self.c.execute(statement)
            for line in self.c:
                try:
                    for item in map(string.strip, line[0].split("|")):
                        if "#" + item not in result:
                            result.append("#" + item)
                except StandardError, e:
                    print "DEBUGFEHLER: ", e

        # If in prefetch mode and a German search has had no results, then
        # try again in English
        if not result and suggestions == "on":
            result = self.search(search_word, 
                    "en", suggestions="on")

        result = self.swapFirst(result, search_word)
        return result

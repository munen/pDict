# -*- coding: utf-8 -*-

#########################################################################
# Alain M. Lafon, preek.aml@gmail.com (c) 2009                          #
#                                                                       #
# Fetches translations off dict.cc                                      #
#########################################################################

import urllib
import urllib2
import string
from BeautifulSoup import BeautifulSoup

class DictOnline(object):
    def __init__(self):
        # Headerdata
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = { 'User-Agent' : self.user_agent }

    def search(self, search_val):
        """Searches dict.cc for search_val. Returns a list."""
        # Value as given on dict.cc; search relevant
        values = {'s' : search_val }
        # Results
        translation = []
        
        data = urllib.urlencode(values)
        req = urllib2.Request("http://www.dict.cc/", data, self.headers)
        
        # The response from the site somtimes comes in scrambled; therefore the
        # result is fetched until the parser gets it right
        pool = ''
        while pool == '':
            try:
               response = urllib2.urlopen(req)
            except:
                return "offline"

            # the_page contains the result in html
            the_page = response.read()
            
            # Begin parsing the page
            try:
                pool = BeautifulSoup(the_page)
            except:
                None
       
        # TODO: Include headers
        results = pool.findAll('td', attrs={'class' : 'td7nl'})
        headers_pool = pool.findAll('td', attrs={'class' : 'td6'})
        headers = []
        for header in headers_pool:
            headers.append(header)

        # example result:
        #<td class="td7nl"><a href="javascript:ve(866661)" style="background-color:red;color:white;padding:0px 4px;border:2px outset">Unverified!</a> to <a href="/englisch-deutsch/wedge.html">wedge</a> <a href="/englisch-deutsch/%5Bsl.%5D.html"><kbd title="slang">[sl.]</kbd></a> <a href="/englisch-deutsch/%5Bvulg.%5D.html"><kbd title="vulgar">[vulg.]</kbd></a></td>
        
        # The first word will also be from the originating language, the second the
        # translation. Translations will be saved as lists in list translation 
        # [[orig1, trans1], [orig2, trans2], ..]
        t_word = ''
        search_val_language = 'en'
        for result in results:
            word = ''
            attributes = ''
            link_pool = [] 
            # First get all links, so that they may be tagged
            params = ['a', 'b', 'kbd', 'val']
            for param in params:
                for tmp in result.findAll(param):
                    link_pool.append(tmp.string)
            for tmp in result.findAll(text=True):
                # Skip all informational numbers in the translation
                try:
                    string.atoi(tmp)
                    continue
                except:
                    # Don't save markups
                    if tmp != ' ' and tmp[0] != '&':
                        # Tag all links
                        # If link begins with '[', then tag after it
                        #if tmp[0] == '[':
                        #    tmp = '[#' + tmp[1:]
                        if tmp in link_pool:
                            tmp = '#' + tmp
                        word = word + " " +\
                                string.strip(unicode(tmp).encode("utf-8"))
            if t_word == '':
                t_word = word
            else:
                # dict.cc returns english always on the left column
                if unicode(t_word.lower(),
                        errors='ignore').find(unicode(search_val.lower(),
                        errors='ignore')) != -1:
                    search_val_language = 'en'
                if unicode(word.lower(), 
                        errors='ignore').find(unicode(search_val.lower(),
                        errors='ignore')) != -1:
                    search_val_language = 'de'
                translation.append([unicode(t_word, "utf-8"),
                    unicode(word, "utf-8")])
                t_word = ''
       
        # If search_val is German, turn the order around
        if search_val_language == 'de':
            for i in range(len(translation)):
                translation[i][0], translation[i][1] = translation[i][1], \
                translation[i][0]

        return translation

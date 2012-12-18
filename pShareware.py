# -*- coding: utf-8 -*-

#########################################################################
# Alain M. Lafon, preek.aml@gmail.com (c) 2009                          #
#                                                                       #
# Shareware features of pDict. If the copy is not validated and the     #
# trial time is over, the user is presented with a nag screen.          #
#########################################################################

import string
import sqlite3

class pShareware(object):
    def __init__(self):
        self.conn = sqlite3.connect('data/data.db')

    def checkTrial(self):
        """Checks if the copy is validated."""
        # If pDict is started for the first time, a code is generated and
        # inserted into the database. If the user pays, then I will do a
        # rot13 on the code, send it back to him and he will have a registered
        # copy of pDict
        statement = "select code from licence"
        c = self.conn.cursor()
        c.execute(statement)
        code = c.fetchall()
        if code:
            # licenced_to will first be set when the user registeres his code
            # correctly to pDict.
            statement = "select licenced_to from licence"
            c = self.conn.cursor()
            c.execute(statement)
            licenced_to = c.fetchall()
            if licenced_to[0][0]:
                # No trial version
                return "" 
            else:
                return code[0][0]
        else:
            # From time generate user code
            import time
            now = str(time.time())[1:].replace(".", "1")
            code = now[:4] + "-" + now[4:8] + "-" + now[8:12]
            codeInsert = "insert into licence (code) values ('%s');" % code
            c.execute(codeInsert)
            self.conn.commit()
            self.conn.close()
            return code

    def validateSerial(self, serial):
        """Checks the users' serial."""
        statement = "select code from licence"
        c = self.conn.cursor()
        c.execute(statement)
        code = c.fetchall()[0][0]
        code = code.replace("-", "")
        transformed_code = ""
        try:
            for element in code:
                transformed_code += str(int(element)%2)
        except:
            # If the user didn't just enter numbers
            return False

        return transformed_code == serial

    def setValidation(self, code):
        """Validates the copy of pDict"""
        codeInsert = "update licence set licenced_to = '%s' " % code +\
                "where code is not null;" 
        c = self.conn.cursor()
        c.execute(codeInsert)
        self.conn.commit()
        self.conn.close()

    def getLicenceText(self):
        """Returns the current licence text."""
        licence = """
END-USER SHAREWARE LICENSE AGREEMENT 
This is a legal agreement between you, the end user, and dispatched software.
By installing and using pDict, you agree to this Shareware License Agreement.

COPYRIGHT 
The software is protected by copyright laws and international copyright
treaties, as well as other intellectual property laws and treaties. The
software is licensed and not sold. This Agreement grants you the right to
install and use the Software on your computer.

DISCLAIMER OF WARRANTY 
There is no Limited Warranty or product support for unregistered users of the
Software. This software is provided "AS IS", without warranty of any kind.

PRIVACY PROTECTION 
Any personal information disclosed to the author as a result of registration
will be held confidential and will not be disclosed to any third party for
commercial or non-profit purposes. 

DISTRIBUTION
The end user may copy and distribute this program freely, provided that:
    1)   No fee is charged for such copying and distribution, and
    2)   It is distributed only in its original, unmodified state.

USAGE
You can evaluate pDict for an indefinite time.  If you like this program,
however, your contribution will be appreciated. 
You may not use this product in a commercial environment without paying a
license fee.
"""        
        return licence

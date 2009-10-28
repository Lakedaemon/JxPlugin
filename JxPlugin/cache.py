# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
# 1 tab = 4 white spaces

import os
import cPickle

from ankiqt import mw

def load_cache():
    """returns the JxPlugin Cache if it exists and {} if it doesn't"""
    path = os.path.join(mw.config.configPath, "plugins", "JxPlugin", "Cache", mw.deck.name() + ".pickle")                      
    if not os.path.exists(path): 
        return {}
    file = open(path, 'rb')
    cache = cPickle.load(file)
    file.close()
    return cache
        
def save_cache(dict):
    """saves the JxPlugin Cache on disk"""  
    path = os.path.join(mw.config.configPath, "plugins", "JxPlugin", "Cache", mw.deck.name() + ".pickle")   
    file = open(path, 'wb')
    cPickle.dump(dict, file, cPickle.HIGHEST_PROTOCOL)
    file.close()
    


# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://repose.cx/anki/
# ---------------------------------------------------------------------------

from ui_menu import *

if __name__ == "__main__":
    print "Don't run me : I'm a plugin."
else:  
    #r = KanjiGraphLauncher(mw)
    mw.addHook('init', init_JxPlugin)
    print 'Lakedaemon plugin loaded'


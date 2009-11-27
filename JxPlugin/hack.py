# -*- coding: utf-8 -*-
# Copyright: Olivier Binda <olivier.binda@wanadoo.fr>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# ---------------------------------------------------------------------------
# This file is a plugin for the "anki" flashcard application http://ichi2.net/anki/
# ---------------------------------------------------------------------------
"""let's put all Anki hack in there"""
from PyQt4.QtCore import SIGNAL, QUrl
import os

from ankiqt import mw

# directory where QTWebKit will look for resources
JxResourcesUrl = QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__ ),"Resources") + os.sep)

# "hack" to overload mw.help.anchorClicked
def JxAnchorClicked(url):
        # prevent the link being handled
        mw.help.widget.setSource(QUrl(""))
        addr = unicode(url.toString())
        if addr.startswith("hide:"):
            if len(addr) > 5:
                # hide for good
                mw.help.config[addr] = True
            mw.help.hide()
            if "hide" in mw.help.handlers:
                mw.help.handlers["hide"]()
        elif addr.startswith("py:"):
            key = addr[3:]
            if key in mw.help.handlers:
                mw.help.handlers[key]()
	elif addr.startswith("Jx:"):
            key = addr[3:]
            from export import JxExport2Anki, JxExport2csv, JxRemove, JxClear
            eval(key)
        else:
            # open in browser
            QDesktopServices.openUrl(QUrl(url))
        if mw.help.focus:
            mw.help.focus.setFocus()
	    

mw.help.widget.connect(mw.help.widget, SIGNAL("anchorClicked(QUrl)"),
                            JxAnchorClicked)    

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, Cristian García <cristian99garcia@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys
import time
import signal
import subprocess
import thread
import fcntl

from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import Vte
from gi.repository import GLib
from gi.repository import Pango

from sugar3.activity import activity
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import _create_activity_icon as ActivityIcon
from sugar3.activity.activity import get_bundle_path
from sugar3 import profile

from sugar3.presence import presenceservice

DEBUG_TERMINAL = False


class SuperTuxActivity(activity.Activity):

    def __init__(self, handle):
        super(SuperTuxActivity, self).__init__(handle, create_jobject=False)

        self.__source_object_id = None
        self._vte = Vte.Terminal()

        if DEBUG_TERMINAL:
            toolbox = activity.ActivityToolbox(self)
            toolbar = toolbox.get_activity_toolbar()
            self.set_toolbox(toolbox)

            self._vte.set_size(30, 5)
            self._vte.set_size_request(200, 300)
            self._vte.set_font(Pango.FontDescription('Monospace 10'))

            vtebox = gtk.HBox()
            vtebox.pack_start(self._vte)
            vtesb = gtk.VScrollbar(self._vte.get_adjustment())
            vtesb.show()
            vtebox.pack_start(vtesb, False, False, 0)
            self.set_canvas(vtebox)

            toolbox.show()
            self.show_all()
            toolbar.share.hide()
            toolbar.keep.hide()

        # now start subprocess.
        self._vte.connect('child-exited', self.on_child_exit)
        self._vte.grab_focus()
        bundle_path = activity.get_bundle_path()

        try:
            self._pid = self._vte.fork_command_full(
                Vte.PtyFlags.DEFAULT,
                bundle_path,
                ["/bin/sh", "-c", '%s/bin/supertux' % bundle_path],
                ["LD_LIBRARY_PATH=%s/lib" % bundle_path],
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,
                None)

        except AttributeError:
            self._pid = self._vte.spawn_sync(
                Vte.PtyFlags.DEFAULT,
                bundle_path,
                ["/bin/sh", "-c", '%s/bin/supertux' % bundle_path],
                [],
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,
                None)

    def on_child_exit(self, widget):
        if not DEBUG_TERMINAL:
            sys.exit()


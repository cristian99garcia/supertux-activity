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


from sugar.activity import activity

# Set to false to hide terminal and auto quit on exit
DEBUG_TERMINAL = False

class SuperTuxActivity(activity.Activity):

    def __init__(self, handle):
        import gtk, pango, platform, sys
        from ctypes import cdll

        if platform.machine().startswith('arm'):
            pass # FIXME

        else:
            if platform.architecture()[0] == '64bit':
                vte_path = "x86-64"

            else:
                vte_path = "x86"

            vte = cdll.LoadLibrary("lib/%s/libvte.so.9" % vte_path)

        sys.path.append("lib/%s" % vte_path)
        import vte

        super(SuperTuxActivity, self).__init__(handle, create_jobject=False)

        self.__source_object_id = None

        # creates vte widget
        self._vte = vte.Terminal()

        if DEBUG_TERMINAL:
            toolbox = activity.ActivityToolbox(self)
            toolbar = toolbox.get_activity_toolbar()
            self.set_toolbox(toolbox)

            self._vte.set_size(30,5)
            self._vte.set_size_request(200, 300)
            font = 'Monospace 10'
            self._vte.set_font(pango.FontDescription(font))
            self._vte.set_colors(gtk.gdk.color_parse ('#E7E7E7'),
                                 gtk.gdk.color_parse ('#000000'),
                                 [])

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
        self._pid = self._vte.fork_command \
            (command='/bin/sh',
             argv=['/bin/sh','-c', '%s/bin/supertux' % bundle_path],
             envv=["LD_LIBRARY_PATH=%s/lib" % bundle_path],
             directory=bundle_path)

    def on_child_exit(self, widget):
        """This method is invoked when the user's script exits."""
        import sys
        if not DEBUG_TERMINAL:
            sys.exit()


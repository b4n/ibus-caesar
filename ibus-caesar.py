#!/usr/bin/python3
# Dummy IBus engine for typing and converting Caesar code.
# Copyright (C) 2023 Colomban Wendling <lists.ban@herbesfolles.org>
#
# Bits from ibus-braille2, BSD license
# Copyright (C) 2019 Samuel Thibault <samuel.thibault@ens-lyon.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import argparse
import logging

import gi
gi.require_version('IBus', '1.0')

from gi.repository import IBus
from gi.repository import GObject
from gi.repository import Gio

try:
    from Xlib.keysymdef.miscellany import XK_Left
except ImportError:
    gi.require_version('Gdk', '3.0')
    from gi.repository.Gdk import KEY_Left as XK_Left


DEBUG_LEVEL = 0


def debug(level, *args):
    if level <= DEBUG_LEVEL:
        logging.debug(*args)


class CaesarEngine(IBus.Engine):
    __gtype_name__ = 'CaesarEngine'

    shift = 3

    def __init__(self):
        debug(3, "Initializing %s...", self.__class__)
        super().__init__()

    def do_enable(self):
        # notify we'll be using surrounding text
        self.get_surrounding_text()

        self.shift = 3  # default to Caesar's most known shift
        try:
            self.shift = int(self.get_name().split(':', 1)[1])
        except IndexError:
            pass
        except ValueError as ex:
            logging.warning('Invalid shift: %s', ex)

    def _encodable(self, c):
        return len(c) == 1 and ord('a') <= ord(c.lower()) <= ord('z')

    def _encode(self, c, shift):
        if self._encodable(c):
            base = ord('a' if c.islower() else 'A')
            return chr(base + (ord(c) - base + shift) % 26)
        return c

    def do_process_key_event(self, keysym, scancode, state):
        # modifiers for key release
        modifiers = (IBus.ModifierType.CONTROL_MASK
                     | IBus.ModifierType.MOD1_MASK
                     | IBus.ModifierType.SHIFT_MASK
                     | IBus.ModifierType.SUPER_MASK
                     | IBus.ModifierType.RELEASE_MASK)

        if (state & modifiers & ~IBus.ModifierType.SHIFT_MASK) == 0:
            c = chr(keysym)
            if self._encodable(c):
                debug(1, "encrypting character: %s", c)
                self.commit_text(IBus.Text.new_from_string(self._encode(c, self.shift)))
                return True
        elif (chr(keysym).lower() == 'e' and
              (state & modifiers & ~IBus.ModifierType.SHIFT_MASK) == IBus.ModifierType.CONTROL_MASK):
            text, cursor, anchor = self.get_surrounding_text()
            debug(2, "surrounding text is '%s'", text.get_text())
            debug(2, "cursor is at %s", cursor)
            debug(2, "anchor is at %s", anchor)

            s = text.get_text()
            if cursor > anchor:
                s = s[anchor:cursor]
            elif anchor > cursor:
                s = s[cursor:anchor]

            debug(1, "encrypting text '%s'", s)
            shift = -self.shift if state & IBus.ModifierType.SHIFT_MASK else self.shift
            es = ''.join(self._encode(c, shift) for c in s)
            debug(1, "encrypted text is '%s'", es)

            if cursor == anchor:
                debug(2, "deleting %s characters at %s", text.get_length(), -cursor)
                self.delete_surrounding_text(-cursor, text.get_length())
            self.commit_text(IBus.Text.new_from_string(es))

            # hack to move the cursor back where it was
            for i in range(len(s) - cursor):
                self.forward_key_event(XK_Left, 105, 0)
            return True

        # don't eat
        return False


def relative_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


class CaesarEngineApp(Gio.Application):
    def __init__(self, exec_by_ibus=False, set_engine=False):
        super().__init__()

        self.__component = IBus.Component.new_from_file(relative_path("caesar.xml"))
        self.__bus = IBus.Bus()
        self.__bus.connect("disconnected", lambda bus: self.release())
        self.__factory = IBus.Factory.new(self.__bus.get_connection())

        engines_from_xml = [desc.get_name() for desc in self.__component.get_engines()]
        # add the existing engines
        for name in engines_from_xml:
            self.__factory.add_engine(name, GObject.type_from_name("CaesarEngine"))

        # add engines for the (1..25) shifts (we don't need the 26th as it
        # loops around), but only if they don't exist already.  This is
        # somewhat a hack, and the engines should be described in the XML.
        for shift in range(1, 26):
            name = "caesar:%d" % shift
            if name in engines_from_xml:
                continue

            engine = IBus.EngineDesc.new(name, "Caesar %d" % shift,
                                         "Caesar code, shift=%+d" % shift, "",
                                         self.__component.get_license(),
                                         self.__component.get_author(),
                                         "system-lock-screen-symbolic", "")
            self.__component.add_engine(engine)
            self.__factory.add_engine(name, GObject.type_from_name("CaesarEngine"))

        if exec_by_ibus:
            self.__bus.request_name(self.__component.get_name(), 0)
        else:
            self.__bus.register_component(self.__component)
        if set_engine:
            self.__bus.set_global_engine_async("caesar", -1, None, None, None)

    def do_activate(self):
        self.hold()


def main():
    global DEBUG_LEVEL

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ibus', help='executed by IBus.',
                        action='store_true')
    parser.add_argument('-s', '--set-engine', help='Set global engine at startup.',
                        action='store_true')
    parser.add_argument('-D', '--debug', help='enable debugging (repeat '
                                              'option for more verbosity).',
                        action='count', default=0)

    args = parser.parse_args()

    DEBUG_LEVEL = args.debug
    if DEBUG_LEVEL > 0:
        logging.basicConfig(level=logging.DEBUG)

    IBus.init()
    app = CaesarEngineApp(args.ibus, args.set_engine)
    app.run()


if __name__ == '__main__':
    main()

ibus-caesar
===========

**ibus-caesar** is a useless IBus input method.  It allows writing
[Caesar cipher](https://en.wikipedia.org/wiki/Caesar_cipher) straight out of
your keyboard, as well as ciphering or deciphering such codes on the fly.

Installation
------------

No installation is actually required for a recreational use.  Just run
`ibus-caesar.py -s` and start typing.  See `ibus-caesar.py --help` for more
options and details.

It is however possible to install the input method system-wide.  To do so,
run:

```shell
$ make PREFIX=/usr
# make install PREFIX=/usr
```

You can change `PREFIX` to your liking (defaults to */usr/local*), but there
are two things to note:

1. Set `PREFIX` on *both* `make` and `make install` calls.
2. The IBus component will be installed in `$PREFIX/share/ibus/component/`,
   which might or might not be somewhere IBus looks at.

Also, remember to run `make clean` if you already ran `make` with another
prefix.


Enabling the input method
-------------------------

If run manually, you can use the `-s` switch to set IBus' *global-engine* to
`caesar`.

Regardless of the way *ibus-caesar* has been started, you can use
`ibus engine caesar` to switch to that engine.

The `caesar` engine uses a shift to the right of 3.  You can specify a
different shift using `caesar:2`, `caesar:25` or alike.  Possible shift values
are from 1 to 25.


Usage
-----

Just type normally, and the basic ASCII letters will be ciphered according to
the shift.

To cipher or decipher existing lines of text, move the cursor to such a line
and type *Ctrl+e* for ciphering and *Ctrl+Shift+e* for deciphering.

**Warning**: This shifts input.  It's damn annoying.  And it won't stop until
you switch to another input method or stop the *ibus-caesar* engine.


License
-------

GPLv3+

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

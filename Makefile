#!/usr/bin/make -f

VERSION = 0.1
PACKAGE = ibus-caesar

INSTALL_EXEC ?= install -m 0755 -D
INSTALL_DATA ?= install -m 0644 -D
MKDIR_P ?= install -m 0755 -d
LN_S ?= ln -s
RM ?= rm -f

PREFIX ?= /usr/local
EXEC_PREFIX ?= $(PREFIX)/libexec
DATA_PREFIX ?= $(PREFIX)/share
PKGDATADIR = $(DATA_PREFIX)/$(PACKAGE)
PKGLIBDIR = $(PREFIX)/lib/$(PACKAGE)

all: caesar.xml

caesar.xml: caesar.xml.in Makefile
	sed -e 's%@VERSION@%$(VERSION)%g' \
	    -e 's%@EXEC_PREFIX@%$(EXEC_PREFIX)%g' < $< > $@

install: install-data install-exec

install-exec: ibus-caesar.py Makefile
	$(INSTALL_EXEC) ibus-caesar.py $(DESTDIR)$(PKGLIBDIR)/
	$(MKDIR_P) $(DESTDIR)$(EXEC_PREFIX)/
	$(LN_S) $(PKGLIBDIR)/ibus-caesar.py $(DESTDIR)$(EXEC_PREFIX)/ibus-caesar

install-data: caesar.xml Makefile
	$(INSTALL_DATA) caesar.xml $(DESTDIR)$(PKGLIBDIR)/caesar.xml
	$(MKDIR_P) $(DESTDIR)$(DATA_PREFIX)/ibus/component/
	$(LN_S) $(PKGLIBDIR)/caesar.xml $(DESTDIR)$(DATA_PREFIX)/ibus/component/

clean:
	$(RM) caesar.xml

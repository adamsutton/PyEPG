#
# PyEPG primary makefile
#

#
# Directories
#

DIST_DIR      := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
ROOT_DIR      := $(abspath $(DIST_DIR)/..)
DEB_DIR       := $(DIST_DIR)/debian
SRC_DIR       := $(ROOT_DIR)/src
BUILD_DIR     := $(ROOT_DIR)/build

#
# Binaries (and commands)
#

ECHO          := @echo
RM            := @rm -f
PYTHON        := python
PY_SETUP      := $(PYTHON) $(DIST_DIR)/setup.py
DEB_MAKE      := $(MAKE) -f $(DEB_DIR)/rules

#
# Project description
#

PROJECT       ?= $(shell $(PY_SETUP) --name)
VERSION       ?= $(shell $(PY_SETUP) --version)
PKGNAME       := $(PROJECT)-$(VERSION)

#
# Rules
#

default: all

# Build from scratch
all: clean deb

# Cleanup
cleanall: clean
	$(RM) $(ROOT_DIR)/*.deb $(ROOT_DIR)/*.changes
clean:
	$(RM) -r $(BUILD_DIR)

# Build
build:	
	$(PY_SETUP) $@

# Build deb
deb:
	mkdir -p $(BUILD_DIR)
	for d in data lib scripts; do \
	test -L $(BUILD_DIR)/$$d || ln -s $(ROOT_DIR)/$$d $(BUILD_DIR)/$$d; \
	done
	cp -a $(ROOT_DIR)/dist/*  $(BUILD_DIR)
	cd $(BUILD_DIR); dpkg-buildpackage -rfakeroot -us -uc -b

# Check setup
check:
	$(ECHO) "PROJECT      := $(PROJECT)"
	$(ECHO) "VERSION      := $(VERSION)"
	$(ECHO) ""
	$(ECHO) "ROOT_DIR     := $(ROOT_DIR)"
	$(ECHO) "DIST_DIR     := $(DIST_DIR)"
	$(ECHO)	"DEB_DIR      := $(DEB_DIR)"
	$(ECHO) ""
	$(ECHO) "PY_SETUP     := $(PY_SETUP)"
	$(ECHO) "DEB_MAKE     := $(DEB_MAKE)"

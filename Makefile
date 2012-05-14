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
clean:
	$(PY_SETUP) $@
	fakeroot $(DEB_DIR)/rules $@

# Build
build:	
	$(PY_SETUP) $@

# Build deb
deb:
	cd $(DIST_DIR); dpkg-buildpackage -rfakeroot -us -uc

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

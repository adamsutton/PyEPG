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
	$(DEB_MAKE) $@

# Build
build:	
	$(PY_SETUP) $@

# Build deb
deb:
	$(PY_SETUP) sdist --dist-dir=$(BUILD_DIR) --prune
	mv $(BUILD_DIR)/$(PKGNAME).tar.gz $(BUILD_DIR)/$(PKGNAME).orig.tar.gz
	test -e $(BUILD_DIR)/debian || ln -s $(DEB_DIR) $(BUILD_DIR)/debian
	cd $(BUILD_DIR); dpkg-buildpackage -rfakeroot
# -R$(DEB_DIR)/rules
#--admindir=$(DEB_DIR)

#builddeb:
# build the source package in the parent directory
# then rename it to project_version.orig.tar.gz
#$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=../ --prune
#rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
# build the package
#dpkg-buildpackage -i -I -rfakeroot

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

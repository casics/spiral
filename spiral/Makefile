##
## @file    Makefile
## @brief   Top-level Makefile for CASICS
## @author  mhucka@caltech.edu
##
## <!---------------------------------------------------------------------------
## Copyright (C) 2015 by the California Institute of Technology.
## This software is part of CASICS, the Comprehensive and Automated Software
## Inventory Creation System.  For more information, visit http://casics.org.
## ------------------------------------------------------------------------- -->

# I used to create tags in each source directory separately, but that turns
# out to be very inconvenient when using tags.  The approach here is designed
# to create only one tags file, in the current directory, by recursively
# looking in subdirectories for source files to use as input.  Tell Emacs to
# use that TAGS file by using M-x visit-tags-table.

tags etags: etags-version-check TAGS

etags-command ?= etags $(ETAGSFLAGS)

files-to-tag := $(shell find . -path ./extractor/tests -prune -o -name '*.py' -o -name '*.java')

TAGS: $(files-to-tag)
	$(etags-command) $(files-to-tag)

etags-version-check: 
	@if test -z "`etags --version 2>&1 | grep 'Free Software'`"; then \
	  echo "Your 'etags' command is not the GNU version, and I'm"; \
	  echo "afraid I don't know how to work with it. Quitting."; \
	  exit 2; \
	fi

# Makefile for source rpm: xorg-x11-xdm
# $Id$
NAME := xorg-x11-xdm
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common

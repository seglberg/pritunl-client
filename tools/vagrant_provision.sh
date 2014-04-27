#!/usr/bin/env bash
apt-get update -qq 1> /dev/null

# Build requirements
apt-get install -qq -y devscripts debhelper python-all python-setuptools python-gtk2 python-appindicator 1> /dev/null

#!/usr/bin/env python
from sugar.activity import bundlebuilder
from ConfigParser import ConfigParser
parser = ConfigParser()
parser.read("activity/activity.info")
name = parser.get('Activity', 'name')
bundlebuilder.start(name)

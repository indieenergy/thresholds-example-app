#!/usr/bin/env python
# encoding: utf-8
"""
admin.py

Created by Michael Yagley on 2011-04-26.
Copyright (c) 2011 Indie Energy Systems Company, LLC.. All rights reserved.
"""

from django.contrib import admin

from threshold.models import Geopod

admin.site.register(Geopod)

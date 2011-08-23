#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Copyright (c) 2011 Indie Energy Systems Company, LLC.. All rights reserved.
"""

from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('threshold.views',
    url(r'auth/$', 'auth', name='threshold_auth'),
    url(r'data/$', 'data', name='threshold_data'),
    url(r'$', 'home', name='threshold_home'),
)

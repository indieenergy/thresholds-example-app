#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Copyright (c) 2011 Indie Energy Systems Company, LLC.. All rights reserved.
"""

import base64
import calendar
import datetime
import geopod
import hashlib
import hmac
import time

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson

from threshold.models import Geopod

from dateutil import parser

def home(request):
    instrument_panel = {}
    data_str = request.GET.get('data', '')
    
    signature = base64.urlsafe_b64decode(request.GET.get('sig', '').encode("ascii"))
    signature_check = hmac.new(settings.GEOPOD_CONSUMER_SECRET.encode("ascii"), msg=data_str.encode("ascii"), digestmod=hashlib.sha256).digest()
    
    if signature != signature_check:
        return HttpResponseForbidden()
    
    if data_str:
        data = simplejson.loads(base64.urlsafe_b64decode(data_str.encode("ascii")))
        subdomain = data.get('subdomain', '')
        if subdomain:
            gp = get_object_or_404(Geopod, subdomain=subdomain)
            gc = geopod.GeopodClient(gp.subdomain, gp.access_token, gp.access_token_secret, settings.GEOPOD_CONSUMER_KEY, settings.GEOPOD_CONSUMER_SECRET, "testgeopod.com")
            points = gc.request('/point/', params={'markers[]': 'his'})
    
    now = datetime.datetime.now()
    start = request.GET.get('start', str(datetime.date(year=now.year, month=now.month, day=now.day)))
    end = request.GET.get('end', str(datetime.date(year=now.year, month=now.month, day=now.day)))
    
    context = {
        'geopod': gp,
        'points': [{'id': '149eecb3-4cb9224d'}],
        'start': start,
        'end': end,
    }
    return render_to_response('threshold.html', context, context_instance=RequestContext(request))
    
def data(request):
    now = datetime.datetime.now()
    point_ids = request.GET.getlist('points[]')
    start = request.GET.get('start', str(datetime.date(year=now.year, month=now.month, day=now.day)))
    end = request.GET.get('end', str(datetime.date(year=now.year, month=now.month, day=now.day)))
    
    start_date = parser.parse(start)
    end_date = parser.parse(end)
    
    subdomain = request.GET.get('subdomain', '')
    if not subdomain:
        return HttpResponseBadRequest()
    
    gp = get_object_or_404(Geopod, subdomain=subdomain)
    gc = geopod.GeopodClient(gp.subdomain, gp.access_token, gp.access_token_secret, settings.GEOPOD_CONSUMER_KEY, settings.GEOPOD_CONSUMER_SECRET, "testgeopod.com")
    
    data_series = []
    for point_id in point_ids:
        point = gc.request('/history/%s/%s/%s/' % (point_id, start, end))
        if 'error' not in point:
            data_series.append({
                'name': point.get('name', ''),
                'unit': point.get('unit', ''),
                'data': point.get('data', []),
                'point_id': point_id,
            })
        
    graph_data = {
        'start_date': start,
        'end_date': end,
        'utc_offset':  (time.mktime(start_date.timetuple()) - calendar.timegm(start_date.timetuple()))*1000,
        'series': data_series,
    }
    return HttpResponse(simplejson.dumps(graph_data), mimetype="text/javascript")
    
    
@csrf_exempt
def auth(request):
    response = None
    
    if request.method == 'POST':
        subdomain = request.POST.get('subdomain', '')
        if subdomain:
            gp, created = Geopod.objects.get_or_create(subdomain=request.POST.get('subdomain'))
            gp.name = request.POST.get('name', '')
            gp.access_token = request.POST.get('access_token', '')
            gp.access_token_secret = request.POST.get('access_token_secret', '')
            gp.save()
            response = HttpResponse()
        else:
            response = HttpResponseBadRequest()
    else:
        response =HttpResponseNotAllowed(['POST',])
    
    return response
    
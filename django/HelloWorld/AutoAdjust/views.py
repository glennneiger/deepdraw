# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
import requests
import json
from django.shortcuts import render

# Create your views here.

class ShowView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/show.html").read())
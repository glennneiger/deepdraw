from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
import requests
import json
from string import digits
from data.models import Tripletmark


# Create your views here.

class Test_Base(APIView):
    def get(self, request):
        print('ok');
        return HttpResponse('成功')


class testdb(APIView):
    def get(self, request):
        test1 = Tripletmark(uuid1='1', uuid2='2', bbox1='3', bbox2='4', mark='5', fix='6')
        test1.save()
        return HttpResponse('成功')


class getAll(APIView):
    def get(self, request):
        test = Tripletmark.objects.all()
        print(test)
        for i in test:
            print(i.uuid1)
        return HttpResponse('success')


class LoginView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("../templates/login.html").read())

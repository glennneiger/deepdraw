from django.http import HttpResponse


def hello(request):
    # console.log("ok");
    return HttpResponse("Hello world ! ")



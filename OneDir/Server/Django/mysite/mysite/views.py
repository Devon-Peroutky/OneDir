from django.http import HttpResponse

def hello(request):
    return HttpResponse("Hello world! <br><br> Add '/admin' to the end of the url to go to a WHOLE NEW PAGE!")

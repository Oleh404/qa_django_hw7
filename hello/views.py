from django.http import HttpResponse

def hello(request, name="World"):
    return HttpResponse(f"<h1>Hello, {name}</h1>")

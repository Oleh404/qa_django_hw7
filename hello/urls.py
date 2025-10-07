from django.urls import path
from .views import hello

urlpatterns = [
    path("", hello, name="hello_default"),
    path("<str:name>/", hello, name="hello_named"),
]

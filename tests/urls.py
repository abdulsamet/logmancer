"""
URL configuration for logmancer tests.
"""

from django.urls import path
from django.http import JsonResponse, HttpResponse


def dummy_view(request):
    return HttpResponse('{"msg": "ok"}')


def test_view(request):
    return JsonResponse({"test": "success"})


def error_view(request):
    raise ValueError("Test exception")


def auth_required_view(request):
    if request.user.is_authenticated:
        return JsonResponse({"user": request.user.username})
    return JsonResponse({"error": "Not authenticated"}, status=401)


def json_post_view(request):
    if request.method == "POST":
        return JsonResponse({"received": "json data"})
    return JsonResponse({"method": request.method})


test_urlpatterns = [
    path("dummy/", dummy_view, name="dummy"),
    path("test/", test_view, name="test"),
    path("error/", error_view, name="error"),
    path("auth/", auth_required_view, name="auth"),
    path("json/", json_post_view, name="json"),
]

from django.urls import path
from flexselect.views import field_changed

urlpatterns = [
    path('field_changed', field_changed),
]

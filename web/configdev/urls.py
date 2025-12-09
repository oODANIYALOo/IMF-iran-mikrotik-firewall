from django.urls import path
from configdev import views
urlpatterns = [
path('',views.Index.as_view()),
]
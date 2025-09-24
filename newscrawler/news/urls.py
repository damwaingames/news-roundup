from django.urls import path
from . import views

app_name = "news"

urlpatterns = [
    path("", views.index, name="index"),
    path("summarize_articles/", views.summarize_articles, name="summarize_articles"),
]

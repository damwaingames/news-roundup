from django.shortcuts import render

from django.utils import timezone
from datetime import timedelta

from .models import NewsArticle


def index(request):
    news_articles = NewsArticle.objects.order_by("-crawl_date").filter(
        article_date__gte=timezone.now() - timedelta(days=7)
    )

    return render(
        request,
        "news/index.html",
        context={
            "news_articles": news_articles,
        },
    )

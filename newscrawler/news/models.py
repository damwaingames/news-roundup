from django.db import models


class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(unique=True)
    full_text = models.TextField()
    summary = models.TextField()
    crawl_date = models.DateTimeField(auto_now_add=True)
    article_date = models.DateTimeField()

    def __str__(self):
        return self.title

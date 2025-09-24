from django.contrib import admin
from .models import NewsArticle


class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "link", "crawl_date", "article_date")
    search_fields = ("title", "link")
    list_filter = ("crawl_date", "article_date")
    date_hierarchy = "crawl_date"
    ordering = ("-crawl_date",)
    list_per_page = 25
    list_max_show_all = 100
    list_editable = ("article_date",)


admin.site.register(NewsArticle, NewsArticleAdmin)

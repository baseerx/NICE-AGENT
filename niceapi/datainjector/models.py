# news_verification/models.py
from utils.fields import MSSQLSequentialUUIDField
from django.db import models
# use built-in User for verifiers/admins
from django.contrib.auth.models import User
import uuid

class OverallAnalysis(models.Model):
    summary = models.TextField()
    overall_sentiment = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'overall_analysis'
        verbose_name_plural = "Overall Analyses"

    def __str__(self):
        return f"{self.overall_sentiment} - {self.created_at.date()}"


class NewsArticle(models.Model):
    headline = models.TextField()
    publication_date = models.DateField()
    author = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255)
    url = models.URLField(max_length=1000, unique=True)
    image_url = models.URLField(max_length=1000, null=True, blank=True)
    article_unique_id = models.CharField(max_length=64, null=True, blank=True)  # SHA256 hex digest
    sentiment = models.CharField(max_length=50)
    summary = models.TextField()
    local_or_international = models.CharField(max_length=50)
    overall_analysis = models.ForeignKey(
        OverallAnalysis, null=True, blank=True, on_delete=models.SET_NULL, related_name='articles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'news_articles'

    def __str__(self):
        return self.headline[:80]


class ArticleTag(models.Model):
    article = models.ForeignKey(
        NewsArticle, on_delete=models.CASCADE, related_name='auto_tags')
    tag_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'article_tags'

    def __str__(self):
        return self.tag_name



class Verification(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]

    article = models.OneToOneField(
        NewsArticle, on_delete=models.CASCADE, related_name='verification')
    verified_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='verifications')
    verification_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Pending')
    manual_sentiment = models.CharField(max_length=50, null=True, blank=True)
    manual_tags = models.JSONField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    verified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'verification'

    def __str__(self):
        return f"{self.article.headline[:50]} - {self.verification_status}"




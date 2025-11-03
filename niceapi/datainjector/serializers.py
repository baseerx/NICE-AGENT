from rest_framework import serializers
from .models import NewsArticle, OverallAnalysis, ArticleTag, Verification

class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = '__all__'


class OverallAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = OverallAnalysis
        fields = '__all__'


class ArticleTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleTag
        fields = '__all__'


class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = '__all__'

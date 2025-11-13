from rest_framework.decorators import api_view
from rest_framework.response import Response
from sqlalchemy import text
from utils.db import SessionLocal  # adjust import if needed
from datainjector.models import NewsArticle, Verification, ArticleTag
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

@api_view(['GET'])
def get_article(request):
    session = SessionLocal()
    query = text("""
        SELECT 
            a.id AS article_id,
            a.headline,
            a.publication_date,
            a.author,
            a.source,
            a.url,
            a.image_url,
            a.article_unique_id,
            a.sentiment,
            a.summary AS article_summary,
            a.local_or_international,
            a.created_at AS article_created_at,
            a.updated_at AS article_updated_at,
            a.overall_analysis_id,

            oa.id AS overall_analysis_id,
            oa.summary AS overall_summary,
            oa.overall_sentiment,
            oa.created_at AS analysis_created_at,

            v.id AS verification_id,
            v.verification_status,
            v.manual_sentiment,
            v.manual_tags,
            v.remarks,
            v.verified_at,
            v.verified_by_id,

            t.id AS tag_id,
            t.tag_name,
                 t.individual_sentiment
        FROM [NICE].[dbo].[news_articles] a
        LEFT JOIN [NICE].[dbo].[overall_analysis] oa 
            ON a.overall_analysis_id = oa.id
        LEFT JOIN [NICE].[dbo].[verification] v 
            ON v.article_id = a.id
        LEFT JOIN [NICE].[dbo].[article_tags] t 
            ON t.article_id = a.id
        WHERE v.verification_status != 'Verified' or v.verification_status IS NULL
    """)

    rows = session.execute(query).fetchall()
    session.close()

    # Convert to dicts
    rows = [dict(row._mapping) for row in rows]

    # Group by article_id
    articles_dict = {}

    for row in rows:
        article_id = row["article_id"]
        if article_id not in articles_dict:
            # Initialize article record
            articles_dict[article_id] = {
                "article_id": row["article_id"],
                "headline": row["headline"],
                "publication_date": row["publication_date"],
                "author": row["author"],
                "source": row["source"],
                "url": row["url"],
                "image_url": row["image_url"],
                "article_unique_id": row["article_unique_id"],
                "sentiment": row["sentiment"],
                "article_summary": row["article_summary"],
                "local_or_international": row["local_or_international"],
                "article_created_at": row["article_created_at"],
                "article_updated_at": row["article_updated_at"],
                "overall_analysis": {
                    "overall_analysis_id": row["overall_analysis_id"],
                    "overall_summary": row["overall_summary"],
                    "overall_sentiment": row["overall_sentiment"],
                    "analysis_created_at": row["analysis_created_at"],
                },
                "verification": {
                    "verification_id": row["verification_id"],
                    "verification_status": row["verification_status"],
                    "manual_sentiment": row["manual_sentiment"],
                    "manual_tags": row["manual_tags"],
                    "remarks": row["remarks"],
                    "verified_at": row["verified_at"],
                    "verified_by_id": row["verified_by_id"],
                },
                "tags": []
            }

        # Append tags (avoid duplicates)
        if row["tag_name"] and row["tag_name"] not in [t["tag_name"] for t in articles_dict[article_id]["tags"]]:
            articles_dict[article_id]["tags"].append({
                "tag_id": row["tag_id"],
                "tag_name": row["tag_name"],
                "sentiment": row["individual_sentiment"]
            })

    # Convert grouped data to list
    result = list(articles_dict.values())

    return Response(result)


@api_view(['GET'])
def verified_articles(request):
    session = SessionLocal()
    query = text("""
        SELECT 
            a.id AS article_id,
            a.headline,
            a.publication_date,
            a.author,
            a.source,
            a.url,
            a.image_url,
            a.article_unique_id,
            a.sentiment,
            a.summary AS article_summary,
            a.local_or_international,
            a.created_at AS article_created_at,
            a.updated_at AS article_updated_at,
            a.overall_analysis_id,

            oa.id AS overall_analysis_id,
            oa.summary AS overall_summary,
            oa.overall_sentiment,
            oa.created_at AS analysis_created_at,

            v.id AS verification_id,
            v.verification_status,
            v.manual_sentiment,
            v.manual_tags,
            v.remarks,
            v.verified_at,
            v.verified_by_id,

            t.id AS tag_id,
            t.tag_name,
                 t.individual_sentiment
        FROM [NICE].[dbo].[news_articles] a
        LEFT JOIN [NICE].[dbo].[overall_analysis] oa 
            ON a.overall_analysis_id = oa.id
        LEFT JOIN [NICE].[dbo].[verification] v 
            ON v.article_id = a.id
        LEFT JOIN [NICE].[dbo].[article_tags] t 
            ON t.article_id = a.id
        WHERE v.verification_status = 'Verified'
    """)

    rows = session.execute(query).fetchall()
    session.close()

    # Convert to dicts
    rows = [dict(row._mapping) for row in rows]

    # Group by article_id
    articles_dict = {}

    for row in rows:
        article_id = row["article_id"]
        if article_id not in articles_dict:
            # Initialize article record
            articles_dict[article_id] = {
                "article_id": row["article_id"],
                "headline": row["headline"],
                "publication_date": row["publication_date"],
                "author": row["author"],
                "source": row["source"],
                "url": row["url"],
                "image_url": row["image_url"],
                "article_unique_id": row["article_unique_id"],
                "sentiment": row["sentiment"],
                "article_summary": row["article_summary"],
                "local_or_international": row["local_or_international"],
                "article_created_at": row["article_created_at"],
                "article_updated_at": row["article_updated_at"],
                "overall_analysis": {
                    "overall_analysis_id": row["overall_analysis_id"],
                    "overall_summary": row["overall_summary"],
                    "overall_sentiment": row["overall_sentiment"],
                    "analysis_created_at": row["analysis_created_at"],
                },
                "verification": {
                    "verification_id": row["verification_id"],
                    "verification_status": row["verification_status"],
                    "manual_sentiment": row["manual_sentiment"],
                    "manual_tags": row["manual_tags"],
                    "remarks": row["remarks"],
                    "verified_at": row["verified_at"],
                    "verified_by_id": row["verified_by_id"],
                },
                "tags": []
            }

        # Append tags (avoid duplicates)
        if row["tag_name"] and row["tag_name"] not in [t["tag_name"] for t in articles_dict[article_id]["tags"]]:
            articles_dict[article_id]["tags"].append({
                "tag_id": row["tag_id"],
                "tag_name": row["tag_name"],
                "sentiment": row["individual_sentiment"]
            })

    # Convert grouped data to list
    result = list(articles_dict.values())

    return Response(result)


@api_view(['PUT'])
def update_sentiment(request, articleid):
    try:
        article = NewsArticle.objects.get(id=articleid)
    except NewsArticle.DoesNotExist:
        return Response({"message": "Article not found"}, status=404)

    new_sentiment = request.data.get("sentiment")
    if not new_sentiment or new_sentiment.capitalize() not in ["Positive", "Negative", "Neutral"]:
        return Response({"message": "Invalid sentiment value"}, status=400)

    article.sentiment = new_sentiment.capitalize()
    article.save(update_fields=["sentiment"])

    return Response({
        "message": "Sentiment updated successfully",
        "article_id": article.pk,
        "sentiment": article.sentiment
    }, status=200)


@api_view(['PUT'])
def verify_article(request, articleid):
    try:
        article = NewsArticle.objects.get(id=articleid)
    except NewsArticle.DoesNotExist:
        return Response({"message": "Article not found"}, status=404)

    verification_data = request.data

    # Pass verified_by as default if creating
    verification, created = Verification.objects.get_or_create(
        article=article,
        defaults={
            'verified_by': request.user,
            'verification_status': verification_data.get("verification_status", "Pending"),
            'verified_at': timezone.now()
        }
    )

    if not created:
        # If it already exists, update fields
        verification.verification_status = verification_data.get(
            "verification_status", verification.verification_status)
        verification.verified_by = request.user
        verification.verified_at = timezone.now()
        verification.save()

    return Response({
        "message": "Article verified successfully",
        "article_id": article.pk,
        "verification_status": verification.verification_status
    }, status=200)


@api_view(['PUT'])
def add_tag(request, articleid):
    try:
        article = NewsArticle.objects.get(id=articleid)
    except NewsArticle.DoesNotExist:
        return Response({"message": "Article not found"}, status=404)

    tag_name = request.data.get("tag_name")
    if not tag_name:
        return Response({"message": "Tag name is required"}, status=400)

    # Create and associate the tag
    new_tag = ArticleTag.objects.create(article=article, tag_name=tag_name)

    return Response({
        "message": "Tag added successfully",
        "article_id": article.pk,
        "tag": {
            "tag_id": new_tag.pk,
            "tag_name": new_tag.tag_name
        }
    }, status=201)

@api_view(['POST'])
def set_tag_sentiment(request):
    article_id = request.data.get("article_id")
    tag_name = request.data.get("tag")
    sentiment = request.data.get("sentiment")

    if not all([article_id, tag_name, sentiment]):
        return Response({"message": "article_id, tag, and sentiment are required"}, status=400)

    try:
        article = NewsArticle.objects.get(id=article_id)
    except NewsArticle.DoesNotExist:
        return Response({"message": "Article not found"}, status=404)

    try:
        tag = ArticleTag.objects.get(article=article, tag_name=tag_name)
    except ArticleTag.DoesNotExist:
        return Response({"message": "Tag not found for this article"}, status=404)

    tag.individual_sentiment = sentiment
    tag.save(update_fields=["individual_sentiment"])

    return Response({
        "message": "Tag sentiment updated successfully",
        "article_id": article.pk,
        "tag": {
            "tag_id": tag.pk,
            "tag_name": tag.tag_name,
            "sentiment": tag.individual_sentiment
        }
    }, status=200)

@api_view(['DELETE'])
def delete_article(request, articleid):
    try:
        article = NewsArticle.objects.get(id=articleid)
    except NewsArticle.DoesNotExist:
        return Response({"message": "Article not found"}, status=404)

    # snapshot related info before deletion
    tags_count = ArticleTag.objects.filter(article=article).count()
    verification_exists = Verification.objects.filter(article=article).exists()
    overall = article.overall_analysis

    try:
        article.delete()
        Verification.objects.filter(article=article).delete()
        ArticleTag.objects.filter(article=article).delete()
    except Exception as e:
        return Response({"message": "Failed to delete article", "error": str(e)}, status=500)

    overall_deleted = False
    if overall:
        # delete overall_analysis if no other articles reference it
        if not overall.articles.exists():
            try:
                overall.delete()
                overall_deleted = True
            except Exception:
                overall_deleted = False

    return Response({
        "message": "Article deleted successfully",
        "article_id": articleid,
        "tags_deleted": tags_count,
        "verification_deleted": verification_exists,
        "overall_analysis_deleted": overall_deleted
    }, status=200)

@api_view(['DELETE'])
def remove_tag(request, articleid):
    try:
        article = NewsArticle.objects.get(id=articleid)
    except NewsArticle.DoesNotExist:
        return Response({"message": "Article not found"}, status=404)

    tag_name = request.data.get("tag_name")
    if not tag_name:
        return Response({"message": "Tag name is required"}, status=400)

    try:
        tag = ArticleTag.objects.get(article=article, tag_name=tag_name)
        tag.delete()
    except ArticleTag.DoesNotExist:
        return Response({"message": "Tag not found for this article"}, status=404)

    return Response({
        "message": "Tag removed successfully",
        "article_id": article.pk,
        "tag_name": tag_name
    }, status=200)
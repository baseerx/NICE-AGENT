from collections import defaultdict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sqlalchemy import text
from utils.db import SessionLocal  # adjust import if needed


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
            t.tag_name
        FROM [NICE].[dbo].[news_articles] a
        LEFT JOIN [NICE].[dbo].[overall_analysis] oa 
            ON a.overall_analysis_id = oa.id
        LEFT JOIN [NICE].[dbo].[verification] v 
            ON v.article_id = a.id
        LEFT JOIN [NICE].[dbo].[article_tags] t 
            ON t.article_id = a.id;
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
                "tag_name": row["tag_name"]
            })

    # Convert grouped data to list
    result = list(articles_dict.values())

    return Response(result)

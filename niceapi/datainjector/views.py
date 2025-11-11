from django.shortcuts import render
from django.views import View
from .models import NewsArticle, OverallAnalysis, ArticleTag, Verification
from rest_framework.response import Response
from rest_framework.decorators import api_view
from dotenv import load_dotenv
import os
import secrets
import requests
import string
import json
import re
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.contrib.auth.models import User

# Create your views here.
load_dotenv()

# helper to create a secure random string


@staticmethod
def random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def parse_agent_result(result):
    """
    Handles nested response structures like:
    [ { "content": { "parts": [ { "text": "```json {...} ```" } ] } } ]
    Returns parsed JSON dict if successful.
    """
    try:
        # If the result is a list, drill down into the text
        if isinstance(result, list) and len(result) > 0:
            text_block = (
                result[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
        elif isinstance(result, dict):
            # Handle direct dict response (already parsed)
            return result
        else:
            print("⚠️ Unexpected response type from agent:", type(result))
            return None

        # Clean Markdown code block formatting
        text_block = re.sub(r"```json|```", "", text_block).strip()

        # Parse into JSON
        parsed = json.loads(text_block)
        return parsed if isinstance(parsed, dict) else None

    except Exception as e:
        print(f"⚠️ Failed to parse agent result: {e}")
        return None


def fetch_store_data(data):
    """
    Fetches data from external agent and stores it across:
    - OverallAnalysis
    - NewsArticle
    - ArticleTag
    - Verification
    """

    agent_url = os.getenv("AGENT_URL")
    if not agent_url:
        print("❌ AGENT_URL not set in environment variables.")
        return None

    try:
        print(
            f"Fetching news for user={data['user_id']}, session={data['session_id']}")

        response = requests.post(
            agent_url,
            json={
                "appName": "app",
                "userId": data["user_id"],
                "sessionId": data["session_id"],
                "newMessage": {
                    "role": "user",
                    "parts": [{"text": "latest news regarding power sector of Pakistan?"}],
                },
            },
            timeout=200,
        )

        response.raise_for_status()
        result = response.json()

        print("📨 Received response from agent.")
        print("🧾 Raw agent response type:", type(result))

        # Parse nested or wrapped JSON
        parsed_result = parse_agent_result(result)

        if not parsed_result or "items" not in parsed_result:
            print("⚠️ Invalid response format — 'items' missing or parse failed.")
            return None

        # Step 1️⃣: Create an OverallAnalysis record
        overall_analysis = OverallAnalysis.objects.create(
            summary=parsed_result.get("summary", "No summary provided."),
            overall_sentiment=parsed_result.get("overall_sentiment", "Neutral"),
            created_at=timezone.now()  # Automatically set current timestamp
        )

        stored_count = 0

        # Step 2️⃣: Store each news article
        for item in parsed_result.get("items", []):
            try:
                with transaction.atomic():
                    article, created = NewsArticle.objects.get_or_create(
                        url=item.get("url"),
                        defaults={
                            "headline": item.get("headline", "No headline"),
                            "publication_date": item.get("publication_date") or timezone.now().date(),
                            "author": item.get("author", "unknown"),
                            "source": item.get("source", ""),
                            "image_url": item.get("image", ""),
                            "article_unique_id": item.get("id"),
                            "sentiment": item.get("sentiment", "Neutral"),
                            "summary": item.get("summary", ""),
                            "local_or_international": item.get("local_or_international", "Unknown"),
                            "overall_analysis": overall_analysis,
                        },
                    )

                    if created:
                        stored_count += 1

                        # Step 3️⃣: Add tags
                        tags = item.get("tags", [])
                        for tag_name in tags:
                            ArticleTag.objects.create(
                                article=article, tag_name=tag_name)

                        # Optional: Create placeholder Verification record
                        # verifier = User.objects.first()
                        # if verifier:
                        #     Verification.objects.create(
                        #         article=article,
                        #         verified_by=verifier.username,
                        #         verification_status="Pending",
                        #     )

            except IntegrityError:
                continue

        print(
            f"✅ Stored {stored_count} new articles linked to OverallAnalysis overall_analysis.id")
        return {"stored_articles": stored_count}

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data from agent: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        return None


@api_view(['GET'])
def set_session(request):
    # handle possible module-level @staticmethod on random_string
    rand_fn = getattr(random_string, "__func__", random_string)

    username = 'u_' + rand_fn(12)
    session_id = 's_' + rand_fn(12)
    session_url = f'http://127.0.0.1:8000/apps/app/users/{username}/sessions/{session_id}'
    agent_url = os.getenv("AGENT_SESSION_URL")
    session_api_url = f'{agent_url}users/{username}/sessions/{session_id}'

    try:
        response = requests.post(session_api_url)
        data = {
            "message": "Data stored successfully",
            "agent_url": agent_url,
            "user_id": username,
            "session_id": session_id,
            "session_url": session_url,
            "session_api_url": session_api_url,
            "response_status": getattr(response, "status_code", None),
        }
    except requests.exceptions.RequestException as e:
        return Response({"message": "Failed to connect to the agent URL", "error": str(e)}, status=500)

    result = fetch_store_data(data)
    print("📦 Result from fetch_store_data:", result)
    if result is None:
        return Response({"message": "Failed to fetch/store data from agent"}, status=500)

    return Response(result, status=200)



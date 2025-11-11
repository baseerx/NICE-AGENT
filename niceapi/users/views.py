from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework import status
import json
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import uuid
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
# Create your views here.


@api_view(['POST'])
def register(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )
        user.save()

        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(["POST"])
def login_view(request):
    data = request.data
    username = data.get("username")
    password = data.get("password")
   
    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({"error": "Invalid username or password"}, status=400)

    login(request, user)  # creates session

    # ✅ use JsonResponse instead of DRF Response for session cookie binding
    response = JsonResponse({
        "message": "Login successful",
        "user": {"username": user.username, "email": user.email},
    })
   
    return response


@csrf_exempt
@api_view(["GET"])
def session_check(request):
    if request.user.is_authenticated:
        return Response({
            "authenticated": True,
            "user": {
                "username": request.user.username,
                "email": request.user.email
            }
        })
    else:
        return Response({"authenticated": False})


@csrf_exempt
@api_view(["GET"])
def user_logout(request):
    try:
        # log out user and clear session data
        logout(request)

        # prepare response
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

        # delete all cookies present in the request (plus common ones)
        cookies = set(request.COOKIES.keys())
        cookies.update([getattr(settings, "SESSION_COOKIE_NAME", "sessionid"), "csrftoken"])

        for cookie in cookies:
            # delete_cookie signature varies by Django version; handle both cases
            try:
                response.delete_cookie(cookie, path="/", samesite="None")
            except TypeError:
                response.delete_cookie(cookie, path="/")

        return response
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

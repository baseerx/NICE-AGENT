from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework import status
import json
from rest_framework.decorators import api_view
import uuid
from django.core.cache import cache
from django.http import JsonResponse
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


@api_view(["POST"])
def login_view(request):
    """
    Authenticates the user and creates a session using Django's session framework.
    """
    try:
        data = request.data
        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, user)  # creates the session & sets sessionid cookie

        response = Response(
            {
                "message": "Login successful",
                "user": {"username": user.username, "email": user.email},
            },
            status=status.HTTP_200_OK,
        )
    # Optionally, store extra info in a cookie
        response.set_cookie("username", user.username,
                            httponly=True, samesite='Lax')
        response.set_cookie("email", user.email, httponly=True, samesite='Lax')

        return response
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


@api_view(["POST"])
def logout_view(request):
    logout(request)
    return Response({"message": "Logged out successfully"})

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.shortcuts import render

from .services_auth import register_user, authenticate_user, update_password

# 测试视图
from django.shortcuts import render

def test_page(request):
    return render(request, "test.html")

# 注册
@csrf_exempt
def register(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not password:
        return JsonResponse({"error": "missing fields"}, status=400)

    user = register_user(username, email, password)

    return JsonResponse({
        "status": "success",
        "user_id": user.id
    })


# 登录
@csrf_exempt
def login_view(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)

    username = data.get("username")
    password = data.get("password")

    user = authenticate_user(username, password)

    if user is None:
        return JsonResponse({"error": "invalid credentials"}, status=401)

    login(request, user)

    return JsonResponse({
        "status": "success",
        "username": user.username
    })


# 登出
@csrf_exempt
def logout_view(request):

    logout(request)

    return JsonResponse({
        "status": "logged out"
    })


# 当前用户（权限验证）
def current_user(request):

    if not request.user.is_authenticated:
        return JsonResponse({"user": None})

    return JsonResponse({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email
    })


# 修改密码
@csrf_exempt
def change_password(request):

    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"}, status=401)

    data = json.loads(request.body)

    new_password = data.get("password")

    if not new_password:
        return JsonResponse({"error": "password required"}, status=400)

    update_password(request.user, new_password)

    return JsonResponse({
        "status": "password updated"
    })


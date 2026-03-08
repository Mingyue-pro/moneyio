import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError

from .services_categories import (
    build_category_tree_for_user,
    create_category_for_user,
    get_category_for_user,
    update_category_for_user,
    delete_category_for_user,
)


def _require_login(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"}, status=401)
    return None


@csrf_exempt
def categories_collection(request):
    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    if request.method == "GET":
        results = build_category_tree_for_user(request.user)
        return JsonResponse({"results": results})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            category = create_category_for_user(request.user, data)
            return JsonResponse({
                "status": "success",
                "category_id": category.id
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "invalid JSON"}, status=400)
        except ValidationError as e:
            return JsonResponse({"error": e.message}, status=400)

    return JsonResponse({"error": "method not allowed"}, status=405)


@csrf_exempt
def categories_item(request, category_id):
    auth_error = _require_login(request)
    if auth_error:
        return auth_error

    if request.method == "GET":
        category = get_category_for_user(request.user, category_id)
        if not category:
            return JsonResponse({"error": "not found"}, status=404)

        return JsonResponse({
            "id": category.id,
            "name": category.name,
            "category_type": category.category_type,
            "icon_id": category.icon_id,
            "tree_level": category.tree_level,
            "parent_id": category.parent.id if category.parent else None,
        })

    if request.method in ("PUT", "PATCH"):
        try:
            data = json.loads(request.body)
            category = update_category_for_user(request.user, category_id, data)

            if not category:
                return JsonResponse({"error": "not found"}, status=404)

            return JsonResponse({"status": "success"})
        except json.JSONDecodeError:
            return JsonResponse({"error": "invalid JSON"}, status=400)
        except ValidationError as e:
            return JsonResponse({"error": e.message}, status=400)

    if request.method == "DELETE":
        ok = delete_category_for_user(request.user, category_id)

        if not ok:
            return JsonResponse({"error": "not found"}, status=404)

        return JsonResponse({"status": "deleted"})

    return JsonResponse({"error": "method not allowed"}, status=405)
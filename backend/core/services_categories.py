from django.core.exceptions import ValidationError
from .models import Category


def list_categories_for_user(user):
    return (
        Category.objects
        .filter(user=user)
        .select_related("parent")
        .order_by("category_type", "tree_level", "name")
    )


def build_category_tree_for_user(user):
    categories = list_categories_for_user(user)

    parents = []
    children_map = {}

    for category in categories:
        if category.parent_id is None:
            parents.append(category)
            children_map[category.id] = []

    for category in categories:
        if category.parent_id is not None:
            children_map.setdefault(category.parent_id, []).append(category)

    results = []
    for parent in parents:
        results.append({
            "id": parent.id,
            "name": parent.name,
            "category_type": parent.category_type,
            "tree_level": parent.tree_level,
            "children": [
                {
                    "id": child.id,
                    "name": child.name,
                    "category_type": child.category_type,
                    "tree_level": child.tree_level,
                    "parent_id": child.parent_id,
                }
                for child in children_map.get(parent.id, [])
            ]
        })

    return results


def create_category_for_user(user, payload):
    name = payload.get("name")
    category_type = payload.get("category_type")
    parent_id = payload.get("parent_id")
    icon_id = payload.get("icon_id")

    if not name or not category_type:
        raise ValidationError("name and category_type are required")

    parent = None
    tree_level = 1

    if parent_id:
        parent = Category.objects.filter(id=parent_id, user=user).first()
        if not parent:
            raise ValidationError("invalid parent_id")

        if parent.tree_level >= 2:
            raise ValidationError("only two levels of categories are allowed")

        if parent.category_type != category_type:
            raise ValidationError("child category must have the same category_type as parent")

        tree_level = 2

    category = Category.objects.create(
        user=user,
        parent=parent,
        name=name,
        category_type=category_type,
        icon_id=icon_id,
        tree_level=tree_level
    )

    return category


def get_category_for_user(user, category_id):
    return (
        Category.objects
        .filter(id=category_id, user=user)
        .select_related("parent")
        .first()
    )


def update_category_for_user(user, category_id, payload):
    category = get_category_for_user(user, category_id)
    if not category:
        return None

    if "name" in payload:
        if not payload["name"]:
            raise ValidationError("name cannot be empty")
        category.name = payload["name"]

    if "icon_id" in payload:
        category.icon_id = payload.get("icon_id")

    if "parent_id" in payload:
        parent_id = payload.get("parent_id")

        if parent_id in ("", None):
            category.parent = None
            category.tree_level = 1
        else:
            parent = Category.objects.filter(id=parent_id, user=user).first()
            if not parent:
                raise ValidationError("invalid parent_id")

            if parent.id == category.id:
                raise ValidationError("category cannot be its own parent")

            if parent.tree_level >= 2:
                raise ValidationError("only two levels of categories are allowed")

            if parent.category_type != category.category_type:
                raise ValidationError("child category must have the same category_type as parent")

            category.parent = parent
            category.tree_level = 2

    category.save()
    return category


def delete_category_for_user(user, category_id):
    category = get_category_for_user(user, category_id)
    if not category:
        return False

    # 删除当前分类时，顺带删除它的二级分类
    Category.objects.filter(parent=category, user=user).delete()

    category.delete()
    return True
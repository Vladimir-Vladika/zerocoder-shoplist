def can_manage(user):
    return user.is_authenticated and user.is_active and (user.is_superuser or user.groups.filter(name="Менеджеры").exists())

def access(request):
    return {"can_manage_products": can_manage(request.user)}

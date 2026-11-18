from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from .context_processors import can_manage
from .forms import ProductForm, RegisterForm
from .models import Product

def manager_required(view):
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not can_manage(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapped

def product_list(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.all()
    if query:
        matching_ids = [pk for pk, name in products.values_list("pk", "name") if query.casefold() in name.casefold()]
        products = products.filter(pk__in=matching_ids)
    page = Paginator(products, 12).get_page(request.GET.get("page"))
    return render(request, "catalog/product_list.html", {"page": page, "query": query})

def product_detail(request, pk):
    return render(request, "catalog/product_detail.html", {"product": get_object_or_404(Product, pk=pk)})

def register(request):
    if request.user.is_authenticated:
        return redirect("product_list")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("product_list")
    return render(request, "registration/register.html", {"form": form})

@manager_required
def dashboard(request):
    return render(request, "catalog/dashboard.html", {"products": Product.objects.all()})

@manager_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Товар добавлен.")
        return redirect("dashboard")
    return render(request, "catalog/product_form.html", {"form": form, "title": "Добавить товар"})

@manager_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Изменения сохранены.")
        return redirect("dashboard")
    return render(request, "catalog/product_form.html", {"form": form, "title": "Редактировать товар"})

@manager_required
@require_http_methods(["GET", "POST"])
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Товар удалён.")
        return redirect("dashboard")
    return render(request, "catalog/product_confirm_delete.html", {"product": product})

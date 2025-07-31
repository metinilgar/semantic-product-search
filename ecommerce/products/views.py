from django.shortcuts import render
from .models import Category, Product

# Create your views here.

def home(request):
    """Anasayfa view'ı"""
    categories = Category.objects.all()
    latest_products = Product.objects.all()[:8]  # Son 8 ürün
    context = {
        'categories': categories,
        'latest_products': latest_products,
    }
    return render(request, 'products/home.html', context)

def product_list(request):
    """Tüm ürünleri listeleyen view"""
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id)
        selected_category = Category.objects.get(id=category_id)
    else:
        products = Product.objects.all()
        selected_category = None
    
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
    }
    return render(request, 'products/product_list.html', context)

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from .models import Category, Product
from .search_service import search_and_get_products
import logging

logger = logging.getLogger(__name__)

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


def search_view(request):
    """Arama sayfası view'ı"""
    query = request.GET.get('q', '').strip()
    
    context = {
        'query': query,
        'results': [],
        'search_performed': False,
        'categories': Category.objects.all(),
    }
    
    if query:
        try:
            logger.info(f"Arama yapılıyor: '{query}'")
            
            # Arama servisini çağır
            search_result = search_and_get_products(query)
            
            context.update({
                'search_performed': True,
                'results': search_result.get('products', []),
                'total_found': search_result.get('total_found', 0),
                'api_response': search_result,
                'error': search_result.get('error', False),
                'message': search_result.get('message', ''),
                'expanded_query': search_result.get('expanded_query', ''),
                'detected_gender': search_result.get('gender', ''),
                'product_types': search_result.get('product_types', []),
            })
            
            if search_result.get('error'):
                messages.error(request, search_result.get('message', 'Arama sırasında hata oluştu'))
            elif context['total_found'] == 0:
                messages.info(request, 'Arama kriterlerinize uygun ürün bulunamadı')
            else:
                messages.success(request, f"{context['total_found']} ürün bulundu")
                
        except Exception as e:
            logger.error(f"Arama view hatası: {str(e)}")
            messages.error(request, 'Arama sırasında beklenmeyen bir hata oluştu')
            context['error'] = True
    
    return render(request, 'products/search.html', context)


def search_api(request):
    """AJAX arama API'si (opsiyonel)"""
    if request.method == 'POST':
        query = request.POST.get('q', '').strip()
        
        if not query:
            return JsonResponse({
                'error': True,
                'message': 'Arama sorgusu boş olamaz'
            })
        
        try:
            search_result = search_and_get_products(query)
            
            # Ürün verilerini serialize et
            products_data = []
            for product in search_result.get('products', []):
                products_data.append({
                    'id': str(product.id),
                    'name': product.name,
                    'price': float(product.price),
                    'category': product.category.name,
                    'image_url': f"http://127.0.0.1:8001{product.image.url}" if product.image else "",
                    'score': getattr(product, 'search_score', 0)
                })
            
            return JsonResponse({
                'success': True,
                'query': query,
                'total_found': len(products_data),
                'products': products_data,
                'api_response': search_result
            })
            
        except Exception as e:
            logger.error(f"AJAX arama hatası: {str(e)}")
            return JsonResponse({
                'error': True,
                'message': 'Arama sırasında hata oluştu'
            })
    
    return JsonResponse({'error': True, 'message': 'Sadece POST istekleri kabul edilir'})

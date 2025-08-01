from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('id',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock_quantity', 'gender', 'created_at')
    list_filter = ('category', 'gender', 'created_at')
    search_fields = ('name', 'material_type')
    list_editable = ('price', 'stock_quantity')
    readonly_fields = ('id',)

from django.contrib import admin
from .models import CustomUser, Area, Region

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'ticket', 'role', 'area', 'region']
    search_fields = ['username', 'ticket', 'iin']
    list_filter = ['role', 'area']

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'area']
    search_fields = ['name']
    list_filter = ['area']

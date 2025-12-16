from django.contrib import admin
from .models import *


# CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'tarkibiy_tuzilma', 'bekat_nomi', 'is_staff','passport_seriya','birth_date', 'email',)
    fieldsets = (
        (None, {'fields': ('username', 'password', 'role', 'tarkibiy_tuzilma', 'bekat_nomi')}),
        ('Permissions', {'fields': ('is_staff','is_superuser','is_active')}),
    )

# TarkibiyTuzilma

@admin.register(TarkibiyTuzilma)
class TarkibiyTuzilmaAdmin(admin.ModelAdmin):
    list_display = ('tuzilma_nomi', 'rahbari','status', 'is_pending', 'updated_by','created_by', 'created_at')
    list_filter = ('status', 'is_pending')
    search_fields = ('tuzilma_nomi', 'rahbari')




@admin.register(Bekat)
class BekatAdmin(admin.ModelAdmin):
    list_display = ('bekat_nomi', 'rahbari', 'status', 'is_pending', 'updated_by','created_by', 'created_at')
    list_filter = ('status', 'is_pending')
    search_fields = ('bekat_nomi', 'rahbari')


# ArizaYuborish

class ArizaYuborishImageInline(admin.TabularInline):
    model = ArizaYuborishImage
    extra = 1


# class KelganArizalarImageInline(admin.TabularInline):
#     model = KelganArizalarImage
#     extra = 1




@admin.register(ArizaYuborish)
class ArizaYuborishAdmin(admin.ModelAdmin):
    list_display = ('tuzilma', 'kim_tomonidan', 'status', 'created_by', 'is_approved', 'bildirgi')
    readonly_fields = ('created_by', 'sana')
    
    
    inlines = [ArizaYuborishImageInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# KelganArizalar

@admin.register(KelganArizalar)
class KelganArizalarAdmin(admin.ModelAdmin):
    list_display = ('ariza', 'status', 'created_by', 'is_approved')
    list_filter = ('status', 'is_approved')
    readonly_fields = ('created_by', 'sana')

    # inlines = [KelganArizalarImageInline]
    
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# PPRTuri

@admin.register(PPRTuri)
class PPRTuriAdmin(admin.ModelAdmin):
    list_display = ('nomi','davriyligi', 'qisqachanomi', 'kimlar_qiladi', 'comment')
    search_fields = ('nomi','davriyligi','qisqachanomi', 'kimlar_qiladi', 'comment')


# ObyektNomi

@admin.register(ObyektNomi)
class ObyektNomiAdmin(admin.ModelAdmin):
    list_display = ('obyekt_nomi',)
    search_fields = ('obyekt_nomi',)


# PPRJadval

@admin.register(PPRJadval)
class PPRJadvalAdmin(admin.ModelAdmin):
    list_display = ('oy', 'obyekt', 'ppr_turi', 'kim_tomonidan',)
    list_filter = ('oy',)
    search_fields = ('obyekt__obyekt_nomi', 'ppr_turi__nomi', 'kim_tomonidan',)


# Hujjatlar

@admin.register(Hujjatlar)
class HujjatlarAdmin(admin.ModelAdmin):
    list_display = ('xizmat_hujjatlari',)
    search_fields = ('xizmat_hujjatlari',)


@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ('ppr_qilish_oylik',)
    search_fields = ('ppr_qilish_oylik',)

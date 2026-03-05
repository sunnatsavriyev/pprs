from django.contrib import admin
from .models import *
from django.utils.html import format_html

# CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'tarkibiy_tuzilma', 'bekat_nomi', 'is_staff','passport_seriya','birth_date', 'email',)
    fieldsets = (
        (None, {'fields': ('username', 'password', 'role', 'tarkibiy_tuzilma', 'bekat_nomi')}),
        ('Permissions', {'fields': ('is_staff','is_superuser','is_active')}),
    )


@admin.register(BolimCategory)
class BolimCategoryAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'tuzilma', 'created_by', 'created_at')
    search_fields = ('nomi', 'tuzilma__tuzilma_nomi')



@admin.register(Bolim)
class BolimAdmin(admin.ModelAdmin):
    list_display = ('bolim_category', 'tuzilma', 'rahbari', 'status', 'created_at')
    list_filter = ('status', 'tuzilma')
    search_fields = ('bolim_category__nomi', 'rahbari')

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
    list_display = ('id', 'get_tuzilmalar', 'turi', 'status', 'sana', 'created_by', 'ijro_muddati', 'is_approved', 'qayta_yuklandi', 'muddati_otgan')
    
    def get_tuzilmalar(self, obj):
        return ", ".join([t.tuzilma_nomi for t in obj.tuzilmalar.all()])
    
    get_tuzilmalar.short_description = 'Tuzilmalar' 


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
    list_display = ('nomi','davriyligi', 'vaqti', 'qisqachanomi', 'kimlar_qiladi', 'comment',)
    search_fields = ('nomi','davriyligi','vaqti', 'qisqachanomi', 'kimlar_qiladi', 'comment',)



# ObyektNomi

@admin.register(ObyektNomi)
class ObyektNomiAdmin(admin.ModelAdmin):
    list_display = ('obyekt_nomi','toliq_nomi',)
    search_fields = ('obyekt_nomi','toliq_nomi',)



@admin.register(ObyektLocation)
class ObyektLocationAdmin(admin.ModelAdmin):    
    list_display = ('obyekt', 'lat', 'lng', 'created_at')

# PPRJadval









@admin.register(PPRJadval)
class PPRJadvalAdmin(admin.ModelAdmin):
    # 'obyektlar' o'rniga 'get_obyektlar' funksiyasini qo'shamiz
    list_display = ('get_obyektlar', 'ppr_turi', 'sana', 'status', 'tasdiqlangan', 'bolim_category')
    search_fields = ('obyektlar__obyekt_nomi', 'ppr_turi__nomi') # obyekt__ emas obyektlar__ bo'ldi
    list_filter = ('status', 'tasdiqlangan', 'bolim_category')

    def get_obyektlar(self, obj):
        # Obyektlar nomlarini vergul bilan birlashtirib qaytaradi
        return ", ".join([o.obyekt_nomi for o in obj.obyektlar.all()])
    
    get_obyektlar.short_description = 'Obyektlar' # Ustun nomi



@admin.register(PPRYuborish)
class PPRYuborishAdmin(admin.ModelAdmin):
    list_display = ('id', 'bolim_category', 'yil', 'oy', 'user', 'created_at')
    list_filter = ('yil', 'oy', 'bolim_category')

@admin.register(PPRTasdiqlash)
class PPRTasdiqlashAdmin(admin.ModelAdmin):
    list_display = ('id', 'yuborish_paketi', 'status', 'user', 'created_at')
    list_filter = ('status',)
    
    




class PPRBajarildiImageInline(admin.TabularInline):
    model = PPRBajarildiImage
    extra = 1


@admin.register(PPRBajarildi)
class PPRBajarildiAdmin(admin.ModelAdmin):
    inlines = [PPRBajarildiImageInline]
    list_display = ('jadval', 'user')







@admin.register(PPRYakunlash)
class PPRYakunlashAdmin(admin.ModelAdmin):
    list_display = ('yakunlash',)

# Hujjatlar

@admin.register(Hujjatlar)
class HujjatlarAdmin(admin.ModelAdmin):
    list_display = ('xizmat_hujjatlari',)
    search_fields = ('xizmat_hujjatlari',)




@admin.register(HujjatShabloni)
class HujjatShabloniAdmin(admin.ModelAdmin):
    list_display = ('tuzilma', 'yuklovchi', 'created_at')
    list_filter = ('tuzilma', 'nomi')
    search_fields = ('tuzilma__tuzilma_nomi', 'nomi')
    
    # Admin orqali qo'shganda ham yuklovchini avtomatik belgilash (ixtiyoriy)
    def save_model(self, request, obj, form, change):
        if not obj.yuklovchi:
            obj.yuklovchi = request.user
        super().save_model(request, obj, form, change)
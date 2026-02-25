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



@admin.register(PPRYillikJadval)
class PPRYillikJadvalAdmin(admin.ModelAdmin):
    # Obyekt ManyToMany bo'lgani uchun list_display'da to'g'ridan-to'g'ri ko'rsatib bo'lmaydi
    # Buning uchun maxsus funksiya yozamiz
    list_display = ('yil', 'get_obyektlar', 'get_oylar', 'ppr_turi', 'bolim_category', 'tasdiqlangan', 'status')
    list_filter = ('yil', 'status', 'tasdiqlangan', 'bolim_category', 'tarkibiy_tuzilma')
    search_fields = ('comment', 'ppr_turi__nomi', 'obyekt__obyekt_nomi')
    filter_horizontal = ('obyekt',) # Admin panelda obyektlarni qulay tanlash uchun (box ko'rinishi)

    def get_obyektlar(self, obj):
        # Obyektlar ro'yxatini vergul bilan chiqarish
        return ", ".join([o.obyekt_nomi for o in obj.obyekt.all()])
    get_obyektlar.short_description = "Obyektlar"

    def get_oylar(self, obj):
        # JSONField ichidagi oylarni vergul bilan chiqarish
        if isinstance(obj.oylar, list):
            return ", ".join(obj.oylar)
        return obj.oylar
    get_oylar.short_description = "Rejalashtirilgan oylar"


@admin.register(PPRYillikYuborish)
class PPRYillikYuborishAdmin(admin.ModelAdmin):
    list_display = ('yil', 'bolim_category', 'tarkibiy_tuzilma', 'user', 'created_at', 'get_status')
    list_filter = ('yil', 'bolim_category', 'tarkibiy_tuzilma')
    readonly_fields = ('created_at',)

    def get_status(self, obj):
        # Paket holatini (tasdiqlangan yoki rad etilganligini) ko'rish
        if hasattr(obj, 'qaror'):
            color = 'green' if obj.qaror.status == 'tasdiqlandi' else 'red'
            return format_html('<b style="color: {};">{}</b>', color, obj.qaror.get_status_display())
        return "Kutilmoqda"
    get_status.short_description = "Qaror holati"


@admin.register(PPRYillikTasdiqlash)
class PPRYillikTasdiqlashAdmin(admin.ModelAdmin):
    list_display = ('yuborish_paketi', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('comment', 'user__username')
    readonly_fields = ('created_at',)

    # Tasdiqlashda qaysi paket ekanligini chiroyli ko'rsatish
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('yuborish_paketi', 'user')


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
    
    

class PPRYillikBajarildiImageInline(admin.TabularInline):
    model = PPRYillikBajarildiImage
    extra = 1


@admin.register(PPRYillikBajarildi)
class PPRYillikBajarildiAdmin(admin.ModelAdmin):
    list_display = ('jadval', 'oy', 'user', 'created_at')
    list_filter = ('oy', 'jadval')
    search_fields = ('jadval__name', 'user__username')
    ordering = ('-created_at',)
    inlines = [PPRYillikBajarildiImageInline]







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
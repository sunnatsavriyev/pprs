from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("monitoring", "Monitoring"),
        ("tarkibiy", "Tarkibiy Tuzilma Rahbari"),
        ("bekat", "Bekat Rahbari"),
        ("bolim", "Bo'lim Boshlig'i"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    tarkibiy_tuzilma = models.ForeignKey(
        'TarkibiyTuzilma',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='users'
    )
    bekat_nomi = models.ForeignKey(
        'Bekat',
        on_delete=models.SET_NULL,
        blank=True, 
        null=True,
        related_name='users'
    )
    bolim = models.ForeignKey(
        'Bolim',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='users'
    )
    monitoring = models.ForeignKey(
        'Monitoring',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='users'
    )
    photo = models.ImageField(upload_to='admin_photos/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    passport_seriya = models.CharField(max_length=9, blank=True, null=True)
    # email aslida AbstractUser da mavjud, lekin agar null=True kerak bo'lsa:
    email = models.EmailField(blank=True, null=True)
    # related_name qo‘shish
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
    

    def is_admin(self):
        return self.role == "admin"

    def is_tarkibiy(self):
        return self.role == "tarkibiy"

    def is_bekat(self):
        return self.role == "bekat"
    
    def is_bolim(self):
        return self.role == "bolim"
    
    
    def is_monitoring(self):
        return self.role == "monitoring"




class Bekat(models.Model):
    BEKAT_CHOICES = (
    ("Beruniy", "Beruniy"),
    ("Tinchlik", "Tinchlik"),
    ("Chorsu", "Chorsu"),
    ("Gʻafur Gʻulom", "Gʻafur Gʻulom"),
    ("Alisher Navoiy", "Alisher Navoiy"),
    ("Abdulla Qodiriy", "Abdulla Qodiriy"),
    ("Pushkin", "Pushkin"),
    ("Buyuk Ipak Yoʻli", "Buyuk Ipak Yoʻli"),
    ("Novza", "Novza"),
    ("Milliy bogʻ", "Milliy bogʻ"),
    ("Xalqlar doʻstligi", "Xalqlar doʻstligi"),
    ("Chilonzor", "Chilonzor"),
    ("Mirzo Ulugʻbek", "Mirzo Ulugʻbek"),
    ("Olmazor", "Olmazor"),
    ("Doʻstlik", "Doʻstlik"),
    ("Mashinasozlar", "Mashinasozlar"),
    ("Toshkent", "Toshkent"),
    ("Oybek", "Oybek"),
    ("Kosmonavtlar", "Kosmonavtlar"),
    ("Oʻzbekiston", "Oʻzbekiston"),
    ("Hamid Olimjon", "Hamid Olimjon"),
    ("Mingoʻrik", "Mingoʻrik"),
    ("Yunus Rajabiy", "Yunus Rajabiy"),
    ("Shahriston", "Shahriston"),
    ("Bodomzor", "Bodomzor"),
    ("Minor", "Minor"),
    ("Turkiston", "Turkiston"),
    ("Yunusobod", "Yunusobod"),
    ("Tuzel", "Tuzel"),
    ("Yashnobod", "Yashnobod"),
    ("Texnopark", "Texnopark"),
    ("Sergeli", "Sergeli"),
    ("Choshtepa", "Choshtepa"),
    ("Turon", "Turon"),
    ("Chinor", "Chinor"),
    ("Yangiobod", "Yangiobod"),
    ("Rohat", "Rohat"),
    ("Oʻzgarish", "Oʻzgarish"),
    ("Yangihayot", "Yangihayot"),
    ("Qoʻyliq", "Qoʻyliq"),
    ("Matonat", "Matonat"),
    ("Qiyot", "Qiyot"),
    ("Tolariq", "Tolariq"),
    ("Xonobod", "Xonobod"),
    ("Quruvchilar", "Quruvchilar"),
    ("Olmos", "Olmos"),
    ("Paxtakor", "Paxtakor"),
    ("Qipchoq", "Qipchoq"),
    ("Amir Temur xiyoboni", "Amir Temur xiyoboni"),
    ("Mustaqillik maydoni", "Mustaqillik maydoni"),
)

    bekat_nomi = models.CharField(max_length=255, choices=BEKAT_CHOICES)
    faoliyati = models.TextField()
    rahbari = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    passport_seriya = models.CharField(max_length=9, blank=True, null=True)
    # email aslida AbstractUser da mavjud, lekin agar null=True kerak bo'lsa:
    email = models.EmailField(blank=True, null=True)
    status = models.BooleanField()
    is_pending = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bekat_created'
    )
    updated_by = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,  
        null=True,
        blank=True,
        related_name='bekat_pending_updates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.bekat_nomi


class Monitoring(models.Model):
    faoliyati = models.TextField()
    rahbari = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='monitoring_photos/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    passport_seriya = models.CharField(max_length=9, blank=True, null=True)
    # email aslida AbstractUser da mavjud, lekin agar null=True kerak bo'lsa:
    email = models.EmailField(blank=True, null=True)
    status = models.BooleanField(default=True)
    
    created_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, related_name='monitoring_creator')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Monitoring | {self.rahbari}"





class TarkibiyTuzilma(models.Model):
    tuzilma_nomi = models.CharField(max_length=255)
    faoliyati = models.TextField()
    rahbari = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    passport_seriya = models.CharField(max_length=9, blank=True, null=True)
    # email aslida AbstractUser da mavjud, lekin agar null=True kerak bo'lsa:
    email = models.EmailField(blank=True, null=True)
    status = models.BooleanField()
    created_by = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tuzilma_created'
    )
    is_pending = models.BooleanField(default=False)  
    updated_by = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tuzilma_pending_updates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.tuzilma_nomi





class BolimCategory(models.Model):
    nomi = models.CharField(max_length=255)
    tuzilma = models.ForeignKey(
        'TarkibiyTuzilma', 
        on_delete=models.CASCADE, 
        related_name='bolim_kategoriyalari'
    )
    created_by = models.ForeignKey(
        'CustomUser', 
        on_delete=models.SET_NULL, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('nomi', 'tuzilma') # Bitta tuzilmada bir xil nomli bo'lim bo'lmasligi uchun

    def __str__(self):
        return f"{self.nomi} ({self.tuzilma.tuzilma_nomi})"




class Bolim(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='bolim_profile', 
        null=True, 
        blank=True
    )
    tuzilma = models.ForeignKey(TarkibiyTuzilma, on_delete=models.CASCADE, related_name="bolimlar")
    bolim_category = models.ForeignKey(
        BolimCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='xodimlar',
        verbose_name="Bo'lim nomi"
    )
    faoliyati = models.TextField()
    rahbari = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='bolim_photos/', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    passport_seriya = models.CharField(max_length=9, blank=True, null=True)
    status = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='bolim_creator')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        category_name = self.bolim_category.nomi if self.bolim_category else "Noma'lum"
        return f"{self.rahbari} | {category_name}"




class ArizaYuborish(models.Model):
    STATUS = (
        ("bajarilgan", "Bajarilgan"),
        ("qaytarildi", "Qaytarildi"),
        ("qabul qilindi", "Qabul qilindi"),
        ("jarayonda", "Jarayonda"),
    )
    TURI = (
        ("ijro", "Ijro uchun"),
        ("malumot", "Ma'lumot uchun"),
    )
    tuzilmalar = models.ManyToManyField(TarkibiyTuzilma, related_name="arizalar")
    turi = models.CharField(max_length=15, choices=TURI, default="ijro")
    ijro_muddati = models.DateField(null=True, blank=True)
    comment = models.TextField()
    extra_comment = models.TextField(null=True, blank=True)
    sana = models.DateTimeField(auto_now_add=True)
    kim_tomonidan = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="ariza_kim",
        verbose_name="Kim tomonidan",
        null=True, blank=True
    )
    
    parol = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS, default="jarayonda")
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=False)  
    bildirgi = models.FileField(upload_to='ariza_bildirgilar/' , null=True, blank=True)
    qayta_yuklandi = models.BooleanField(default=False)
    muddati_otgan = models.BooleanField(default=False)
    def __str__(self):
        if self.kim_tomonidan:
            user = self.kim_tomonidan.username
        else:
            user = "No user"
        return f"Ariza - {user} | {self.sana.strftime('%d.%m.%Y %H:%M')}"





class ArizaYuborishImage(models.Model):
    ariza = models.ForeignKey(
        ArizaYuborish, 
        on_delete=models.CASCADE, 
        related_name="rasmlar"
    )
    rasm = models.ImageField(upload_to="ariza_rasmlar_multi/")








class KelganArizalar(models.Model):
    STATUS = (
        ("bajarilgan", "Bajarilgan"),
        ("jarayonda", "Jarayonda"),
    )

    ariza = models.ForeignKey(ArizaYuborish, on_delete=models.CASCADE, related_name="kelganlar")
    # rasm = models.ImageField(upload_to='kelgan_rasmlar/')
    ilovalar = models.FileField(upload_to='ilovalar/', null=True, blank=True)
    akt_file = models.FileField(upload_to='kelgan_fayllar/', null=True, blank=True)
    sana = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    parol = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS, default="jarayonda")
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    
    turi = models.CharField(max_length=50)
    ijro_muddati = models.DateField(null=True, blank=True)
    bildirgi = models.FileField(upload_to='ariza_bildirgilar/', null=True, blank=True)
    def __str__(self):
        return f"Kelgan ariza - {self.ariza.id}"




class KelganArizaImage(models.Model):
    step = models.ForeignKey(
        KelganArizalar, 
        related_name="rasmlar", 
        on_delete=models.CASCADE
    )
    rasm = models.ImageField(upload_to="ariza_rasmlar_multi/")

    def __str__(self):
        return f"Rasm step {self.step.id}"




class PPRTuri(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    nomi = models.CharField(max_length=100, help_text="Masalan: Nomi", null=True, blank=True)
    qisqachanomi = models.CharField(max_length=100, help_text="Masalan: Qisqa nomi", null=True, blank=True,)
    davriyligi = models.IntegerField(help_text="Masalan: qancha vaqtda", null=True, blank=True)
    VaqtiChoises = (
        ("soat", "soat"),
        ("kun", "kun"),
        ("oy", "oy"),
    )
    vaqti = models.CharField(max_length=100,choices=VaqtiChoises, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='ppr_turlari/', null=True, blank=True)
    kimlar_qiladi = models.CharField(max_length=255, null=True, blank=True)
    tarkibiy_tuzilma = models.ForeignKey('TarkibiyTuzilma', on_delete=models.SET_NULL, null=True, blank=True)
    bekat = models.ForeignKey('Bekat', on_delete=models.SET_NULL, null=True, blank=True)
    bolim = models.ForeignKey('Bolim', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nomi




class ObyektNomi(models.Model):
    obyekt_nomi = models.CharField(max_length=255)
    toliq_nomi = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    tarkibiy_tuzilma = models.ForeignKey('TarkibiyTuzilma', on_delete=models.SET_NULL, null=True, blank=True)
    bekat = models.ForeignKey('Bekat', on_delete=models.SET_NULL, null=True, blank=True)
    bolim = models.ForeignKey('Bolim', on_delete=models.SET_NULL, null=True, blank=True)
    bolim_category = models.ForeignKey(
        'BolimCategory', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='obyektlar'
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['obyekt_nomi', 'tarkibiy_tuzilma', 'bekat', 'bolim_category'], 
                name='unique_obyekt_per_category'
            )
        ]
    def __str__(self):
        return self.obyekt_nomi



class ObyektLocation(models.Model):
    obyekt = models.OneToOneField(
        ObyektNomi,
        on_delete=models.CASCADE,
        related_name='location'
    )
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.obyekt.obyekt_nomi} ({self.lat}, {self.lng})"











class PPRJadval(models.Model):
    STATUS_CHOICES = (
        ("jarayonda", "Jarayonda"),
        ("yuborildi", "Yuborildi"),
        ("tasdiqlandi", "Tasdiqlandi"),
        ("rad_etildi", "Rad etildi"),
        ("bajarildi", "Bajarildi"),
        
    )
    sana = models.DateField(null=True, blank=True) # Faqat bitta kun uchun
    obyektlar = models.ManyToManyField(ObyektNomi, related_name="ppr_jadvallari")
    ppr_turi = models.ForeignKey(PPRTuri, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="jarayonda")
    tasdiqlangan = models.BooleanField(default=False)
    muddat = models.BooleanField(default=False)
    bolim_category = models.ForeignKey(
        BolimCategory, 
        on_delete=models.CASCADE, 
        related_name="ppr_jadvallari",
        null=True, # Eski ma'lumotlar xato bermasligi uchun
        blank=True
    )
    tarkibiy_tuzilma = models.ForeignKey('TarkibiyTuzilma', on_delete=models.SET_NULL, null=True, blank=True)
    bekat = models.ForeignKey('Bekat', on_delete=models.SET_NULL, null=True, blank=True)
    bolim = models.ForeignKey('Bolim', on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    def save(self, *args, **kwargs):
        from datetime import timedelta
        from django.utils import timezone

        # 1. Muddatni muhrlash (agar hali False bo'lsa)
        if not self.muddat and self.sana:
            # Status tasdiqlandi yoki bajarildi bo'lishi bilan tekshiramiz
            if self.status in ["tasdiqlandi", "bajarildi"]:
                if timezone.now().date() > (self.sana + timedelta(days=3)):
                    self.muddat = True
                    
        if self.pk and self.tasdiqlangan:
            update_fields = kwargs.get("update_fields", None)
            # faqat status update qilinmasa, xatoga yo'l qo'yish
            if not update_fields or "status" not in update_fields:
                raise ValueError("Tasdiqlangan jadvalni tahrirlash mumkin emas!")

        super().save(*args, **kwargs)





class PPRYuborish(models.Model):
    STATUS_CHOICES = [
        ('yuborildi', 'Yuborildi'),
        ('tasdiqlandi', 'Tasdiqlandi'),
        ('rad_etildi', 'Rad etildi'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    yil = models.IntegerField()
    oy = models.IntegerField()
    bolim_category = models.ForeignKey('BolimCategory', on_delete=models.CASCADE)
    tarkibiy_tuzilma = models.ForeignKey('TarkibiyTuzilma', on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='yuborildi')
    comment = models.TextField(null=True, blank=True) # Bo'lim xodimi izohi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['yil', 'oy', 'bolim_category', 'tarkibiy_tuzilma'],
                condition=models.Q(is_active=True),
                name='unique_active_ppr_yuborish'
            )
        ]
        
    def __str__(self):
        return f"{self.yil}-{self.oy} | {self.bolim_category} | {self.tarkibiy_tuzilma} | {self.status}"






class PPRTasdiqlash(models.Model):
    yuborish_paketi = models.OneToOneField(PPRYuborish, on_delete=models.CASCADE, related_name='qaror')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=[("tasdiqlandi", "Tasdiqlandi"), ("rad_etildi", "Rad etildi")])
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)




    
class PPRBajarildi(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    jadval = models.ForeignKey('PPRJadval', on_delete=models.CASCADE, related_name='bajarildilar')
    bajarilgan_obyektlar = models.ManyToManyField(ObyektNomi)
    comment = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='ppr_bajarildi_files/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.jadval} - {self.created_at}"




class PPRBajarildiImage(models.Model):
    bajarildi = models.ForeignKey(
        PPRBajarildi, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to='ppr_bajarildi_images/')




class PPRYakunlash(models.Model):
    yakunlash = models.BooleanField(default=False)
    
  



class Hujjatlar(models.Model):
    xizmat_hujjatlari = models.FileField(upload_to='hujjatlar/')

    def __str__(self):
        return self.xizmat_hujjatlari.name




class Notification(models.Model):
    bolim_category = models.ForeignKey('BolimCategory', on_delete=models.CASCADE, null=True, blank=True)
    tarkibiy_tuzilma = models.ForeignKey('TarkibiyTuzilma', on_delete=models.CASCADE, null=True, blank=True)
    
    # Faqat rahbarlarga tegishli xabarlar uchun (ixtiyoriy)
    for_rahbar = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link_id = models.IntegerField(null=True, blank=True) 
    # is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    seen_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='seen_notifications')
    read_times = models.JSONField(default=dict, blank=True)
    class Meta:
        ordering = ['-created_at']





class HujjatShabloni(models.Model):
    HUJJAT_TURLARI = (
        ("bildirgi", "Bildirgi"),
        ("ariza", "Ariza"),
        ("tushuntirish_xati", "Tushuntirish xati"),
        ("hisobot", "Hisobot"),
        ("boshqa", "Boshqa"),
    )

    nomi = models.CharField(max_length=50, choices=HUJJAT_TURLARI, verbose_name="Hujjat turi")
    file = models.FileField(upload_to='shablonlar/', verbose_name="Shablon fayli (Word)")
    
    # Qaysi tuzilma nomidan yuklanayotgani
    tuzilma = models.ForeignKey(
        'TarkibiyTuzilma', 
        on_delete=models.CASCADE, 
        related_name='shablonlar',
        verbose_name="Tarkibiy Tuzilma"
    )
    
    yuklovchi = models.ForeignKey(
        settings.AUTH_USER_MODEL, # CustomUser
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='yuklangan_shablonlar'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tuzilma.tuzilma_nomi} - {self.get_nomi_display()}"

    class Meta:
        verbose_name = "Hujjat Shabloni"
        verbose_name_plural = "Hujjat Shablonlari"
        ordering = ['-created_at']
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission



class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("tarkibiy", "Tarkibiy Tuzilma Rahbari"),
        ("bekat", "Bekat Rahbari"),
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









class ArizaYuborish(models.Model):
    STATUS = (
        ("bajarilgan", "Bajarilgan"),
        ("qaytarildi", "Qaytarildi"),
        ("qabul qilindi", "Qabul qilindi"),
        ("jarayonda", "Jarayonda"),
    )

    tuzilma = models.ForeignKey(TarkibiyTuzilma, on_delete=models.CASCADE, related_name="arizalar")
    comment = models.TextField()
    sana = models.DateTimeField(auto_now_add=True)
    # photo = models.ImageField(upload_to='ariza_rasmlari/', blank=True, null=True)
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
        ("bajarildi", "Bajarildi"),
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

    def __str__(self):
        return f"Kelgan ariza - {self.ariza.id}"




# class KelganArizalarImage(models.Model):
#     kelgan = models.ForeignKey(
#         KelganArizalar, 
#         on_delete=models.CASCADE, 
#         related_name="rasmlar"
#     )
#     rasm = models.ImageField(upload_to="kelgan_rasmlar_multi/")





class PPRTuri(models.Model):
    nomi = models.CharField(max_length=200)
    davriyligi = models.IntegerField(max_length=100, help_text="Masalan: har necha oyda", null=True, blank=True)

    def __str__(self):
        return self.nomi


class ObyektNomi(models.Model):
    obyekt_nomi = models.CharField(max_length=255)

    def __str__(self):
        return self.obyekt_nomi


class PPRJadval(models.Model):
    Choose_oy = (
        ("Yanvar", "Yanvar"),
        ("Fevral", "Fevral"),
        ("Mart", "Mart"),
        ("Aprel", "Aprel"),
        ("May", "May"),
        ("Iyun", "Iyun"),
        ("Iyul", "Iyul"),
        ("Avgust", "Avgust"),
        ("Sentabr", "Sentabr"),
        ("Oktabr", "Oktabr"),
        ("Noyabr", "Noyabr"),
        ("Dekabr", "Dekabr"),
    )
    Choose_kim = (
        ("Texnik", "Texnik"),
        ("AKT_xodimi", "AKT_xodimi"),
        )
    oy = models.CharField(max_length=20, choices=Choose_oy)
    obyekt = models.ForeignKey(ObyektNomi, on_delete=models.CASCADE)
    ppr_turi = models.ForeignKey(PPRTuri, on_delete=models.CASCADE)
    kim_tomonidan = models.CharField(max_length=255, null=True, blank=True, choices=Choose_kim)

    def __str__(self):
        return f"{self.oy} - {self.obyekt}"



class Hujjatlar(models.Model):
    xizmat_hujjatlari = models.FileField(upload_to='hujjatlar/')

    def __str__(self):
        return self.xizmat_hujjatlari.name



# 8. Notifications

class Notifications(models.Model):
    ppr_qilish_oylik = models.CharField(max_length=255)

    def __str__(self):
        return self.ppr_qilish_oylik

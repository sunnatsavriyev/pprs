from calendar import calendar
from datetime import timedelta, timezone
from urllib import request
from attr import attrs
from rest_framework import serializers
from .models import *
import os
import random
import json
from django.db.models import Q
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
def generate_unique_passport():
    while True:
        code = f"AD{random.randint(1000000, 9999999)}"
        if not Bekat.objects.filter(passport_seriya=code).exists():
            return code



ALLOWED_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".heic",
    ".heif",
    ".avif",
]

def validate_image_format(image):
    ext = os.path.splitext(image.name)[1].lower()
    content_type = image.content_type.lower()

    allowed_ext = [
        ".jpg",
        ".jpeg",
        ".png",
        ".heic",
        ".heif",
        ".avif",
    ]

    allowed_mime = [
        "image/jpeg",
        "image/png",
        "image/heic",
        "image/heif",
        "image/avif",                 
        "application/octet-stream",  
        "binary/octet-stream"
    ]

    if ext not in allowed_ext and content_type not in allowed_mime:
        raise serializers.ValidationError(
            f"Rasm formati qo‘llab-quvvatlanmaydi! ({content_type} / {ext}). "
            "Faqat JPG, JPEG, PNG, HEIC, HEIF, AVIF formatlari ruxsat etiladi."
        )


class UserTuzilmaSerializer(serializers.ModelSerializer):
    bekat_nomi = serializers.CharField(required=False, allow_null=True)
    tuzilma_nomi = serializers.CharField(required=False)
    bolim_nomi = serializers.CharField(
    source="bolim_profile.bolim_category.nomi",
    read_only=True
    )
    bolim_name = serializers.CharField(required=False, allow_blank=True)
    faoliyati = serializers.CharField(required=False, allow_blank=True)
    rahbari = serializers.CharField(required=False)
    email = serializers.EmailField(required=False, allow_null=True)
    birth_date = serializers.DateField(required=False, allow_null=True, input_formats=['%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d'],)
    photo = serializers.ImageField(required=False, allow_null=True)
    passport_seriya = serializers.CharField(required=False)
    status = serializers.BooleanField(required=False)
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        min_length=6
    )


    class Meta:
        model = CustomUser
        fields = [
            "id", "username", "password", "role",
            "tarkibiy_tuzilma", "tarkibiy_tuzilma_id", "bekat_nomi", "bolim_nomi","bolim_id","bolim_name",
            "tuzilma_nomi", "faoliyati", "rahbari",
            "email", "birth_date",
            "passport_seriya", "status", "photo"
        ]
        extra_kwargs = {
            "tarkibiy_tuzilma": {"read_only": True},
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request")  

        if instance.bekat_nomi:
            rep["status"] = instance.bekat_nomi.status
            rep["faoliyati"] = instance.bekat_nomi.faoliyati
            if instance.bekat_nomi.photo:
                rep["photo"] = request.build_absolute_uri(instance.bekat_nomi.photo.url)
            else:
                rep["photo"] = None
            rep["bekat_nomi"] = instance.bekat_nomi.bekat_nomi 
            rep["rahbari"] = instance.bekat_nomi.rahbari
            rep["email"] = instance.bekat_nomi.email
            rep["birth_date"] = instance.bekat_nomi.birth_date.strftime("%d-%m-%Y") if instance.bekat_nomi.birth_date else None
            rep["passport_seriya"] = instance.bekat_nomi.passport_seriya
            rep["created_at"] = instance.bekat_nomi.created_at.strftime("%d-%m-%Y") if instance.bekat_nomi.created_at else None
            rep["created_by"] = instance.bekat_nomi.created_by.username if instance.bekat_nomi.created_by else None
            
        if instance.role == "monitoring" and instance.monitoring:
            m = instance.monitoring

            rep["status"] = m.status
            rep["faoliyati"] = m.faoliyati
            rep["rahbari"] = m.rahbari
            rep["email"] = m.email
            rep["birth_date"] = m.birth_date.strftime("%d-%m-%Y") if m.birth_date else None
            rep["passport_seriya"] = m.passport_seriya
            rep["created_at"] = m.created_at.strftime("%d-%m-%Y") if m.created_at else None
            rep["created_by"] = m.created_by.username if m.created_by else None

            if m.photo:
                rep["photo"] = request.build_absolute_uri(m.photo.url)
            else:
                rep["photo"] = None


        elif instance.role == "tarkibiy" and instance.tarkibiy_tuzilma:
            rep["status"] = instance.tarkibiy_tuzilma.status
            rep["faoliyati"] = instance.tarkibiy_tuzilma.faoliyati
            if instance.tarkibiy_tuzilma.photo:
                rep["photo"] = request.build_absolute_uri(instance.tarkibiy_tuzilma.photo.url)
            else:
                rep["photo"] = None
            rep["tarkibiy_tuzilma"] = instance.tarkibiy_tuzilma.tuzilma_nomi
            rep["tarkibiy_tuzilma_id"] = instance.tarkibiy_tuzilma.id
            rep["rahbari"] = instance.tarkibiy_tuzilma.rahbari
            rep["email"] = instance.tarkibiy_tuzilma.email
            rep["birth_date"] = instance.tarkibiy_tuzilma.birth_date.strftime("%d-%m-%Y") if instance.tarkibiy_tuzilma.birth_date else None
            rep["passport_seriya"] = instance.tarkibiy_tuzilma.passport_seriya
            rep["created_at"] = instance.tarkibiy_tuzilma.created_at.strftime("%d-%m-%Y") if instance.tarkibiy_tuzilma.created_at else None
            rep["created_by"] = instance.tarkibiy_tuzilma.created_by.username if instance.tarkibiy_tuzilma.created_by else None

        elif instance.role == "admin" or instance.is_superuser:
            rep["faoliyati"] = "Admin foydalanuvchi"
            rep["photo"] = request.build_absolute_uri(instance.photo.url) if instance.photo else None
            rep["email"] = instance.email
            rep["rahbari"] = instance.username
            rep["birth_date"] = instance.birth_date.strftime("%d-%m-%Y") if instance.birth_date else None
            rep["status"] = True
            rep["passport_seriya"] = instance.passport_seriya
            


            
            
        if instance.role == "bolim":
            bolim = getattr(instance, "bolim_profile", None)
            if bolim:
                rep["faoliyati"] = bolim.faoliyati
                rep["rahbari"] = bolim.rahbari
                rep["email"] = bolim.email
                rep["birth_date"] = bolim.birth_date.strftime("%d-%m-%Y") if bolim.birth_date else None
                rep["passport_seriya"] = bolim.passport_seriya
                rep["status"] = bolim.status
                if bolim.photo:
                    rep["photo"] = request.build_absolute_uri(bolim.photo.url) if request else bolim.photo.url
                
                # CustomUser dagi FK ni o'rniga bolim_nomi ni yozish
                rep["bolim_nomi"] = bolim.bolim_category.nomi if bolim.bolim_category else None
                rep["bolim_id"] = bolim.id
                rep["tarkibiy_tuzilma"] = bolim.tuzilma.tuzilma_nomi if bolim.tuzilma else None
                rep["tarkibiy_tuzilma_id"] = bolim.tuzilma.id
                rep["created_at"] = (
                    bolim.created_at.strftime("%d-%m-%Y")
                    if bolim.created_at else None
                )
                rep["created_by"] = (
                    bolim.created_by.username
                    if bolim.created_by else None
                )




        show_password = False
        if request:
            if request.user.is_admin() or request.user.is_superuser:
                show_password = True
            elif request.user.id == instance.id:
                show_password = True

        if show_password:
            rep["password"] = getattr(instance, "_raw_password", None)
        else:
            rep["password"] = None  

        return rep


    def get_bolim_nomi(self, instance):
        bolim = getattr(instance, "bolim_profile", None)
        if bolim and bolim.bolim_category:
            return bolim.bolim_category.nomi
        return None





    # ---------- Validatsiya ----------
    def validate(self, attrs):
        role = attrs.get("role", getattr(self.instance, "role", None))
        is_create = self.instance is None
        
        if is_create:
            password = attrs.get("password")
            if not password:
                raise serializers.ValidationError({
                    "password": "Parol majburiy va bo‘sh bo‘lishi mumkin emas"
                })

        if role == "tarkibiy":
            required_fields = [ "faoliyati", "rahbari"]
            for f in required_fields:
                if not attrs.get(f):
                    raise serializers.ValidationError({f: "Majburiy maydon"})

        if role == "bekat" and not attrs.get("bekat_nomi"):
            raise serializers.ValidationError({"bekat_nomi": "Bekat tanlanishi shart!"})
        
        
        

        return attrs

    # ---------- Create ----------
    def create(self, validated_data):
        raw_password = validated_data.pop("password")
        role = validated_data["role"]
        uploaded_photo = validated_data.pop("photo", None)

        # Tarkibiy tuzilma yaratish
        tuzilma = None
        if role == "tarkibiy":
            tuzilma = TarkibiyTuzilma.objects.create(
                tuzilma_nomi=validated_data["tuzilma_nomi"],
                faoliyati=validated_data["faoliyati"],
                rahbari=validated_data["rahbari"],
                passport_seriya = validated_data.get("passport_seriya", None),
                status=validated_data.get("status", False),
                is_pending=True,
                photo=uploaded_photo,
                email=validated_data.get("email", None),
                birth_date=validated_data.get("birth_date", None),
                created_by=self.context["request"].user
            )

        # USER YARATISH
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            password=raw_password,
            role=role
        )
        
        if role == "admin":
            user.email = validated_data.get("email", "")
            user.birth_date = validated_data.get("birth_date")
            user.passport_seriya = validated_data.get("passport_seriya")
            if uploaded_photo:
                user.photo = uploaded_photo
            user._raw_password = raw_password
            user.save()
            return user

        if role == "tarkibiy":
            user.tarkibiy_tuzilma = tuzilma
            
        if role == "monitoring":
            monitoring = Monitoring.objects.create(
                faoliyati=validated_data.get("faoliyati", "Monitoring xodimi"),
                rahbari=validated_data.get("rahbari", ""),
                status=validated_data.get("status", True),
                email=validated_data.get("email"),
                birth_date=validated_data.get("birth_date"),
                passport_seriya=validated_data.get("passport_seriya"),
                photo=uploaded_photo,
                created_by=self.context["request"].user
            )

            user.monitoring = monitoring
            user._raw_password = raw_password
            user.save()
            return user




        if role == "bekat":
            bekat_value = validated_data.get("bekat_nomi")
            if isinstance(bekat_value, str):
                # har doim yangi bekat yaratish
                bekat_obj = Bekat.objects.create(
                    bekat_nomi=bekat_value,
                    faoliyati=validated_data.get("faoliyati", ""),
                    rahbari=validated_data.get("rahbari", ""),
                    passport_seriya=validated_data.get("passport_seriya", generate_unique_passport()),
                    status=validated_data.get("status", False),
                    photo=uploaded_photo,
                    email=validated_data.get("email", None),
                    birth_date=validated_data.get("birth_date", None),
                    created_by=self.context["request"].user
                )
                user.bekat_nomi = bekat_obj


        user._raw_password = raw_password
        user.save()
        return user

    # ---------- Update ----------
    def update(self, instance, validated_data):
        raw_password = validated_data.get("password")
        uploaded_photo = validated_data.pop("photo", None)
        if raw_password:
            instance.set_password(raw_password)
            instance._raw_password = raw_password

        instance.username = validated_data.get("username", instance.username)
        new_role = validated_data.get("role", instance.role)
        status_value = validated_data.get("status", None)
        email_value = validated_data.get("email")
        birth_value = validated_data.get("birth_date")

        # --------- Rol o'zgarganda faqat rol va nom bog'lanishini o'chirish ---------
        if instance.role != new_role:
            if instance.role == "bekat" and new_role == "tarkibiy":
                # eski bekat nomi va roli o'chadi, qolgan maydonlar saqlanadi
                old_bekat_photo = instance.bekat_nomi.photo if instance.bekat_nomi else None
                instance.bekat_nomi = None
            elif instance.role == "tarkibiy" and new_role == "bekat":
                old_tuzilma_photo = instance.tarkibiy_tuzilma.photo if instance.tarkibiy_tuzilma else None
                instance.tarkibiy_tuzilma = None

        # ------------------ TARKIBIY ------------------
        if new_role == "tarkibiy":
            t = instance.tarkibiy_tuzilma
            if t:
                t.tuzilma_nomi = validated_data.get("tuzilma_nomi", t.tuzilma_nomi)
                t.faoliyati = validated_data.get("faoliyati", t.faoliyati)
                t.rahbari = validated_data.get("rahbari", t.rahbari)
                t.passport_seriya = validated_data.get("passport_seriya", t.passport_seriya)
                t.status = status_value if status_value is not None else t.status
                t.email = email_value if email_value is not None else t.email
                t.birth_date = birth_value if birth_value is not None else t.birth_date
                if uploaded_photo is not None:
                    t.photo = uploaded_photo
                elif instance.role == "bekat" and old_bekat_photo:
                    t.photo = old_bekat_photo
                t.save()
            else:
                t = TarkibiyTuzilma.objects.create(
                    tuzilma_nomi=validated_data.get("tuzilma_nomi", ""),
                    faoliyati=validated_data.get("faoliyati", ""),
                    rahbari=validated_data.get("rahbari", ""),
                    passport_seriya=validated_data.get("passport_seriya", generate_unique_passport()),
                    status=status_value if status_value is not None else False,
                    photo=uploaded_photo if uploaded_photo else (old_bekat_photo if instance.role=="bekat" else None),
                    email=email_value,
                    birth_date=birth_value,
                    is_pending=True,
                    created_by=self.context["request"].user
                )
                instance.tarkibiy_tuzilma = t

        # ------------------ BEKAT ------------------
        elif new_role == "bekat":
            bekat_value = validated_data.get("bekat_nomi")
            if isinstance(bekat_value, str):
                bekat_obj, created = Bekat.objects.get_or_create(
                    bekat_nomi=bekat_value,
                    defaults={
                        "faoliyati": validated_data.get("faoliyati", ""),
                        "rahbari": validated_data.get("rahbari", ""),
                        "passport_seriya": generate_unique_passport(),
                        "status": status_value if status_value is not None else False,
                        "photo": uploaded_photo if uploaded_photo else (old_tuzilma_photo if instance.role=="tarkibiy" else None),
                        "email": email_value,
                        "birth_date": birth_value,
                        "created_by": self.context["request"].user
                    }
                )
                if not created:
                    if "faoliyati" in validated_data:
                        bekat_obj.faoliyati = validated_data["faoliyati"]
                    if "rahbari" in validated_data:
                        bekat_obj.rahbari = validated_data["rahbari"]
                    if "passport_seriya" in validated_data:
                        bekat_obj.passport_seriya = validated_data["passport_seriya"]
                    if "status" in validated_data:
                        bekat_obj.status = validated_data["status"]

                    if email_value is not None:
                        bekat_obj.email = email_value
                    if birth_value is not None:
                        bekat_obj.birth_date = birth_value

                    if uploaded_photo is not None:
                        bekat_obj.photo = uploaded_photo

                    bekat_obj.save()

                instance.bekat_nomi = bekat_obj
                
        # ------------------ BOLIM ------------------
        elif new_role == "bolim":
            bolim_profile = getattr(instance, "bolim_profile", None)
            if bolim_profile:
                # mavjud profilni yangilash
                bolim_nomi_new = validated_data.get("bolim_nomi")
                if bolim_nomi_new:  
                    bolim_profile.bolim_nomi = bolim_nomi_new

                bolim_profile.faoliyati = validated_data.get("faoliyati", bolim_profile.faoliyati)
                bolim_profile.rahbari = validated_data.get("rahbari", bolim_profile.rahbari)
                bolim_profile.passport_seriya = validated_data.get("passport_seriya", bolim_profile.passport_seriya)
                bolim_profile.status = validated_data.get("status", bolim_profile.status)
                bolim_profile.email = validated_data.get("email", bolim_profile.email)
                bolim_profile.birth_date = validated_data.get("birth_date", bolim_profile.birth_date)
                if uploaded_photo is not None:
                    bolim_profile.photo = uploaded_photo
                bolim_profile.save()
            else:
                # yangi bolim profilini yaratish
                if instance.tarkibiy_tuzilma:
                    bolim_profile = Bolim.objects.create(
                        user=instance,
                        tuzilma=instance.tarkibiy_tuzilma,
                        bolim_nomi=validated_data.get("bolim_nomi", ""),  # yangi yaratishda bo'sh bo'lishi mumkin
                        faoliyati=validated_data.get("faoliyati", ""),
                        rahbari=validated_data.get("rahbari", ""),
                        passport_seriya=validated_data.get("passport_seriya", generate_unique_passport()),
                        status=validated_data.get("status", True),
                        photo=uploaded_photo if uploaded_photo else None,
                        email=validated_data.get("email"),
                        birth_date=validated_data.get("birth_date"),
                        created_by=self.context["request"].user
                    )
                instance.bolim_profile = bolim_profile



        # ------------------ MONITORING ------------------
        elif new_role == "monitoring":
            monitoring = instance.monitoring

            if monitoring:
                monitoring.faoliyati = validated_data.get("faoliyati", monitoring.faoliyati)
                monitoring.rahbari = validated_data.get("rahbari", monitoring.rahbari)
                monitoring.status = validated_data.get("status", monitoring.status)
                monitoring.email = email_value if email_value is not None else monitoring.email
                monitoring.birth_date = birth_value if birth_value is not None else monitoring.birth_date
                monitoring.passport_seriya = validated_data.get(
                    "passport_seriya", monitoring.passport_seriya
                )

                if uploaded_photo is not None:
                    monitoring.photo = uploaded_photo

                monitoring.save()




        elif new_role == "admin":
            if "email" in validated_data:
                instance.email = validated_data["email"]
            if "birth_date" in validated_data:
                instance.birth_date = validated_data["birth_date"]
            if "passport_seriya" in validated_data:
                instance.passport_seriya = validated_data["passport_seriya"]
            if uploaded_photo is not None:
                instance.photo = uploaded_photo
            

        instance.role = new_role
        instance.save()
        return instance



class TuzilmaSerializers(serializers.ModelSerializer):
    class Meta:
        model = TarkibiyTuzilma
        fields = "__all__"


class BolimCategorySerializer(serializers.ModelSerializer):
    tuzilma_nomi = serializers.CharField(source='tuzilma.tuzilma_nomi', read_only=True)
    class Meta:
        model = BolimCategory
        fields = ['id', 'nomi', 'tuzilma', 'tuzilma_nomi','created_at']
        read_only_fields = ['tuzilma', 'created_by']
        
        
        

class BolimUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, default="1234")
    tuzilma = serializers.PrimaryKeyRelatedField(read_only=True)
    tuzilma_nomi = serializers.CharField(source="tuzilma.tuzilma_nomi", read_only=True)
    bolim_category_id = serializers.PrimaryKeyRelatedField(
        queryset=BolimCategory.objects.none(), 
        source='bolim_category', 
        write_only=True,
        required=True
    )
    bolim_nomi = serializers.CharField(source='bolim_category.nomi', read_only=True)
    class Meta:
        model = Bolim
        fields = [
            "id", "tuzilma", "tuzilma_nomi", "bolim_category_id", "bolim_nomi",
            "username", "password",
            "faoliyati", "rahbari", "photo", "email",
            "birth_date", "passport_seriya", "status", "created_at"
        ]
        read_only_fields = ["created_at"]
        
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context['request'].user

        # Agar user admin / superuser bo'lsa hamma kategoriyalarni ko'rsatamiz
        if user.is_superuser or user.role in ["admin", "monitoring"]:
            self.fields['bolim_category_id'].queryset = BolimCategory.objects.all()
        # Foydalanuvchi tarkibiy bo'lsa, faqat o'z tuzilmasidagi kategoriyalar
        elif user.role == "tarkibiy" and user.tarkibiy_tuzilma:
            self.fields['bolim_category_id'].queryset = BolimCategory.objects.filter(
                tuzilma=user.tarkibiy_tuzilma
            )
        else:
            self.fields['bolim_category_id'].queryset = BolimCategory.objects.none()

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        username = validated_data.pop("username")
        password = validated_data.pop("password")
        
        # source='bolim_category' orqali kelgan ob'ekt
        bolim_category = validated_data.pop("bolim_category", None)  

        # -------- TUZILMA TEKSHIRUVI --------
        if user.role == "tarkibiy":
            tuzilma = user.tarkibiy_tuzilma
            if not tuzilma:
                raise serializers.ValidationError({"tuzilma": "Sizga tuzilma biriktirilmagan"})
            if bolim_category.tuzilma != tuzilma:
                raise serializers.ValidationError({"bolim_category_id": "Bu bo'lim nomi sizning tuzilmangizga tegishli emas!"})
        elif user.role in ["admin", "superuser"]:
            tuzilma = validated_data.pop("tuzilma", None) or user.tarkibiy_tuzilma
        else:
            raise serializers.PermissionDenied("Bo‘lim yaratishga ruxsatingiz yo‘q")

        # -------- USER YARATISH --------
        new_user = CustomUser.objects.create_user(
            username=username,
            password=password,
            role="bolim",
            tarkibiy_tuzilma=tuzilma
        )
        new_user._raw_password = password
        new_user.save()

        # -------- BO‘LIM PROFILINI YARATISH --------
        bolim = Bolim.objects.create(
            user=new_user,
            tuzilma=tuzilma,
            bolim_category=bolim_category,
            created_by=user,
            **validated_data  # endi bu yerda validated_data ichida tuzilma yo'q
        )

        new_user.bolim_profile = bolim
        new_user.save()

        return bolim






class ArizaImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArizaYuborishImage
        fields = ["id","rasm"]




class StepSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    comment = serializers.CharField()
    extra_comment = serializers.CharField()
    status = serializers.CharField()
    created_by = serializers.CharField(allow_null=True)
    is_approved = serializers.BooleanField()
    sana = serializers.DateTimeField()




class TuzilmaTargetSerializer(serializers.Serializer):
    tuzilma = serializers.PrimaryKeyRelatedField(
        queryset=TarkibiyTuzilma.objects.all(),
        required=True
    )
    extra_comment = serializers.CharField(required=False, allow_blank=True)



class ArizaYuborishSerializer(serializers.ModelSerializer):
    # O'qish uchun (GET)
    tuzilmalar = serializers.PrimaryKeyRelatedField(
        read_only=True, 
        many=True
    )
    
    # YOZISH UCHUN (POST) - yangi format
    # Bu yerda [{tuzilma: 1, extra_comment: "A"}, {tuzilma: 2, extra_comment: "B"}] keladi
    targets = TuzilmaTargetSerializer(many=True, write_only=True,required=False)

    # Qolgan maydonlar o'zgarishsiz...
    parol = serializers.CharField(write_only=True)
    photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    bildirgi = serializers.FileField(required=False)
    rasmlar = ArizaImagesSerializer(many=True, read_only=True)
    tuzilma_nomlari = serializers.SerializerMethodField()
    kim_tomonidan = serializers.SerializerMethodField()
    created_by = serializers.CharField(source="created_by.username", read_only=True)
    sana = serializers.DateTimeField(format="%d-%m-%Y", read_only=True)
    ijro_muddati = serializers.DateField(
        format="%d-%m-%Y",
        required=False,
        allow_null=True
    )

    steplar = serializers.SerializerMethodField()
    muddati_otgan = serializers.BooleanField(read_only=True)

    class Meta:
        model = ArizaYuborish
        fields = [
            "id", "comment", "parol", 
            "tuzilmalar",  
            "targets",     
            "tuzilma_nomlari", "kim_tomonidan", 
            "created_by", "status", 'turi', 'ijro_muddati', 
            "is_approved", "photos", "rasmlar", "bildirgi", 
            "steplar", "qayta_yuklandi", "sana", 
            "extra_comment" ,"muddati_otgan"
        ]
        read_only_fields = ["kim_tomonidan", "created_by", "status", "is_approved", 'steplar', 'extra_comment']

    
    def get_tuzilma_nomlari(self, obj):
        return [t.tuzilma_nomi for t in obj.tuzilmalar.all()]
    
    
    
    def to_representation(self, instance):
        """ Har safar ma'lumotni ko'rganda muddatni tekshiradi """
        today = timezone.now().date()
        
        # Agar turi 'ijro' bo'lsa, muddati bo'lsa va hali False bo'lsa tekshiramiz
        if (instance.turi == "ijro" and 
            instance.ijro_muddati and 
            instance.ijro_muddati < today and 
            not instance.muddati_otgan):
            
            instance.muddati_otgan = True
            instance.save(update_fields=['muddati_otgan'])
            
        return super().to_representation(instance)
    
    
    
    def get_kim_tomonidan(self, obj):
        user = obj.kim_tomonidan
        if not user:
            return None
        
        request = self.context.get('request')

        # foydalanuvchi rasmi URL sini olish
        if user.bekat_nomi and user.bekat_nomi.photo:
            photo_url = request.build_absolute_uri(user.bekat_nomi.photo.url) if request else None
            name = user.bekat_nomi.bekat_nomi
        elif user.tarkibiy_tuzilma and user.tarkibiy_tuzilma.photo:
            photo_url = request.build_absolute_uri(user.tarkibiy_tuzilma.photo.url) if request else None
            name = user.tarkibiy_tuzilma.tuzilma_nomi
        else:
            photo_url = request.build_absolute_uri(user.photo.url) if (user.photo and request) else None
            name = user.username

        return {
            "name": name,
            "photo": photo_url
        }

    
    
    def validate_photos(self, photos):
        for img in photos:
            validate_image_format(img)
        return photos

    
    def get_steplar(self, obj):
        request = self.context.get('request')
        steps = []


        # 2. Kelgan snapshotlar (KelganArizalar)
        for step in obj.kelganlar.all().order_by('id'):
            step_rasmlar = [request.build_absolute_uri(img.rasm.url) for img in step.rasmlar.all()]
            steps.append({
                "id": step.id,
                "comment": step.comment,
                "status": step.status,
                "created_by": step.created_by.username if step.created_by else None,
                "is_approved": step.is_approved,
                "sana": step.sana,
                "akt_file": request.build_absolute_uri(step.akt_file.url) if step.akt_file else None,
                "ilovalar": request.build_absolute_uri(step.ilovalar.url) if step.ilovalar else None,
                "bildirgi": request.build_absolute_uri(step.bildirgi.url) if getattr(step, 'bildirgi', None) else None,
                "rasmlar": step_rasmlar
            })

        return steps


    
    
    
    def validate_parol(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Parol noto'g'ri!")
        return value

    
    
    def to_internal_value(self, data):
        """
        Frontenddan kelayotgan FormData ichidagi string-JSONlarni 
        haqiqiy Python formatiga o'tkazib beradi.
        """
        # data - bu QueryDict (immutable). Uni o'zgartirish uchun nusxa olamiz.
        try:
            mutable_data = data.dict() # Agar bitta qiymatli maydonlar bo'lsa
        except AttributeError:
            mutable_data = data.copy()

        # 1. targets - agar string bo'lsa (JSON.stringify qilingan bo'lsa)
        targets = data.get('targets')
        if isinstance(targets, str):
            try:
                mutable_data['targets'] = json.loads(targets)
            except (json.JSONDecodeError, TypeError):
                pass

        # 2. photos - FormData bir xil nomli bir nechta faylni yuborganda 
        # faqat oxirgisini olishi mumkin, shuning uchun list qilib olamiz
        if hasattr(data, 'getlist'):
            photos = data.getlist('photos')
            if photos:
                mutable_data['photos'] = photos

        return super().to_internal_value(mutable_data)

    def create(self, validated_data):
        user = self.context['request'].user
        
        # 1. Frontenddan kelgan targets (tuzilma + extra_comment) ro'yxatini ajratib olamiz
        targets_data = validated_data.pop("targets", [])
        photos = validated_data.pop("photos", [])
        
        if not targets_data:
            raise serializers.ValidationError({"targets": "Kamida bitta tuzilma tanlanishi shart."})

        created_arizalar = []

        for item in targets_data:
            tuzilma_obj = item['tuzilma']          
            specific_comment = item.get('extra_comment', "") 

            ariza = ArizaYuborish.objects.create(
                comment=validated_data.get("comment"),     
                extra_comment=specific_comment,             
                parol=validated_data.get("parol"),
                turi=validated_data.get("turi", "ijro"),
                ijro_muddati=validated_data.get("ijro_muddati") if validated_data.get("turi") == "ijro" else None,
                created_by=user,
                kim_tomonidan=user,
                bildirgi=validated_data.get("bildirgi"),    # Fayl hammasiga nusxalanadi (link orqali)
                status="jarayonda",
                is_approved=user.is_superuser
            )
            
            # 4. Tuzilmani bog'laymiz 
            # (Sizning modelingizda M2M, shuning uchun add qilamiz, lekin baribir bitta tuzilma bo'ladi)
            ariza.tuzilmalar.add(tuzilma_obj)

            # 5. Rasmlarni har bir ariza uchun alohida saqlaymiz
            for img in photos:
                ArizaYuborishImage.objects.create(ariza=ariza, rasm=img)
            
            created_arizalar.append(ariza)

        return created_arizalar[-1]
    
    
    def validate(self, attrs):
                
        if self.instance:
            locked_statuses = ['bajarilgan', 'qabul qilindi']
            
            if self.instance.status in locked_statuses:
                if 'ijro_muddati' in attrs or 'comment' in attrs:
                    raise serializers.ValidationError(
                        f"Ariza '{self.instance.get_status_display()}' holatida. Uni tahrirlash taqiqlangan!"
                    )
        return attrs
    
    
    def update(self, instance, validated_data):
        user = self.context['request'].user

        
        locked_statuses = ['bajarilgan', 'qabul qilindi']
        
        if instance.status in locked_statuses:
            return instance
        # 1. Ma'lumotlarni olish (kelmasa eskisini saqlab qolish)
        new_comment = validated_data.get("comment", instance.comment)
        new_photos = validated_data.pop("photos", None)
        new_bildirgi = validated_data.get("bildirgi", instance.bildirgi)
        new_turi = validated_data.get("turi", instance.turi)
        new_ijro_muddati = validated_data.get("ijro_muddati", instance.ijro_muddati)
        new_parol = validated_data.get("parol")


        
        
        bildirgi_was_sent = "bildirgi" in validated_data
        new_bildirgi = validated_data.get("bildirgi", None)
        
        
        # 2. Asosiy arizani yangilash
        instance.status = "jarayonda"
        instance.qayta_yuklandi = True
        instance.turi = new_turi
        instance.ijro_muddati = new_ijro_muddati
        
        # Agar yangi bildirgi fayli yuborilgan bo'lsa yangilaymiz
        if bildirgi_was_sent:
            instance.bildirgi = new_bildirgi
            
        instance.save()

        # 3. Yangi STEP (KelganArizalar) yaratish
        # Bu har safar PUT bo'lganda tarix (history) sifatida qo'shiladi
        step = KelganArizalar.objects.create(
            ariza=instance,
            created_by=user,
            comment=new_comment,
            status="jarayonda",
            is_approved=user.is_superuser,
            turi=new_turi,
            ijro_muddati=new_ijro_muddati,
            parol=new_parol,
            # Agar bildirgi yangilangan bo'lsa stepga ham biriktiramiz
            bildirgi=new_bildirgi if bildirgi_was_sent else None
        )

        # 4. Rasmlarni bog‘lash
        # Agar yangi rasm yuborilgan bo'lsa, ularni yangi stepga biriktiramiz
        if new_photos:
            for img in new_photos:
                # Eslatma: Model nomingiz KelganArizaImage yoki KelganArizalarImage ekanligini tekshiring
                KelganArizaImage.objects.create(step=step, rasm=img)
        else:
            
            pass

        return instance



















# class KelganArizaImagesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = KelganArizalarImage
#         fields = ["id","rasm"]


class KelganArizalarSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.username", read_only=True)
    ariza_comment = serializers.CharField(source="ariza.comment", read_only=True)
    ariza_tuzilma = serializers.CharField(source="ariza.tuzilma.tuzilma_nomi", read_only=True)
    
    # bu yerda SerializerMethodField ishlatiladi
    ariza_kim_tomonidan = serializers.SerializerMethodField()
    
    sana = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    ariza = serializers.PrimaryKeyRelatedField(
        queryset=ArizaYuborish.objects.all(),  
        write_only=True
    )
    parol = serializers.CharField(write_only=True)
    # rasmlar = KelganArizaImagesSerializer(many=True, read_only=True)

    class Meta:
        model = KelganArizalar
        fields = [
            "id", "akt_file",'ilovalar', "comment", "created_by", 
            "is_approved", "sana", "ariza_comment", "ariza_tuzilma", 
            "ariza_kim_tomonidan", "ariza", "parol"
        ]
        read_only_fields = [
            "created_by", "is_approved", "sana",
            "ariza_comment", "ariza_tuzilma", "ariza_kim_tomonidan"
        ]

    def get_ariza_kim_tomonidan(self, obj):
        user = obj.ariza.kim_tomonidan
        if not user:
            return None
        
        request = self.context.get('request')

        # Foydalanuvchining rasmi va nomini aniqlash
        if user.tarkibiy_tuzilma and user.tarkibiy_tuzilma.photo:
            photo_url = request.build_absolute_uri(user.tarkibiy_tuzilma.photo.url) if request else None
            name = user.tarkibiy_tuzilma.tuzilma_nomi
        elif user.bekat_nomi and user.bekat_nomi.photo:
            photo_url = request.build_absolute_uri(user.bekat_nomi.photo.url) if request else None
            name = user.bekat_nomi.bekat_nomi
        else:
            photo_url = request.build_absolute_uri(user.photo.url) if (user.photo and request) else None
            name = user.username

        return {
            "name": name,
            "photo": photo_url
        }
    
    
    # def validate_rasmlar(self, rasmlar):
    #     for img in rasmlar:
    #         validate_image_format(img)
    #     return rasmlar


    def validate_parol(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Parol noto'g'ri!")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        # images = validated_data.pop("rasmlar", [])
        
        validated_data.pop('created_by', None)
        validated_data.pop('is_approved', None)
        akt_file = validated_data.pop('akt_file', None)
        ilovalar = validated_data.pop('ilovalar', None)

        kelgan = KelganArizalar.objects.create(
            created_by=user,
            status="bajarilgan",
            is_approved=user.is_superuser,
            akt_file=akt_file,
            ilovalar=ilovalar,
            **validated_data
        )
        print("Validated data:", validated_data)

        # # Multi-image save
        # for img in images:
        #     KelganArizalarImage.objects.create(kelgan=kelgan, rasm=img)

        # Asosiy ariza statusini "bajarildi" ga o'zgartirish
        kelgan.ariza.status = "bajarilgan"
        kelgan.ariza.save()

        return kelgan

    
    
    
    def update(self, instance, validated_data):
        # images = validated_data.pop("rasmlar", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # if images:
        #     for img in images:
        #         KelganArizalarImage.objects.create(kelgan=instance, rasm=img)

        return instance













# serializers.py
class KelganArizaSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    sana = serializers.DateTimeField(format=None)
    akt_file = serializers.FileField(use_url=True)
    bildirgi = serializers.FileField(use_url=True, required=False)
    rasmlar = serializers.SerializerMethodField()

    class Meta:
        model = KelganArizalar
        fields = [
            "id",
            "comment",
            "status",
            "created_by",
            "is_approved",
            "sana",
            "akt_file",
            "ilovalar",
            "bildirgi",
            "rasmlar"
        ]

    def get_created_by(self, obj):
        user = obj.created_by
        return user.get_full_name() or user.username if user else None
    
    def get_rasmlar(self, obj):
        request = self.context.get('request')
        return [
            request.build_absolute_uri(img.rasm.url) 
            for img in obj.rasmlar.all()
        ]


class ArizaYuborishWithKelganSerializer(ArizaYuborishSerializer):
    kelganlar = KelganArizaSerializer(many=True, read_only=True)
    parol = serializers.CharField(write_only=True)
    bildirgi = serializers.FileField(read_only=True)
    rasmlar = ArizaImagesSerializer(many=True, read_only=True)
    tuzilma = serializers.CharField(source="tuzilma.tuzilma_nomi", read_only=True)
    kim_tomonidan = serializers.SerializerMethodField()
    created_by = serializers.CharField(source="created_by.username", read_only=True)
    turi = serializers.CharField(read_only=True)
    ijro_muddati = serializers.DateField(read_only=True)

    class Meta:
        model = ArizaYuborish
        fields = [
            "id", "comment", "sana", "parol", "status", "is_approved",
            "tuzilma","extra_comment", "kim_tomonidan", "created_by", "kelganlar", "rasmlar", "bildirgi", "turi", "ijro_muddati"
        ]

    def get_kim_tomonidan(self, obj):
        user = obj.kim_tomonidan
        if not user:
            return None
        
        request = self.context.get('request')

        # Foydalanuvchining rasmi va nomini aniqlash
        if user.tarkibiy_tuzilma:
            name = user.tarkibiy_tuzilma.tuzilma_nomi
            photo_url = request.build_absolute_uri(user.tarkibiy_tuzilma.photo.url) if (user.tarkibiy_tuzilma.photo and request) else None
        elif user.bekat_nomi:
            name = user.bekat_nomi.bekat_nomi
            photo_url = request.build_absolute_uri(user.bekat_nomi.photo.url) if (user.bekat_nomi.photo and request) else None
        else:
            name = user.username
            photo_url = request.build_absolute_uri(user.photo.url) if (user.photo and request) else None

        return {
            "name": name,
            "photo": photo_url
        }






class ArizaStatusUpdateSerializer(serializers.Serializer):
    ariza = serializers.PrimaryKeyRelatedField(
        queryset=ArizaYuborish.objects.all()
    )

    holat = serializers.ChoiceField(
        choices=ArizaYuborish.STATUS
    )

    comment = serializers.CharField(required=False, allow_blank=True)
    akt_file = serializers.FileField(required=False)
    ilovalar = serializers.FileField(required=False)
    # parol = serializers.CharField(write_only=True)

    # def validate_parol(self, value):
    #     user = self.context['request'].user
    #     if not user.check_password(value):
    #         raise serializers.ValidationError("Parol noto'g'ri!")
    #     return value



    def validate(self, data):
        ariza_obj = data['ariza']
        
        if ariza_obj.status in ['bajarilgan']:
            raise serializers.ValidationError(
                "Bu ariza yakunlangan, statusni qayta o'zgartirish mumkin emas!"
            )
        return data




        
        
    

class PPRTuriSerializer(serializers.ModelSerializer):
    
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    
    
    class Meta:
        model = PPRTuri
        fields = ["id", "nomi", "qisqachanomi", "davriyligi", "vaqti", "comment", "file", "kimlar_qiladi", "user", "tarkibiy_tuzilma", "bekat", "bolim"]
        read_only_fields = ['tarkibiy_tuzilma', 'bekat', 'bolim']
        
        extra_kwargs = {
            'nomi': {'required': True},
            'qisqachanomi': {'required': True},
            'davriyligi': {'required': True},
            'vaqti': {'required': True},
            'comment': {'required': True},
            'file': {'required': False},
            'kimlar_qiladi': {'required': True},
        }
        
        
    
    def update(self, instance, validated_data):
        # Fayl mavjud bo'lmasa yoki None bo'lsa, eski faylni saqlaymiz
        file_value = validated_data.get('file', instance.file)
        if file_value is None:
            validated_data['file'] = instance.file

        return super().update(instance, validated_data)

        
    # def create(self, validated_data):
    #         user = self.context['request'].user
    #         validated_data['user'] = user
    #         return super().create(validated_data)







class ObyektLocationSerializer(serializers.ModelSerializer):
    obyekt_name = serializers.CharField(
        source='obyekt.obyekt_nomi',
        read_only=True
    )

    class Meta:
        model = ObyektLocation
        fields = ['id', 'obyekt', 'obyekt_name', 'lat', 'lng', 'created_at']
        extra_kwargs = {
            'obyekt': {'required': True}  
        }

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')

        # PUT/PATCH da obyekt umuman o‘chadi
        if request and request.method in ['PUT', 'PATCH']:
            fields.pop('obyekt')

        return fields
        
        
        
        
class ObyektNomiSerializer(serializers.ModelSerializer):
    location = ObyektLocationSerializer(read_only=True)
    
    
    class Meta:
        model = ObyektNomi
        fields = ['id', 'obyekt_nomi', 'toliq_nomi', 'location', 'tarkibiy_tuzilma', 'bekat', 'bolim']
        read_only_fields = ['tarkibiy_tuzilma', 'bekat', 'bolim']





class PPRYillikJadvalSerializer(serializers.ModelSerializer):
    oylar = serializers.MultipleChoiceField(choices=PPRYillikJadval.OY_CHOICES)

    obyekt = serializers.PrimaryKeyRelatedField(
        queryset=ObyektNomi.objects.all(), 
        many=True
    )
    
    obyekt_details = serializers.SerializerMethodField(read_only=True)
    ppr_turi_name = serializers.CharField(source='ppr_turi.qisqachanomi', read_only=True)
    tarkibiy_tuzilma_name = serializers.CharField(
        source="tarkibiy_tuzilma.tuzilma_nomi", read_only=True
    )
    bolim_name = serializers.CharField(source="bolim.nomi", read_only=True)
    bekat_name = serializers.CharField(source="bekat.nomi", read_only=True)
    
    class Meta:
        model = PPRYillikJadval
        fields = [
            'id', 'yil', 'oylar',
            'obyekt', 'obyekt_details',
            'ppr_turi', 'ppr_turi_name',
            'tarkibiy_tuzilma', 'tarkibiy_tuzilma_name',
            'bekat', 'bekat_name',
            'bolim', 'bolim_name',
            'comment', 'status'
        ]
        read_only_fields = ['tarkibiy_tuzilma', 'bekat', 'bolim', 'created_by']
        
    def get_tarkibiy_tuzilma_names(self, obj):
        return [t.tuzilma_nomi for t in obj.tarkibiy_tuzilma.all()]

    def get_obyekt_details(self, obj):
        # Front-endda obyekt nomlarini ko'rsatish uchun
        return [{"id": o.id, "nomi": o.obyekt_nomi} for o in obj.obyekt.all()]
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user and not user.is_anonymous:
            # 1. PPR TURI Dropdowni
            if user.is_superuser or user.is_admin():
                self.fields['ppr_turi'].queryset = PPRTuri.objects.all()
            else:
                self.fields['ppr_turi'].queryset = PPRTuri.objects.filter(user=user)

            if user.is_bolim():
                if user.tarkibiy_tuzilma:
                    self.fields['obyekt'].queryset = ObyektNomi.objects.filter(
                        tarkibiy_tuzilma=user.tarkibiy_tuzilma
                    ).order_by('obyekt_nomi')
            else:
                self.fields['obyekt'].queryset = ObyektNomi.objects.all().order_by('obyekt_nomi')
    
    
    def validate_oylar(self, value):
        if not value:
            raise serializers.ValidationError(
                "Kamida bitta oy tanlanishi shart."
            )
      
        return list(value)


    def create(self, validated_data):
        obyektlar = validated_data.pop('obyekt', [])

        instance = PPRYillikJadval.objects.create(**validated_data)

        if obyektlar:
            instance.obyekt.set(obyektlar)

        return instance


        

    def update(self, instance, validated_data):
        obyektlar = validated_data.pop('obyekt', None)
        
        # Oddiy fieldlarni yangilash
        instance = super().update(instance, validated_data)
        
        # ManyToMany fieldni yangilash
        if obyektlar is not None:
            instance.obyekt.set(obyektlar)
            
        return instance

       


class PPRYillikYuborishSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPRYillikYuborish
        fields = ['yil']

    def create(self, validated_data):
        user = self.context['request'].user
        yil = validated_data['yil']
        
        # O'ziga tegishli jadvallarni topish
        jadvallar = PPRYillikJadval.objects.filter(
            created_by=user,
            yil=yil,
            status__in=['jarayonda', 'rad_etildi']
        )
        
        if not jadvallar.exists():
            raise serializers.ValidationError("Yuborish uchun jadvallar topilmadi!")

        jadvallar.update(status='yuborildi')
        
        # Userning bo'lim kategoriyasini aniqlash (Bolim modelidan)
        bolim_profile = getattr(user, 'bolim_profile', None)
        if not bolim_profile:
            raise serializers.ValidationError("Sizda bo'lim profili mavjud emas!")

        return PPRYillikYuborish.objects.create(
            user=user,
            yil=yil,
            bolim_category=bolim_profile.bolim_category,
            tarkibiy_tuzilma=user.tarkibiy_tuzilma
        )

# Tasdiqlash tizimi
class PPRYillikTasdiqlashSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPRYillikTasdiqlash
        fields = ['yuborish_paketi', 'status', 'comment']

    def create(self, validated_data):
        user = self.context['request'].user
        paketi = validated_data['yuborish_paketi']
        status_choice = validated_data['status']

        jadvallar = PPRYillikJadval.objects.filter(
            yil=paketi.yil,
            bolim_category=paketi.bolim_category,
            tarkibiy_tuzilma=paketi.tarkibiy_tuzilma,
            status='yuborildi'
        )

        if status_choice == 'tasdiqlandi':
            jadvallar.update(status='tasdiqlandi', tasdiqlangan=True)
        else:
            jadvallar.update(status='rad_etildi')

        return PPRYillikTasdiqlash.objects.create(user=user, **validated_data)


class PPRBajarildiImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPRBajarildiImage
        fields = ['id', 'image']





class PPRBajarildiSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    images = PPRBajarildiImageSerializer(many=True, read_only=True)
    bajarilgan_obyektlar = serializers.PrimaryKeyRelatedField(
        queryset=ObyektNomi.objects.all(),
        many=True,
        required=False
    )
    foiz = serializers.SerializerMethodField()
    bajarilgan_obyektlar_nomi = serializers.StringRelatedField(source='bajarilgan_obyektlar', many=True, read_only=True)

    class Meta:
        model = PPRBajarildi
        fields = [
            'id', 'jadval', 'bajarilgan_obyektlar', 'bajarilgan_obyektlar_nomi', 
            'comment', 'file', 'foiz', 'created_at', 'images', 'user'
        ]
        
    
    
    
    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        jadval = attrs.get('jadval')

        if not jadval:
            raise serializers.ValidationError({"jadval": "Jadval majburiy"})

        # 1. Status tekshirish
        if jadval.status != "tasdiqlandi":
            raise serializers.ValidationError({
                "jadval": "Faqat tasdiqlangan jadval bajarilishi mumkin!"
            })

        # 2. BO'LIM TEKSHIRISH (Foydalanuvchi va Jadval bo'limi bir xilligini tekshiramiz)
        # created_by emas, bolim_category bo'yicha tekshiramiz
        user_bolim = getattr(user.bolim_profile, 'bolim_category', None)
        if user_bolim != jadval.bolim_category and not user.is_superuser:
            raise serializers.ValidationError({
                "jadval": "Siz boshqa bo‘limga tegishli jadvalni bajarolmaysiz!"
            })

        return attrs

        




    
    def get_foiz(self, obj):
        # Jadvaldagi jami obyektlar soni
        jami_count = obj.jadval.obyektlar.count()
        if jami_count == 0:
            return 0
        
        shu_stepdagi_soni = obj.bajarilgan_obyektlar.count()
        
        return round((shu_stepdagi_soni / jami_count) * 100, 2)

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        bajarilganlar_list = validated_data.pop('bajarilgan_obyektlar', [])
        jadval = validated_data['jadval']
        

        # 2. Faqat tasdiqlangan bo‘lsa bajarish mumkin
        if jadval.status != "tasdiqlandi":
            raise serializers.ValidationError({
                "jadval": "Faqat tasdiqlangan jadval bajarilishi mumkin!"
            })

        # 3. Obyektlar tekshiruvi
        jadval_obyekt_ids = set(jadval.obyektlar.values_list('id', flat=True))
        tanlangan_ids = set(obj.id for obj in bajarilganlar_list)

        if not tanlangan_ids.issubset(jadval_obyekt_ids):
            raise serializers.ValidationError({
                "bajarilgan_obyektlar": "Tanlangan obyekt ushbu PPRga biriktirilmagan!"
            })
            
        
        
        
          
        oldin_bajarilgan_ids = set(
            PPRBajarildi.objects.filter(jadval=jadval)
            .values_list('bajarilgan_obyektlar', flat=True)
        )

        if tanlangan_ids.intersection(oldin_bajarilgan_ids):
            raise serializers.ValidationError({
                "bajarilgan_obyektlar": "Bu obyekt allaqachon bajarilgan!"
            })


        # 4. Saqlash
        instance = PPRBajarildi.objects.create(user=user, **validated_data)
        instance.bajarilgan_obyektlar.set(ObyektNomi.objects.filter(id__in=tanlangan_ids))
        
        
        images_data = request.FILES.getlist('images')
        for image_file in images_data:
            PPRBajarildiImage.objects.create(bajarildi=instance, image=image_file)

        # 5. Umumiy bajarilgan obyektlarni hisoblash
        barcha_bajarilgan_ids = set(
            PPRBajarildi.objects.filter(jadval=jadval)
            .values_list('bajarilgan_obyektlar__id', flat=True)
        )

        # jadvaldagi obyektlar bilan solishtirish
        jadval_obyekt_ids = set(jadval.obyektlar.values_list('id', flat=True))
        if jadval_obyekt_ids.issubset(barcha_bajarilgan_ids):
            jadval.status = "bajarildi"
            jadval.save(update_fields=["status"])

        return instance






class ObyektMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObyektNomi
        fields = ['id', 'obyekt_nomi']





class PPRJadvalSerializer(serializers.ModelSerializer):
    # Ko'p obyektlarni qabul qilish uchun PrimaryKeyRelatedField (M2M uchun)
    obyektlar = ObyektMiniSerializer(many=True, read_only=True)
    sana = serializers.DateField(required=True, allow_null=False)
    obyektlar_ids = serializers.PrimaryKeyRelatedField(
        queryset=ObyektNomi.objects.all(),
        many=True,
        write_only=True
    )
    ppr_turi = serializers.PrimaryKeyRelatedField(queryset=PPRTuri.objects.none()) 
    bolim_nomi = serializers.CharField(source='bolim_category.nomi', read_only=True)
    ppr_davriyligi = serializers.CharField(source='ppr_turi.davriyligi', read_only=True)
    ppr_turi_name = serializers.CharField(source='ppr_turi.qisqachanomi', read_only=True)
    muddat = serializers.BooleanField(read_only=True)
    steps = PPRBajarildiSerializer(source='bajarildilar', many=True, read_only=True)
    umumiy_foiz = serializers.SerializerMethodField()

    class Meta:
        model = PPRJadval
        fields = [
            'id', 'sana', 'obyektlar', 'obyektlar_ids', 'ppr_turi', 'bolim_category', 'bolim_nomi', 
            'ppr_turi_name', 'ppr_davriyligi', 'comment', 'status', 'muddat','umumiy_foiz', 'steps'
        ]
        read_only_fields = ['bolim_category', 'tarkibiy_tuzilma', 'bekat', 'bolim']

    
    
    def validate_sana(self, value):
        
        if value is None:
            raise serializers.ValidationError("Sana kiritilishi majburiy!")
        return value
    
    
    
    def validate(self, attrs):
        instance = self.instance
        if instance and instance.tasdiqlangan:
            raise serializers.ValidationError("Tasdiqlangan jadvalni tahrirlash taqiqlanadi!")
        return attrs

    def get_umumiy_foiz(self, obj):
        # BU YERDA HAMMA STEPLARNI YIG'INDISI HISOBLANADI
        jami_count = obj.obyektlar.count()
        if jami_count == 0: return 0
        
        # Barcha bajarilgan takrorlanmas IDlarni yig'amiz
        bajarilgan_ids = PPRBajarildi.objects.filter(
            jadval=obj
        ).values_list('bajarilgan_obyektlar', flat=True).distinct()
        
        # None-larni filtrlash
        bajarilgan_ids = [idx for idx in bajarilgan_ids if idx is not None]
        
        return round((len(set(bajarilgan_ids)) / jami_count) * 100, 2)
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user and not user.is_anonymous:
            # PPR TURI Filter
            if user.is_superuser or user.is_admin():
                self.fields['ppr_turi'].queryset = PPRTuri.objects.all()
            elif user.role == 'bolim':
                # Foydalanuvchining bo'lim kategoriyasini olamiz
                bolim_cat = getattr(user.bolim_profile, 'bolim_category', None)
                if bolim_cat:
                    
                    self.fields['ppr_turi'].queryset = PPRTuri.objects.filter(
                        user__bolim_profile__bolim_category=bolim_cat
                    ).distinct()
                else:
                    self.fields['ppr_turi'].queryset = PPRTuri.objects.none()
            else:
                # Boshqa rollar uchun (masalan rahbar) o'ziga tegishlisini ko'rsatish
                self.fields['ppr_turi'].queryset = PPRTuri.objects.filter(user=user)

            if user.is_bolim():
                if getattr(user, 'tarkibiy_tuzilma', None):
                    self.fields['obyektlar'].queryset = ObyektNomi.objects.filter(
                        tarkibiy_tuzilma=user.tarkibiy_tuzilma
                    ).order_by('obyekt_nomi')
            else:
                self.fields['obyektlar'].queryset = ObyektNomi.objects.all().order_by('obyekt_nomi')

    
    def create(self, validated_data):
        obyektlar_data = validated_data.pop('obyektlar_ids', [])
        user = self.context.get('request').user
        
        bolim_category = None
        if user.role == 'bolim':
            bolim_profile = getattr(user, 'bolim_profile', None)
            if bolim_profile and bolim_profile.bolim_category:
                bolim_category = bolim_profile.bolim_category
            else:
                raise serializers.ValidationError({"detail": "Sizda bo'lim biriktirilmagan!"})
        else:
            bolim_category = validated_data.get('bolim_category')

        instance = PPRJadval.objects.create(
            bolim_category=bolim_category,
            **validated_data
        )

        if obyektlar_data:
            instance.obyektlar.set(obyektlar_data)
    

    
        return instance        



            

class PPRYuborishMiniSerializer(serializers.ModelSerializer):
    oy_nomi = serializers.SerializerMethodField()

    OY_NOMLARI = {
        1: "Yanvar",
        2: "Fevral",
        3: "Mart",
        4: "Aprel",
        5: "May",
        6: "Iyun",
        7: "Iyul",
        8: "Avgust",
        9: "Sentabr",
        10: "Oktabr",
        11: "Noyabr",
        12: "Dekabr",
    }

    class Meta:
        model = PPRYuborish
        fields = ['id', 'yil', 'oy', 'oy_nomi']

    def get_oy_nomi(self, obj):
        return self.OY_NOMLARI.get(obj.oy)





class PPRTasdiqlashDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    yuborish_paketi = PPRYuborishMiniSerializer()

    class Meta:
        model = PPRTasdiqlash
        fields = [
            'id',
            'created_at',
            'user',
            'status',
            'comment',
            'yuborish_paketi'
        ]






# Yuborish Serializer
class PPRYuborishSerializer(serializers.ModelSerializer):
    oy_nomi = serializers.SerializerMethodField()
    yil = serializers.IntegerField(required=False)
    oy = serializers.IntegerField(required=False)
    OY_NOMLARI = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
        5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
        9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr",
    }

    class Meta:
        model = PPRYuborish
        fields = ['id', 'yil', 'oy', 'oy_nomi', 'status', 'comment']
        # PUT/PATCH so'rovida yil va oyni o'zgartirib bo'lmaydigan qilamiz
        extra_kwargs = {
            'yil': {'required': False},
            'oy': {'required': False},
            'is_active': {'read_only': True} 
        }
        read_only_fields = ['status']

    def get_oy_nomi(self, obj):
        return self.OY_NOMLARI.get(obj.oy)

    def create(self, validated_data):
        user = self.context['request'].user
        yil = validated_data['yil']
        oy = validated_data['oy']

        # Tekshirish: Bu oy uchun faqat aktiv paket bormi?
        existing_packet = PPRYuborish.objects.filter(
            yil=yil, oy=oy,
            bolim_category=user.bolim_profile.bolim_category,
            tarkibiy_tuzilma=user.tarkibiy_tuzilma,
            is_active=True
        ).first()

        if existing_packet:
            if existing_packet.status == 'tasdiqlandi':
                raise serializers.ValidationError("Bu oy uchun hisobot allaqachon tasdiqlangan!")
            raise serializers.ValidationError({
                "error": "Bu oy uchun paket mavjud.",
                "id": existing_packet.id,
                "status": existing_packet.status
            })

        # Jadvallarni 'yuborildi' holatiga o'tkazish
        jadvallar = PPRJadval.objects.filter(
            created_by=user, sana__year=yil, sana__month=oy,
            status__in=['jarayonda', 'rad_etildi']
        )

        if not jadvallar.exists():
            raise serializers.ValidationError("Yuborish uchun jadvallar topilmadi!")

        jadvallar.update(status='yuborildi')

        # Yangi paket yaratish (faqat aktiv)
        return PPRYuborish.objects.create(
            user=user,
            yil=yil,
            oy=oy,
            comment=validated_data.get('comment', ''),
            bolim_category=user.bolim_profile.bolim_category,
            tarkibiy_tuzilma=user.tarkibiy_tuzilma,
            status='yuborildi',
            is_active=True
        )

    def update(self, instance, validated_data):
        if instance.status == 'tasdiqlandi':
            raise serializers.ValidationError("Tasdiqlangan paketni qayta yuborib bo'lmaydi!")

        user = self.context['request'].user
        bolim = instance.bolim_category
        tuzilma = instance.tarkibiy_tuzilma
        yil = instance.yil
        oy = instance.oy

        with transaction.atomic():
            # 1️⃣ Eskisini inaktiv qilish
            instance.is_active = False
            instance.save()

            # 2️⃣ Yangi paket yaratish
            new_instance = PPRYuborish.objects.create(
                user=user,
                yil=yil,
                oy=oy,
                bolim_category=bolim,
                tarkibiy_tuzilma=tuzilma,
                status='yuborildi',
                comment=validated_data.get('comment', 'Qayta yuborildi'),
                is_active=True
            )

            # 3️⃣ Jadvallarni yangilash
            PPRJadval.objects.filter(
                bolim_category=bolim,
                tarkibiy_tuzilma=tuzilma,
                sana__year=yil,
                sana__month=oy
            ).update(status='yuborildi')

        return new_instance



class PPRTasdiqlashSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPRTasdiqlash
        fields = ['yuborish_paketi', 'status', 'comment']

    def validate(self, attrs):
        user = self.context['request'].user
        # Faqat Rahbar (is_tarkibiy) yoki Admin tasdiqlay oladi
        if not (user.is_tarkibiy() or user.is_superuser or user.is_admin()):
            raise serializers.ValidationError("Sizda tasdiqlash huquqi yo'q!")
        
        paketi = attrs['yuborish_paketi']
        # Rahbar faqat o'z tuzilmasiga kelgan paketni tasdiqlay oladi
        if user.is_tarkibiy() and paketi.tarkibiy_tuzilma != user.tarkibiy_tuzilma:
            raise serializers.ValidationError("Siz boshqa tuzilmaning paketini tasdiqlay olmaysiz!")
            
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        paketi = validated_data['yuborish_paketi']
        yangi_status = validated_data['status'] # 'tasdiqlandi' yoki 'rad_etildi'
        izoh = validated_data.get('comment', '')

        # 1. Paket statusini yangilash
        paketi.status = yangi_status
        paketi.save()

        # 2. Paket ichidagi jadvallar statusini yangilash
        from .models import PPRJadval
        jadvallar = PPRJadval.objects.filter(
            bolim_category=paketi.bolim_category,
            tarkibiy_tuzilma=paketi.tarkibiy_tuzilma,
            sana__year=paketi.yil, 
            sana__month=paketi.oy
        )
        
        if yangi_status == 'tasdiqlandi':
            jadvallar.update(status='tasdiqlandi', tasdiqlangan=True)
        else:
            jadvallar.update(status='rad_etildi')

        # 3. Tasdiqlash tarixini yangilash yoki yaratish (OneToOneField uchun)
        tasdiq_obj, created = PPRTasdiqlash.objects.update_or_create(
            yuborish_paketi=paketi,
            defaults={
                'user': user,
                'status': yangi_status,
                'comment': izoh
            }
        )

        return tasdiq_obj

   
   
   
          
class PPRYuborishStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    yil = serializers.IntegerField()
    oy = serializers.IntegerField()
    oy_nomi = serializers.SerializerMethodField()
    status = serializers.CharField()
    yaratuvchi_user = serializers.CharField()  
    yaratilgan_sana = serializers.ReadOnlyField()
    tasdiqlashlar = serializers.ListField()
    yuborish_id = serializers.IntegerField(allow_null=True)
    OY_NOMLARI = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel", 5: "May", 6: "Iyun",
        7: "Iyul", 8: "Avgust", 9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
    }

    def get_oy_nomi(self, obj):
        return self.OY_NOMLARI.get(obj['oy'])
    
    
    

    def get_oy_nomi(self, obj):
        return self.OY_NOMLARI.get(obj['oy'])




class PPRJarayondaOylikSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    yil = serializers.IntegerField()
    oy = serializers.IntegerField()
    oy_nomi = serializers.SerializerMethodField()
    status = serializers.CharField()
    yaratilgan_sana = serializers.DateField()

    OY_NOMLARI = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel", 5: "May", 6: "Iyun",
        7: "Iyul", 8: "Avgust", 9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
    }

    def get_oy_nomi(self, obj):
        return self.OY_NOMLARI.get(obj['oy'])




class PPRYillikBajarildiImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPRYillikBajarildiImage
        fields = ['id', 'image']


class PPRYillikBajarildiSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    images = PPRYillikBajarildiImageSerializer(many=True, read_only=True)
    # Oy fieldini read_only qilamiz, chunki uni jadvaldan olamiz
    oy = serializers.CharField(read_only=True)

    class Meta:
        model = PPRYillikBajarildi
        fields = ['id', 'jadval', 'oy', 'comment', 'file', 'created_at', 'images', 'user']

    def validate(self, attrs):
        user = self.context['request'].user
        jadval = attrs['jadval']

        # 1. Oy olish
        oy = jadval.oylar[0] if jadval.oylar else None
        if not oy:
            raise serializers.ValidationError("Jadvalda oy belgilanmagan!")

        # 2. Oy nomini raqamga aylantiramiz
        OY_MAP = {
            "Yanvar": 1, "Fevral": 2, "Mart": 3, "Aprel": 4,
            "May": 5, "Iyun": 6, "Iyul": 7, "Avgust": 8,
            "Sentabr": 9, "Oktabr": 10, "Noyabr": 11, "Dekabr": 12
        }

        oy_raqam = OY_MAP.get(oy)
        if not oy_raqam:
            raise serializers.ValidationError("Oy noto‘g‘ri.")

        # 3. Jadval yilini olamiz
        yil = jadval.yil.yil   # (senda Yil modeli bor edi)

        # 4. Oy boshlanish sanasi
        oy_boshlanish = timezone.datetime(yil, oy_raqam, 1).date()
        bugun = timezone.now().date()

        # 5. Agar oy hali kelmagan bo‘lsa → BLOCK
        if oy_boshlanish > bugun:
            raise serializers.ValidationError({
                "jadval": f"{oy} oyi hali boshlanmagan. Bu oy uchun bajarildi qilib bo‘lmaydi."
            })

        # 6. Bu jadval uchun oldin topshirilganmi?
        if PPRYillikBajarildi.objects.filter(jadval=jadval).exists():
            raise serializers.ValidationError({
                "jadval": "Bu jadval uchun allaqachon hisobot topshirilgan."
            })

        # 7. Oyni create uchun saqlab qo‘yamiz
        attrs['oy'] = oy
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        
        # 1. Yaratish
        bajarildi_obj = super().create(validated_data)
        
        # 2. Jadval statusini yangilash
        jadval = bajarildi_obj.jadval
        jadval.status = "bajarildi"
        jadval.save()
        
        return bajarildi_obj









# ppr/serializers.py
class NotificationSerializer(serializers.ModelSerializer):
    seen_usernames = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='username', source='seen_by'
    )
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'link_id', 'is_read', 'seen_usernames', 'created_at']

    def get_is_read(self, obj):
        user = self.context['request'].user
        return obj.seen_by.filter(id=user.id).exists()




class HujjatlarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hujjatlar
        fields = "__all__"



class HujjatShabloniSerializer(serializers.ModelSerializer):
    # O'qish uchun qulay format (nomini chiqaradi)
    tuzilma_nomi = serializers.CharField(source='tuzilma.tuzilma_nomi', read_only=True)
    yuklovchi_ismi = serializers.CharField(source='yuklovchi.username', read_only=True)

    class Meta:
        model = HujjatShabloni
        fields = [
            'id', 
            'nomi', 
            'file',           
            'tuzilma',        
            'tuzilma_nomi',    
            'yuklovchi_ismi',
            'created_at'
        ]
        read_only_fields = ['yuklovchi', 'created_at']
        
        




class TuzilmaDashboardSerializer(serializers.Serializer):
    tuzilma_nomi = serializers.CharField()
    rahbari = serializers.CharField() 
    bajarilgan_soni = serializers.IntegerField()
    umumiy_kelgan_soni = serializers.IntegerField()
    bajarish_foizi = serializers.SerializerMethodField()

    def get_bajarish_foizi(self, obj):
        if obj['umumiy_kelgan_soni'] == 0:
            return 0
        return round((obj['bajarilgan_soni'] / obj['umumiy_kelgan_soni']) * 100, 1)


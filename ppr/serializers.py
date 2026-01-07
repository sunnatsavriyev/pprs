from rest_framework import serializers
from .models import *
import os
import random
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
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
        "image/avif",                 # ✅ AVIF qo‘shildi
        "application/octet-stream",   # baʼzi brauzerlar
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
    bolim_nomi = serializers.CharField(required=False, source='bolim.bolim_nomi', read_only=True)
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


        elif instance.tarkibiy_tuzilma:
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
                rep["bolim_nomi"] = bolim.bolim_nomi
                rep["bolim_id"] = bolim.id
                rep["tarkibiy_tuzilma"] = bolim.tuzilma.tuzilma_nomi if bolim.tuzilma else None
                rep["tarkibiy_tuzilma_id"] = bolim.tuzilma.id




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
        if hasattr(instance, "bolim_profile") and instance.bolim_profile:
            return instance.bolim_profile.bolim_nomi
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




class BolimUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, default="1234")
    tuzilma_nomi = serializers.CharField(source="tuzilma.tuzilma_nomi", read_only=True)

    class Meta:
        model = Bolim
        fields = [
            "id", "tuzilma", "tuzilma_nomi", "bolim_nomi",
            "username", "password",
            "faoliyati", "rahbari", "photo", "email",
            "birth_date", "passport_seriya", "status", "created_at"
        ]
        read_only_fields = ["created_at"]

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        username = validated_data.pop("username")
        password = validated_data.pop("password")

        # -------- TUZILMA ANIQLASH --------
        if user.role == "tarkibiy":
            tuzilma = user.tarkibiy_tuzilma
            if not tuzilma:
                raise ValidationError({"tuzilma": "Sizga tuzilma biriktirilmagan"})

            # ❗ xavfsizlik uchun
            validated_data.pop("tuzilma", None)

        elif user.role == "admin" or user.is_superuser:
            tuzilma = validated_data.pop("tuzilma", None)
            if not tuzilma:
                raise ValidationError({"tuzilma": "Admin uchun tuzilma majburiy"})

        else:
            raise PermissionDenied("Bo‘lim yaratishga ruxsatingiz yo‘q")

        # -------- USER YARATISH --------
        new_user = CustomUser.objects.create_user(
            username=username,
            password=password,
            role="bolim",
            tarkibiy_tuzilma=tuzilma
        )
        new_user._raw_password = password
        new_user.save()

        # -------- BO‘LIM YARATISH --------
        bolim = Bolim.objects.create(
            user=new_user,
            tuzilma=tuzilma,
            created_by=user,
            **validated_data
        )

        return bolim





class ArizaImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArizaYuborishImage
        fields = ["id","rasm"]




class StepSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    comment = serializers.CharField()
    status = serializers.CharField()
    created_by = serializers.CharField(allow_null=True)
    is_approved = serializers.BooleanField()
    sana = serializers.DateTimeField()




class ArizaYuborishSerializer(serializers.ModelSerializer):
    parol = serializers.CharField(write_only=True)
    photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    rasmlar = ArizaImagesSerializer(many=True, read_only=True)
    tuzilmalar = serializers.PrimaryKeyRelatedField(
        queryset=TarkibiyTuzilma.objects.all(),
        many=True
    )
    bildirgi = serializers.FileField(required=False)
    tuzilma_nomlari = serializers.SerializerMethodField()
    # Read-only fields
    kim_tomonidan = serializers.SerializerMethodField()
    created_by = serializers.CharField(source="created_by.username", read_only=True)
    sana = serializers.DateTimeField(
        format="%Y-%m-%d",
        read_only=True
    )
    steplar = serializers.SerializerMethodField()

    class Meta:
        model = ArizaYuborish
        fields = [
            "id", "comment", "parol", "tuzilmalar",'tuzilma_nomlari', "kim_tomonidan", "created_by", "status",'turi','ijro_muddati', "is_approved", "photos", "rasmlar", "bildirgi", "steplar","qayta_yuklandi", "sana", 
        ]
        read_only_fields = ["kim_tomonidan", "created_by", "status", "is_approved", 'tuzilmalar', 'steplar']

    
    def get_tuzilma_nomlari(self, obj):
        return [t.tuzilma_nomi for t in obj.tuzilmalar.all()]
    
    
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

        # 1. Eng birinchi (asl) ariza stepi
        steps.append({
            "id": obj.id,
            "comment": obj.comment, # Asl komment
            "status": "yaratildi", 
            "created_by": obj.created_by.username if obj.created_by else None,
            "is_approved": obj.is_approved,
            "sana": obj.sana,
            "akt_file": None,
            "ilovalar": request.build_absolute_uri(obj.bildirgi.url) if obj.bildirgi else None,
        })

        
        for step in obj.kelganlar.all().order_by('sana'):
            steps.append({
                "id": step.id,
                "comment": step.comment,
                "status": step.status,
                "created_by": step.created_by.username if step.created_by else None,
                "is_approved": step.is_approved,
                "sana": step.sana,
                "akt_file": request.build_absolute_uri(step.akt_file.url) if step.akt_file else None,
                "ilovalar": request.build_absolute_uri(step.ilovalar.url) if step.ilovalar else None,
            })

        return steps
    
    
    
    def validate_parol(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Parol noto'g'ri!")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        tuzilmalar = validated_data.pop("tuzilmalar", [])
        photos = validated_data.pop("photos", [])
        
        # 1. Arizani yaratish
        ariza = ArizaYuborish.objects.create(
            comment=validated_data["comment"],
            parol=validated_data["parol"],
            turi=validated_data.get("turi", "ijro"),
            ijro_muddati=validated_data.get("ijro_muddati") if validated_data.get("turi") == "ijro" else None,
            created_by=user,
            kim_tomonidan=user,
            bildirgi=validated_data.get("bildirgi"),
            status="jarayonda",
            is_approved=user.is_superuser
        )

        # 2. Tanlangan bir nechta tuzilmalarni bog'lash
        ariza.tuzilmalar.set(tuzilmalar)

        # 3. Rasmlarni saqlash
        for img in photos:
            ArizaYuborishImage.objects.create(ariza=ariza, rasm=img)

        return ariza
    
    
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        
        # 1. Frontenddan kelayotgan yangi ma'lumotlarni olish
        new_comment = validated_data.get("comment")
        new_photos = validated_data.pop("photos", None)
        new_bildirgi = validated_data.get("bildirgi", None)

        # 2. Asosiy arizaning statusini va "qayta_yuklandi" belgisini yangilaymiz
        instance.status = "jarayonda"
        instance.qayta_yuklandi = True
        
        # Agar yangi bildirgi fayli yuborilgan bo'lsa, asosiy modeldagini yangilaymiz
        if new_bildirgi:
            instance.bildirgi = new_bildirgi
        
        instance.save()

        # 3. Rasmlar kelsa, eskisini o'chirib yangisini yuklaymiz (Asosiy ariza uchun)
        if new_photos is not None:
            instance.rasmlar.all().delete()
            for img in new_photos:
                ArizaYuborishImage.objects.create(ariza=instance, rasm=img)

        # 4. YANGI STEP YARATISH (Tarixda qolishi uchun)
        # Bu foydalanuvchi yuborgan yangi "Tahrir" ma'lumotlari
        KelganArizalar.objects.create(
            ariza=instance,
            created_by=user,
            comment=new_comment or "Ma'lumotlar qayta yuklandi",
            status="jarayonda",
            is_approved=user.is_superuser,
            # Agar bildirgi bo'lsa ilovalar qismiga qo'shamiz
            ilovalar=new_bildirgi if new_bildirgi else None 
        )

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
    sana = serializers.DateTimeField(format="%d-%m-%Y")
    akt_file = serializers.FileField(use_url=True)

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
            "ilovalar"
        ]

    def get_created_by(self, obj):
        user = obj.created_by
        return user.get_full_name() or user.username if user else None


class ArizaYuborishWithKelganSerializer(ArizaYuborishSerializer):
    kelganlar = KelganArizaSerializer(many=True, read_only=True)
    parol = serializers.CharField(write_only=True)
    bildirgi = serializers.FileField(read_only=True)
    rasmlar = ArizaImagesSerializer(many=True, read_only=True)
    tuzilma = serializers.CharField(source="tuzilma.tuzilma_nomi", read_only=True)
    kim_tomonidan = serializers.SerializerMethodField()
    created_by = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = ArizaYuborish
        fields = [
            "id", "comment", "sana", "parol", "status", "is_approved",
            "tuzilma", "kim_tomonidan", "created_by", "kelganlar", "rasmlar", "bildirgi"
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
        choices=ArizaYuborish.STATUS,
        label="Statusni tanlang"
    )

    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        label="return comment"
    )




        
        
    

class PPRTuriSerializer(serializers.ModelSerializer):
    
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    
    
    class Meta:
        model = PPRTuri
        fields = "id","nomi", "qisqachanomi", "davriyligi", "vaqti", "comment", "file", "kimlar_qiladi",  "user"
        
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
        fields = ['id', 'obyekt_nomi', 'toliq_nomi', 'location']








class PPRJadvalSerializer(serializers.ModelSerializer):
    obyekt = serializers.PrimaryKeyRelatedField(queryset=ObyektNomi.objects.all())
    ppr_turi = serializers.PrimaryKeyRelatedField(queryset=PPRTuri.objects.none())
    ppr_davriyligi = serializers.CharField(source='ppr_turi.davriyligi', read_only=True)
    obyekt_name = serializers.CharField(source='obyekt.obyekt_nomi', read_only=True)
    ppr_turi_name = serializers.CharField(source='ppr_turi.qisqachanomi', read_only=True)
    class Meta:
        model = PPRJadval
        fields = ['id', 'oy','boshlash_sanasi', 'yakunlash_sanasi', 'obyekt', 'ppr_turi', 'obyekt_name', 'ppr_turi_name', 'ppr_davriyligi','comment', ]

    
    
    
    def validate(self, attrs):
        oy = attrs.get("oy")
        start = attrs.get("boshlash_sanasi")
        end = attrs.get("yakunlash_sanasi")

        # Oy va sana bir vaqtda bo‘lmasin
        if oy and (start or end):
            raise serializers.ValidationError(
                "Agar oy tanlansa, boshlash/yakunlash sanasi kiritilmaydi."
            )

        if (start or end) and oy:
            raise serializers.ValidationError(
                "Agar sana tanlansa, oy tanlanmaydi."
            )

        #  Sana to‘liq bo‘lishi shart
        if start and not end:
            raise serializers.ValidationError(
                "Yakunlash sanasi majburiy."
            )

        if end and not start:
            raise serializers.ValidationError(
                "Boshlash sanasi majburiy."
            )

        #  Sana mantiqi
        if start and end and start > end:
            raise serializers.ValidationError(
                "Boshlash sanasi yakunlash sanasidan katta bo‘lmasligi kerak."
            )

        return attrs
    
    
    
    
    def update(self, instance, validated_data):
        if instance.tasdiqlangan:
            raise serializers.ValidationError("Tasdiqlangan jadvalni tahrirlash mumkin emas!")
        return super().update(instance, validated_data)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not user or user.is_anonymous:
            self.fields['ppr_turi'].queryset = PPRTuri.objects.none()

        elif user.is_superuser or getattr(user, 'role', None) == "admin":
            self.fields['ppr_turi'].queryset = PPRTuri.objects.all()

        else:
            self.fields['ppr_turi'].queryset = PPRTuri.objects.filter(user=user)
            
            

class PPRJadvalYakunlashSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPRYakunlash
        fields = ['id', 'yakunlash']
            

class PPRBajarildiSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    # Jadvalni faqat ID sifatida saqlash uchun
    jadval = serializers.PrimaryKeyRelatedField(
        queryset=PPRJadval.objects.filter(boshlash_sanasi__isnull=False)
    )

    # Frontend uchun label
    jadval_label = serializers.SerializerMethodField()

    # GET qilganda qo‘shimcha info
    ppr_turi_name = serializers.CharField(source='jadval.ppr_turi.qisqachanomi', read_only=True)
    obyekt_name = serializers.CharField(source='jadval.obyekt.obyekt_nomi', read_only=True)
    boshlash_sanasi = serializers.DateField(source='jadval.boshlash_sanasi', read_only=True)
    yakunlash_sanasi = serializers.DateField(source='jadval.yakunlash_sanasi', read_only=True)
    ppr_davriyligi = serializers.CharField(source='jadval.ppr_turi.davriyligi', read_only=True)

    class Meta:
        model = PPRBajarildi
        fields = [
            'id', 'user', 'jadval', 'jadval_label',
            'ppr_turi_name', 'obyekt_name', 'boshlash_sanasi', 'yakunlash_sanasi', 'ppr_davriyligi',
            'comment', 'file', 'images', 'created_at', 'created_time'
        ]

    def get_jadval_label(self, obj):
        jadval = getattr(obj, 'jadval', None)
        if jadval:
            return f"{jadval.ppr_turi.qisqachanomi} - {jadval.obyekt.obyekt_nomi} ({jadval.boshlash_sanasi})"
        return ""


    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)






class HujjatlarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hujjatlar
        fields = "__all__"


class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = "__all__"

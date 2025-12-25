from rest_framework import serializers
from .models import *
import os
import random

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
    faoliyati = serializers.CharField(required=False, allow_blank=True)
    rahbari = serializers.CharField(required=False)
    email = serializers.EmailField(required=False, allow_null=True)
    birth_date = serializers.DateField(required=False, allow_null=True, input_formats=['%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d'],)
    photo = serializers.ImageField(required=False, allow_null=True)
    passport_seriya = serializers.CharField(required=False)
    status = serializers.BooleanField(required=False)
    password = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = [
            "id", "username", "password", "role",
            "tarkibiy_tuzilma", "bekat_nomi",
            "tuzilma_nomi", "faoliyati", "rahbari",
            "email", "birth_date",
            "passport_seriya", "status", "photo"
        ]
        extra_kwargs = {
            "tarkibiy_tuzilma": {"read_only": True},
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request")  # request-ni olish

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

        elif instance.tarkibiy_tuzilma:
            rep["status"] = instance.tarkibiy_tuzilma.status
            rep["faoliyati"] = instance.tarkibiy_tuzilma.faoliyati
            if instance.tarkibiy_tuzilma.photo:
                rep["photo"] = request.build_absolute_uri(instance.tarkibiy_tuzilma.photo.url)
            else:
                rep["photo"] = None
            rep["tarkibiy_tuzilma"] = instance.tarkibiy_tuzilma.tuzilma_nomi 
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
            rep["birth_date"] = instance.birth_date.strftime("%d-%m-%Y") if instance.birth_date else None
            rep["passport_seriya"] = instance.passport_seriya

        # password qismi shunchaki
        show_password = False
        if request:
            if request.user.is_admin() or request.user.is_superuser:
                show_password = True
            elif request.user.id == instance.id:
                show_password = True

        if show_password:
            rep["password"] = getattr(instance, "_raw_password", None)
        else:
            rep["password"] = None  # yulduzcha ko'rsatmasdan

        return rep





    # ---------- Validatsiya ----------
    def validate(self, attrs):
        role = attrs.get("role", getattr(self.instance, "role", None))

        if role == "tarkibiy":
            required_fields = [ "faoliyati", "rahbari", "passport_seriya"]
            for f in required_fields:
                if not attrs.get(f):
                    raise serializers.ValidationError({f: "Majburiy maydon"})

        if role == "bekat" and not attrs.get("bekat_nomi"):
            raise serializers.ValidationError({"bekat_nomi": "Bekat tanlanishi shart!"})

        return attrs

    # ---------- Create ----------
    def create(self, validated_data):
        raw_password = validated_data.get("password", "1234")
        role = validated_data["role"]
        uploaded_photo = validated_data.pop("photo", None)

        # Tarkibiy tuzilma yaratish
        tuzilma = None
        if role == "tarkibiy":
            tuzilma = TarkibiyTuzilma.objects.create(
                tuzilma_nomi=validated_data["tuzilma_nomi"],
                faoliyati=validated_data["faoliyati"],
                rahbari=validated_data["rahbari"],
                passport_seriya=validated_data["passport_seriya"],
                status=validated_data.get("status", False),
                is_pending=True,
                photo=uploaded_photo,
                email=validated_data.get("email"),
                birth_date=validated_data.get("birth_date"),
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

        if role == "bekat":
            bekat_value = validated_data.get("bekat_nomi")
            if isinstance(bekat_value, str):
                bekat_obj = Bekat.objects.filter(bekat_nomi=bekat_value).first()
                if bekat_obj:
                    # mavjud bo'lsa, faqat kerakli maydonlarni yangilash
                    bekat_obj.faoliyati = validated_data.get("faoliyati", bekat_obj.faoliyati)
                    bekat_obj.rahbari = validated_data.get("rahbari", bekat_obj.rahbari)
                    bekat_obj.passport_seriya = validated_data.get("passport_seriya", bekat_obj.passport_seriya)
                    bekat_obj.status = validated_data.get("status", bekat_obj.status)
                    bekat_obj.email = validated_data.get("email", bekat_obj.email)
                    bekat_obj.birth_date = validated_data.get("birth_date", bekat_obj.birth_date)
                    bekat_obj.created_by = self.context["request"].user
                    if uploaded_photo is not None:
                        bekat_obj.photo = uploaded_photo
                    bekat_obj.save()
                else:
                    # yangi yaratish
                    bekat_obj = Bekat.objects.create(
                        bekat_nomi=bekat_value,
                        faoliyati=validated_data.get("faoliyati", ""),
                        rahbari=validated_data.get("rahbari", ""),
                        passport_seriya=generate_unique_passport(),
                        status=validated_data.get("status", False),
                        photo=uploaded_photo,
                        email=validated_data.get("email"),
                        birth_date=validated_data.get("birth_date"),
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
    tuzilma = serializers.PrimaryKeyRelatedField(
        queryset=TarkibiyTuzilma.objects.all()
    )
    bildirgi = serializers.FileField(required=False)
    tuzilma_nomi = serializers.CharField(
        source="tuzilma.tuzilma_nomi",
        read_only=True
    )
    # Read-only fields
    kim_tomonidan = serializers.SerializerMethodField()
    created_by = serializers.CharField(source="created_by.username", read_only=True)
    
    steplar = serializers.SerializerMethodField()

    class Meta:
        model = ArizaYuborish
        fields = [
            "id", "comment", "parol", "tuzilma",'tuzilma_nomi', "kim_tomonidan", "created_by", "status", "is_approved", "photos", "rasmlar", "bildirgi", "steplar","qayta_yuklandi", 
        ]
        read_only_fields = ["kim_tomonidan", "created_by", "status", "is_approved", 'tuzilma', 'steplar']

    def get_kim_tomonidan(self, obj):
        user = obj.kim_tomonidan
        if not user:
            return None
        # Tarkibiy tuzilma yoki bekat nomini tekshirish
        if user.tarkibiy_tuzilma:
            return user.tarkibiy_tuzilma.tuzilma_nomi
        elif user.bekat_nomi:
            return user.bekat_nomi.bekat_nomi
        return user.username

    
    
    def validate_photos(self, photos):
        for img in photos:
            validate_image_format(img)
        return photos

    
    def get_steplar(self, obj):

        request = self.context.get('request')
        steps = []

        # 1. Asosiy ariza step
        steps.append({
            "id": obj.id,
            "comment": obj.comment,
            "status": obj.status,
            "created_by": obj.created_by.username if obj.created_by else None,
            "is_approved": obj.is_approved,
            "sana": obj.sana,
            "akt_file": None,
            "ilovalar": None,
        })

        # 2. KelganArizalar steplari
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
        photos = validated_data.pop("photos", [])

        ariza = ArizaYuborish.objects.create(
            tuzilma=validated_data["tuzilma"],
            comment=validated_data["comment"],
            parol=validated_data["parol"],
            created_by=user,
            bildirgi=validated_data.get("bildirgi"),
            status="jarayonda",
            kim_tomonidan=user,  # user ni qo'yamiz, get_kim_tomonidan orqali tuzilma/bekat chiqariladi
            is_approved=user.is_superuser
        )

   
        for img in photos:
            ArizaYuborishImage.objects.create(ariza=ariza, rasm=img)

        return ariza
    
    
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        new_bildirgi = validated_data.get("bildirgi", None)
        photos = validated_data.pop("photos", None)
        comment = validated_data.get("comment", "")

        # Agar status "qaytarildi" bo‘lsa
        if validated_data.get("status") == "qaytarildi":
            instance.status = "jarayonda"  # boshlab jarayonda qilib qo‘yish mumkin
            instance.qayta_yuklandi = False
            instance.save()
            KelganArizalar.objects.create(
                ariza=instance,
                created_by=user,
                comment=comment or "Qaytarildi",
                status="qaytarildi",
                is_approved=user.is_superuser
            )
        else:
            # status boshqa bo‘lsa yangilash
            instance.status = "jarayonda"
            for attr, value in validated_data.items():
                if attr not in ["status", "photos", "bildirgi"]:
                    setattr(instance, attr, value)
            instance.save()

            if photos is not None:
                instance.rasmlar.all().delete()
                for img in photos:
                    ArizaYuborishImage.objects.create(ariza=instance, rasm=img)
                instance.qayta_yuklandi = True

            if new_bildirgi:
                instance.bildirgi = new_bildirgi
                KelganArizalar.objects.create(
                    ariza=instance,
                    created_by=user,
                    comment="Bildirgi qayta yuklandi",
                    status="jarayonda",
                    is_approved=user.is_superuser
                )
                instance.qayta_yuklandi = True

            instance.save()

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
        if user.tarkibiy_tuzilma:
            return user.tarkibiy_tuzilma.tuzilma_nomi
        elif user.bekat_nomi:
            return user.bekat_nomi.bekat_nomi
        return user.username
    
    
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
        if user.tarkibiy_tuzilma:
            return user.tarkibiy_tuzilma.tuzilma_nomi
        elif user.bekat_nomi:
            return user.bekat_nomi.bekat_nomi
        return user.username






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
        fields = "__all__"
        
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
    ppr_turi_name = serializers.CharField(source='ppr_turi.nomi', read_only=True)
    class Meta:
        model = PPRJadval
        fields = ['id', 'oy','boshlash_sanasi', 'yakunlash_sanasi', 'obyekt', 'ppr_turi', 'obyekt_name', 'ppr_turi_name', 'ppr_davriyligi','comment', ]

    
    
    
    def validate(self, attrs):
        oy = attrs.get("oy")
        start = attrs.get("boshlash_sanasi")
        end = attrs.get("yakunlash_sanasi")

        # ❌ Oy va sana bir vaqtda bo‘lmasin
        if oy and (start or end):
            raise serializers.ValidationError(
                "Agar oy tanlansa, boshlash/yakunlash sanasi kiritilmaydi."
            )

        if (start or end) and oy:
            raise serializers.ValidationError(
                "Agar sana tanlansa, oy tanlanmaydi."
            )

        # ❌ Sana to‘liq bo‘lishi shart
        if start and not end:
            raise serializers.ValidationError(
                "Yakunlash sanasi majburiy."
            )

        if end and not start:
            raise serializers.ValidationError(
                "Boshlash sanasi majburiy."
            )

        # ❌ Sana mantiqi
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
            

class HujjatlarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hujjatlar
        fields = "__all__"


class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = "__all__"

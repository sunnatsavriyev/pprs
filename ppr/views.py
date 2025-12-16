from rest_framework import viewsets,filters
from .models import *
from .serializers import *
from rest_framework import permissions, status
from rest_framework.response import Response
from django.db.models import Prefetch
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from .pagination import CustomPagination
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from datetime import datetime



class UserTuzilmaViewSet(viewsets.ModelViewSet):
    serializer_class = UserTuzilmaSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.is_admin():
            # Adminlar va superuser barcha foydalanuvchilarni ko‘radi
            return CustomUser.objects.all().order_by('-id')
        else:
            # Foydalanuvchi faqat o‘zini ko‘radi
            return CustomUser.objects.filter(id=user.id)

    # CREATE – faqat admin/superuser
    def perform_create(self, serializer):
        user = self.request.user
        if not (user.is_superuser or user.is_admin()):
            raise PermissionDenied("Faqat admin foydalanuvchi yaratishi mumkin.")
        serializer.save()

    # ---------------- UPDATE ----------------
    def perform_update(self, serializer):
        user = self.request.user
        obj = self.get_object()

        # ADMIN yoki SUPERADMIN → barchani o‘zgartira oladi
        if user.is_superuser or user.is_admin():
            serializer.save()
            return

        # Oddiy user → faqat o‘zini update qila oladi
        if user.id != obj.id:
            raise PermissionDenied("Siz faqat o‘zingizni o‘zgartira olasiz.")

        serializer.save()

    # ---------------- DELETE ----------------
    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_superuser or user.is_admin()):
            raise PermissionDenied("Faqat admin foydalanuvchi o‘chirishi mumkin.")
        instance.delete()





class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserTuzilmaSerializer(
            request.user,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)





class TuzilmaNomiViewSet(viewsets.ModelViewSet):
    queryset = TarkibiyTuzilma.objects.filter(status=True)
    serializer_class = TuzilmaSerializers

    def get_queryset(self):
        return TarkibiyTuzilma.objects.filter(status=True)




class ArizaYuborishFilter(django_filters.FilterSet):
    # Tuzilma bo‘yicha filter (ID orqali)
    tuzilma = django_filters.NumberFilter(field_name='tuzilma_id')

    # Kim tomonidan (ID orqali)
    kim_tomonidan = django_filters.NumberFilter(field_name='kim_tomonidan_id')

    # Created by (ID orqali)
    created_by = django_filters.NumberFilter(field_name='created_by_id')

    # Tuzilma nomi orqali filter (TEXT)
    tuzilma_nomi = django_filters.CharFilter(
        field_name='tuzilma__tuzilma_nomi',
        lookup_expr='icontains'
    )

    class Meta:
        model = ArizaYuborish
        fields = [
            'status',
            'is_approved',
            'tuzilma',
            'kim_tomonidan',
            'created_by',
            'tuzilma_nomi'
        ]





class ArizaYuborishViewSet(viewsets.ModelViewSet):
    queryset = ArizaYuborish.objects.all().order_by('-id')
    serializer_class = ArizaYuborishSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]

    search_fields = ['status', 'tuzilma__tuzilma_nomi', 'created_by__username', 'comment']
    ordering_fields = ['id', 'tuzilma__tuzilma_nomi', 'created_by__username']
    # filterset_fields = ['status', 'is_approved']
    filterset_class = ArizaYuborishFilter

    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ArizaYuborish.objects.all().order_by('-id')
        return ArizaYuborish.objects.filter(created_by=user).order_by('-id')

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            status="jarayonda",
            is_approved=user.is_superuser
        )



class KelganArizalarFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr='exact')
    is_approved = django_filters.BooleanFilter()

    tuzilma_nomi = django_filters.CharFilter(
        field_name='ariza__tuzilma__tuzilma_nomi',
        lookup_expr='icontains'
    )

    created_by = django_filters.NumberFilter(
        field_name='ariza__created_by_id'
    )

    class Meta:
        model = KelganArizalar
        fields = ['status', 'is_approved', 'tuzilma_nomi', 'created_by']


            
   
class KelganArizalarViewSet(viewsets.ModelViewSet):
    queryset = ArizaYuborish.objects.all().order_by('-id')
    serializer_class = ArizaYuborishWithKelganSerializer
    permission_classes = [permissions.IsAuthenticated]

    search_fields = [
        'status',
        'tuzilma__tuzilma_nomi',
        'created_by__username',
        'kelganlar__comment',
        'kelganlar__status'
    ]

    ordering_fields = ['id', 'sana', 'status']

    filterset_class = ArizaYuborishFilter   

    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return ArizaYuborish.objects.prefetch_related(
                Prefetch('kelganlar', queryset=KelganArizalar.objects.all())
            ).order_by('-id')

        if user.tarkibiy_tuzilma:
            return ArizaYuborish.objects.filter(
                tuzilma=user.tarkibiy_tuzilma
            ).prefetch_related(
                Prefetch('kelganlar', queryset=KelganArizalar.objects.all())
            ).order_by('-id')

        elif user.bekat_nomi:
            tuzilma = TarkibiyTuzilma.objects.filter(
                tuzilma_nomi=user.bekat_nomi
            ).first()
            if tuzilma:
                return ArizaYuborish.objects.filter(
                    tuzilma=tuzilma
                ).prefetch_related(
                    Prefetch('kelganlar', queryset=KelganArizalar.objects.all())
                ).order_by('-id')

        return ArizaYuborish.objects.none()

    
    
    
    @action(detail=False, methods=['post'], serializer_class=ArizaStatusUpdateSerializer)
    def status_ozgartirish(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ariza = serializer.validated_data['ariza']
        holat = serializer.validated_data['holat']
        comment = serializer.validated_data.get('comment', '')

        user = request.user
        if not user.is_superuser and ariza.tuzilma != getattr(user, 'tarkibiy_tuzilma', None):
            return Response({"detail": "Ruxsat yo‘q"}, status=403)

        ariza.status = holat

        if holat == "qaytarildi":
            ariza.qayta_yuklandi = False
        else:
            ariza.qayta_yuklandi = bool(ariza.rasmlar.exists() or ariza.bildirgi)

        ariza.save()

        kelgan = None
        if comment:
            kelgan = KelganArizalar.objects.create(
                ariza=ariza,
                created_by=user,
                comment=comment or "", 
                status=holat,         
                is_approved=user.is_superuser
            )

        # Response ichida stepday kelganlar bilan qaytarish
        serializer_data = ArizaYuborishWithKelganSerializer(ariza, context={'request': request}).data

        return Response({
            "success": True,
            "ariza": serializer_data,
            "return_commenti": comment or None
        }, status=status.HTTP_200_OK)






class KelganArizalarCreateViewSet(viewsets.ModelViewSet):
    queryset = KelganArizalar.objects.all()
    serializer_class = KelganArizalarSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['status', 'ariza__tuzilma__tuzilma_nomi', 'created_by__username']
    ordering_fields = ['id', 'sana', 'status']
    filterset_fields = ['status', 'is_approved' ]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        qs = KelganArizalar.objects.all()
        
        if user.is_superuser:
            return qs
        elif user.tarkibiy_tuzilma:
            return qs.filter(ariza__tuzilma=user.tarkibiy_tuzilma)
        elif user.bekat_nomi:
            tuzilma = TarkibiyTuzilma.objects.filter(tuzilma_nomi=user.bekat_nomi.bekat_nomi).first()
            if tuzilma:
                return qs.filter(ariza__tuzilma=tuzilma)
        return qs.none()

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        serializer = serializer_class(*args, **kwargs)

        # Faqat hali bajarilmagan arizalarni dropdownga chiqaramiz
        user = self.request.user
        ariza_qs = ArizaYuborish.objects.exclude(status="bajarilgan")

        if not user.is_superuser:
            if user.tarkibiy_tuzilma:
                ariza_qs = ariza_qs.filter(tuzilma=user.tarkibiy_tuzilma)
            elif user.bekat_nomi:
                tuzilma = TarkibiyTuzilma.objects.filter(
                    tuzilma_nomi=user.bekat_nomi.bekat_nomi
                ).first()
                if tuzilma:
                    ariza_qs = ariza_qs.filter(tuzilma=tuzilma)
                else:
                    ariza_qs = ArizaYuborish.objects.none()

        # Agar serializer many=True bo'lsa, child.fields ishlatish
        if hasattr(serializer, 'child'):
            serializer.child.fields['ariza'].queryset = ariza_qs
        else:
            serializer.fields['ariza'].queryset = ariza_qs

        return serializer




    def perform_create(self, serializer):
        user = self.request.user
        kelgan = serializer.save(
            created_by=user,
            is_approved=user.is_superuser
        )
        # Javob qo‘shilganda asosiy arizani statusini "bajarildi" ga o‘zgartirish
        ariza = kelgan.ariza
        ariza.status = "bajarilgan"
        ariza.save()




class ArizaImageDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        image = get_object_or_404(ArizaYuborishImage, pk=pk)

        if image.ariza.created_by != request.user and not request.user.is_superuser:
            return Response(
                {"detail": "Ruxsat yo'q"},
                status=status.HTTP_403_FORBIDDEN
            )

        image.rasm.delete(save=False)
        image.delete()

        return Response(
            {"detail": "Rasm o‘chirildi"},
            status=status.HTTP_204_NO_CONTENT
        )


# class KelganArizalarImagedeleteAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def delete(self, request, pk):
#         image = get_object_or_404(KelganArizalarImage, pk=pk)

#         if image.kelgan_ariza.created_by != request.user and not request.user.is_superuser:
#             return Response(
#                 {"detail": "Ruxsat yo'q"},
#                 status=status.HTTP_403_FORBIDDEN
#             )

#         image.rasm.delete(save=False)
#         image.delete()

#         return Response(
#             {"detail": "Rasm o‘chirildi"},
#             status=status.HTTP_204_NO_CONTENT
#         )


            
class PPRTuriViewSet(viewsets.ModelViewSet):
    queryset = PPRTuri.objects.all()
    serializer_class = PPRTuriSerializer
    


class ObyektNomiViewSet(viewsets.ModelViewSet):
    queryset = ObyektNomi.objects.all()
    serializer_class = ObyektNomiSerializer
    pagination_class = CustomPagination


class PPRJadvalViewSet(viewsets.ModelViewSet):
    queryset = PPRJadval.objects.all()
    serializer_class = PPRJadvalSerializer

    @action(detail=False, methods=['post'])
    def create_jadval(self, request):
        if PPRJadval.objects.filter(tasdiqlangan=True).exists():
            return Response(
                {"detail": "Tasdiqlangan jadval mavjud. Yangi jadval qo‘shib bo‘lmaydi."},
                status=400
            )

        jadval_type = request.data.get("jadval_type")
        obyektlar = ObyektNomi.objects.all()
        ppr_turlari = PPRTuri.objects.filter(user=request.user)

        if jadval_type == "yillik":
            oylar = [
                "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
                "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
            ]

            for oy in oylar:
                for obyekt in obyektlar:
                    for ppr in ppr_turlari:
                        PPRJadval.objects.create(
                            oy=oy,
                            obyekt=obyekt,
                            ppr_turi=ppr
                        )

        elif jadval_type == "oylik":
            oy = request.data.get("oy")
            kunlar = request.data.get("kunlar")  # list of dates

            if not oy or not kunlar:
                return Response(
                    {"detail": "Oylik jadval uchun oy va kunlar majburiy"},
                    status=400
                )

            for sana in kunlar:
                for obyekt in obyektlar:
                    for ppr in ppr_turlari:
                        PPRJadval.objects.create(
                            oy=oy,
                            sana=sana,
                            obyekt=obyekt,
                            ppr_turi=ppr
                        )
        else:
            return Response({"detail": "Noto‘g‘ri jadval turi"}, status=400)

        return Response({"detail": "Jadval muvaffaqiyatli yaratildi"}, status=201)

class HujjatlarViewSet(viewsets.ModelViewSet):
    queryset = Hujjatlar.objects.all()
    serializer_class = HujjatlarSerializer
    pagination_class = CustomPagination


class NotificationsViewSet(viewsets.ReadOnlyModelViewSet):
    
    serializer_class = NotificationsSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # Hozirgi oy
        current_month = datetime.now().month  
        user = request.user

        ppr_this_month = PPRJadval.objects.filter(
            oy=current_month,
            kim_tomonidan=user
        )

        # Agar PPR yo‘q bo‘lsa
        if not ppr_this_month.exists():
            return Response(
                {"message": "Ushbu oyda PPR topilmadi."},
                status=status.HTTP_200_OK
            )

        # Natijalarni serializer qilish
        serialized = PPRJadvalSerializer(ppr_this_month, many=True).data

        return Response(
            {
                "message": f"Bu oyda siz bajarishingiz kerak bo‘lgan {len(serialized)} ta PPR mavjud.",
                "pprlar": serialized
            },
            status=status.HTTP_200_OK
        )

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *


router = DefaultRouter()

router.register("register", UserTuzilmaViewSet, basename="register")
router.register('bolimlar', BolimViewSet, basename='bolimlar')
router.register('bolim-category', BolimCategoryViewSet, basename='bolim-category')
router.register("ariza", ArizaYuborishViewSet, basename="ariza")
router.register("kelgan-arizalar", KelganArizalarViewSet, basename="kelgan-arizalar")
router.register('ariza-status', ArizaStatusViewSet, basename='ariza-status')
router.register("kelgan-arizalar-create", KelganArizalarCreateViewSet, basename="kelgan-arizalar-create")  
router.register("ppr-turi", PPRTuriViewSet)
router.register("obyekt", ObyektNomiViewSet)
router.register('obyekt-locations', ObyektLocationViewSet)
router.register("ppr-jadval", PPRJadvalViewSet)
router.register('ppr-yuborish', PPRYuborishViewSet, basename='ppr-yuborish')
router.register('ppr-tasdiqlash', PPRTasdiqlashViewSet, basename='ppr-tasdiqlash')
#router.register('yillar', YilViewSet, basename='yil')
router.register('ppr-yillik', PPRYillikJadvalViewSet, basename='ppr-yillik')
router.register('ppr-yillik-yuborish', PPRYillikYuborishViewSet, basename='ppr-yillik-yuborish')
router.register('ppr-yillik-tasdiqlash', PPRYillikTasdiqlashViewSet, basename='ppr-yillik-tasdiqlash')
router.register("ppr-bajarildi", PPRBajarildiViewSet, basename='ppr-bajarildi')
router.register("ppr-yillik-bajarildi", PPRYillikBajarildiViewSet, basename='ppr-yillik-bajarildi')
router.register("hujjatlar", HujjatlarViewSet)
router.register("notifications", NotificationViewSet, basename="notifications")
router.register("yuborish-status", PPRYuborishStatusViewSet, basename="yuborish-status")
router.register('ppr-jarayonda', PPRJarayondaOylikViewSet, basename='ppr-jarayonda')
router.register('hujjatlar_shabloni', HujjatShabloniViewSet, basename='hujjatlar_shabloni')


urlpatterns = [
    path("", include(router.urls)),
    path("tuzilma-nomi/", TuzilmaNomiViewSet.as_view({'get':'list'}), name='tuzilma-nomi'),
    path("ariza-image-delete/<int:pk>/", ArizaImageDeleteAPIView.as_view()),
    path("me/", MeAPIView.as_view(), name="me"),
    path("delete-steps/", StepDeleteAPIView.as_view(), name="delete-steps"),
    path('dashboard/stats/', PPRDashboardStatsView.as_view(), name='ppr-stats'),
    path('chart-statistics/', StatisticsChartAPIView.as_view(), name='chart-statistics'),
    path('dashboard/main-stats/', DashboardStatsAPIView.as_view(), name='dashboard_stats'),
    path('top-tuzilmalararizasi/', TopTuzilmalarDashboardAPIView.as_view(), name='top-tuzilmalararizasi'),
    # path("kelgan-arizalar-image-delete/<int:pk>/", KelganArizalarImagedeleteAPIView.as_view()),
]



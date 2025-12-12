from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *


router = DefaultRouter()

router.register("register", UserTuzilmaViewSet, basename="register")
router.register("ariza", ArizaYuborishViewSet, basename="ariza")
router.register("kelgan-arizalar", KelganArizalarViewSet, basename="kelgan-arizalar")
router.register("kelgan-arizalar-create", KelganArizalarCreateViewSet, basename="kelgan-arizalar-create")  
router.register("ppr-turi", PPRTuriViewSet)
router.register("obyekt", ObyektNomiViewSet)
router.register("ppr-jadval", PPRJadvalViewSet)
router.register("hujjatlar", HujjatlarViewSet)
router.register("notifications", NotificationsViewSet, basename="notifications")


urlpatterns = [
    path("", include(router.urls)),
    path("tuzilma-nomi/", TuzilmaNomiViewSet.as_view({'get':'list'}), name='tuzilma-nomi'),
    path("ariza-image-delete/<int:pk>/", ArizaImageDeleteAPIView.as_view()),
    path("me/", MeAPIView.as_view(), name="me"),
    # path("kelgan-arizalar-image-delete/<int:pk>/", KelganArizalarImagedeleteAPIView.as_view()),
]



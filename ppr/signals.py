# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import PPRYuborish, PPRTasdiqlash, Notification

User = get_user_model()



OY_NOMLARI = {
    1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel", 5: "May", 6: "Iyun",
    7: "Iyul", 8: "Avgust", 9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
}


@receiver(post_save, sender=PPRYuborish)
def notify_on_ppr_yuborish(sender, instance, created, **kwargs):
    
    if instance.status == 'yuborildi':
        # Faqat o'sha tarkibiy tuzilmadagi rahbarlarni (is_tarkibiy) topish
        rahbarlar = User.objects.filter(
            tarkibiy_tuzilma=instance.tarkibiy_tuzilma,
            role='tarkibiy' # User modelidagi rol nomi
        )
        oy_nomi = OY_NOMLARI.get(instance.oy, instance.oy)
        
        for rahbar in rahbarlar:
            Notification.objects.create(
                bolim_category=instance.bolim_category,
                tarkibiy_tuzilma=instance.tarkibiy_tuzilma,
                title="Yangi PPR paketi kelib tushdi",
                message=f"{instance.bolim_category.nomi} bo'limidan {instance.yil}-yil {oy_nomi} oyi uchun tasdiqlash so'rovi keldi.",
                link_id=instance.id,
                for_rahbar=True
            )

@receiver(post_save, sender=PPRTasdiqlash)
def notification_on_ppr_tasdiqlash(sender, instance, created, **kwargs):
    if created:
        paketi = instance.yuborish_paketi
        status_text = "tasdiqlandi" if instance.status == "tasdiqlandi" else "rad etildi"
        oy_nomi = OY_NOMLARI.get(paketi.oy, paketi.oy)

        # FAQAT BITTA XABAR YARATILADI
        Notification.objects.create(
            bolim_category=paketi.bolim_category,
            tarkibiy_tuzilma=paketi.tarkibiy_tuzilma,
            title=f"{paketi.bolim_category.nomi}: Paket {status_text}",
            message=f"{paketi.yil}-yil {oy_nomi} oyi uchun yuborilgan paket {status_text}.",
            link_id=paketi.id
        )
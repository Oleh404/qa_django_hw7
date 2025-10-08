from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Task

CLOSED_STATUSES = {"done", "closed", "completed"}


@receiver(pre_save, sender=Task)
def _remember_old_status(sender, instance: Task, **kwargs):
    if not instance.pk:
        instance._old_status = None
        return

    try:
        old = Task.objects.get(pk=instance.pk)
        instance._old_status = old.status
    except Task.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Task)
def _notify_on_status_change(sender, instance: Task, created: bool, **kwargs):
    if created:
        return

    old_status = getattr(instance, "_old_status", None)
    new_status = instance.status

    if old_status == new_status:
        return

    if not instance.owner or not instance.owner.email:
        return

    if new_status in CLOSED_STATUSES:
        subject = f"Задача «{instance.title}» закрита"
        body = (
            f"Вітаю, {instance.owner.get_username()}!\n\n"
            f"Ваша задача «{instance.title}» була ЗАКРИТА "
            f"{timezone.localtime():%Y-%m-%d %H:%M}.\n"
            f"Попередній статус: {old_status!r}.\n"
            f"ID задачі: {instance.pk}\n"
        )
    else:
        subject = f"Зміна статусу задачі «{instance.title}»: {old_status!r} → {new_status!r}"
        body = (
            f"Вітаю, {instance.owner.get_username()}!\n\n"
            f"Статус вашої задачі «{instance.title}» змінено на {new_status!r} "
            f"{timezone.localtime():%Y-%m-%d %H:%M}.\n"
            f"Попередній статус: {old_status!r}.\n"
            f"ID задачі: {instance.pk}\n"
        )

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [instance.owner.email],
        fail_silently=True,
    )

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from logmancer.conf import get_bool, should_exclude_model
from logmancer.middleware import get_current_user
from logmancer.utils import LogEvent


# Global signal handlers
@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """Log model save events"""
    if not get_bool("ENABLE_SIGNALS") or should_exclude_model(sender):
        return

    action = "created" if created else "updated"
    LogEvent.info(
        message=f"{sender.__name__} instance {action}: #{instance.pk}",
        meta={
            "model": sender.__name__,
            "action": action,
            "instance_pk": instance.pk,
        },
        source="signal",
        user=get_current_user(),
        actor_type="system",
    )


@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """Log model delete events"""
    if not get_bool("ENABLE_SIGNALS") or should_exclude_model(sender):
        return

    LogEvent.warning(
        message=f"{sender.__name__} instance deleted: #{instance.pk}",
        meta={
            "model": sender.__name__,
            "action": "deleted",
            "instance_pk": instance.pk,
        },
        source="signal",
        user=get_current_user(),
        actor_type="system",
    )

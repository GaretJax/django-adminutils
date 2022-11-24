from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType


def log_action(user, model, action, message=""):
    return LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(model).pk,
        object_id=model.pk,
        object_repr=str(model),
        action_flag=action,
        change_message=message,
    )


def log_addition(user, model, message=""):
    return log_action(user, model, ADDITION, message)


def log_change(user, model, message=""):
    return log_action(user, model, CHANGE, message)


def log_deletion(user, model, message=""):
    return log_action(user, model, DELETION, message)

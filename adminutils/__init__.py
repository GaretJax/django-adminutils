import copy
import threading

from django.contrib import admin
from django.contrib.postgres.fields import DateRangeField
from django_object_actions import DjangoObjectActions

from .actions import form_processing_action, object_action, queryset_action
from .decorators import options
from .widgets import (
    AdminDateRangeWidget,
    admin_detail_link,
    boolean_icon_with_text,
    formatted_json,
    html_list,
    simple_code_block,
)


__version__ = "0.0.21"
__url__ = "https://github.com/GaretJax/django-adminutils"
__author__ = "Jonathan Stoppani"
__email__ = "jonathan@stoppani.name"
__license__ = "MIT"
__all__ = [
    "boolean_icon_with_text",
    "formatted_json",
    "form_processing_action",
    "html_list",
    "ModelAdmin",
    "object_action",
    "options",
    "queryset_action",
    "simple_code_block",
]


def linked_relation(attribute_name, label_attribute=None, short_description=None):
    def getter(self, obj):
        for attr in attribute_name.split("__"):
            obj = getattr(obj, attr)
            if obj is None:
                # Allow None values at any point in the chain
                return None

        return admin_detail_link(
            obj,
            text=(getattr(obj, label_attribute) if obj and label_attribute else None),
        )

    if short_description is None:
        short_description = attribute_name.replace("__", " ").replace("_", " ")
    getter.short_description = short_description
    getter.admin_order_field = attribute_name
    getter.allow_tags = True
    return getter


def linked_inline(attribute_name, short_description=None):
    def getter(self, obj):
        return admin_detail_link(obj, getattr(obj, attribute_name), bold=True)

    if short_description is None:
        short_description = attribute_name.replace("_", " ")
    getter.short_description = short_description
    getter.admin_order_field = attribute_name
    getter.allow_tags = True
    return getter


def pop_fields(fieldsets, fields):
    fieldsets = copy.deepcopy(fieldsets)
    for label, spec in fieldsets:
        spec["fields"] = [f for f in spec["fields"] if f not in fields]
    return [spec for spec in fieldsets if spec[1]["fields"]]


class CreationFormAdminMixin(object):
    creation_fieldsets = None
    creation_readonly_fields = None
    creation_form = None

    def get_fieldsets(self, request, obj=None):
        if obj is None and self.creation_fieldsets is not None:
            return self.creation_fieldsets
        return super(CreationFormAdminMixin, self).get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj is None and self.creation_readonly_fields is not None:
            return self.creation_readonly_fields
        return super(CreationFormAdminMixin, self).get_readonly_fields(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        if obj is None and self.creation_form is not None:
            kwargs["form"] = self.creation_form
        return super(CreationFormAdminMixin, self).get_form(request, obj, **kwargs)


class EditOnlyInlineMixin:
    can_delete = False
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class ModelAdmin(DjangoObjectActions, admin.ModelAdmin):
    formfield_overrides = {
        DateRangeField: {"widget": AdminDateRangeWidget},
    }

    def __init__(self, *args, **kwargs):
        self._request_local = threading.local()
        self._request_local.request = None
        super().__init__(*args, **kwargs)

    @property
    def request(self):
        return self._request_local.request

    def get_queryset(self, request):
        self._request_local.request = request
        return super().get_queryset(request)

    class Media:
        css = {
            "all": ("admin/css/overrides.css",),
        }

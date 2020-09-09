from django.forms.utils import flatatt
from django.contrib import admin
from django.contrib.admin import widgets as django_admin_widgets
from django.utils import html
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from django_object_actions import DjangoObjectActions

from .decorators import options
from .actions import queryset_action, object_action, form_processing_action
from .widgets import (
    simple_code_block,
    admin_detail_link,
    boolean_icon_with_text,
)


__version__ = "0.0.10"
__url__ = "https://github.com/GaretJax/django-adminutils"
__author__ = "Jonathan Stoppani"
__email__ = "jonathan@stoppani.name"
__license__ = "MIT"
__all__ = [
    "options",
    "queryset_action",
    "simple_code_block",
    "object_action",
    "ModelAdmin",
    "boolean_icon_with_text",
    "form_processing_action",
]


# class EditOnlyInlineMixin:
#     can_delete = False
#     extra = 0
#
#     def has_add_permission(self, request):
#         return False
#
#
def linked_relation(
    attribute_name, label_attribute=None, short_description=None
):
    def getter(self, obj):
        for attr in attribute_name.split("__"):
            obj = getattr(obj, attr)
        return admin_detail_link(
            obj,
            text=(
                getattr(obj, label_attribute)
                if obj and label_attribute
                else None
            ),
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
        return super(CreationFormAdminMixin, self).get_readonly_fields(
            request, obj
        )

    def get_form(self, request, obj=None, **kwargs):
        if obj is None and self.creation_form is not None:
            kwargs["form"] = self.creation_form
        return super(CreationFormAdminMixin, self).get_form(
            request, obj, **kwargs
        )


class ModelAdmin(DjangoObjectActions, admin.ModelAdmin):
    class Media:
        css = {
            "all": ("admin/css/overrides.css",),
        }

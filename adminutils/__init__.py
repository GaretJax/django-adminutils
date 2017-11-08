from django.forms.utils import flatatt
from django.contrib import admin
from django.contrib.admin import widgets
from django.db.models import URLField
from django.utils import html
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from django_object_actions import DjangoObjectActions

from .decorators import options
from .actions import queryset_action, object_action


__version__ = '0.0.1'
__url__ = 'https://github.com/GaretJax/django-adminutils'
__author__ = 'Jonathan Stoppani'
__email__ = 'jonathan@stoppani.name'
__license__ = 'MIT'
__all__ = ['options', 'queryset_action', 'object_action', 'ModelAdmin']


# class EditOnlyInlineMixin:
#     can_delete = False
#     extra = 0
#
#     def has_add_permission(self, request):
#         return False
#
#
# def linked_relation(attribute_name, short_description=None):
#     def getter(self, obj):
#         for attr in attribute_name.split('__'):
#             obj = getattr(obj, attr)
#         return admin_detail_link(obj)
#     if short_description is None:
#         short_description = attribute_name.replace('__', ' ').replace('_', ' ')
#     getter.short_description = short_description
#     getter.admin_order_field = attribute_name
#     getter.allow_tags = True
#     return getter
#
#
# def linked_inline(attribute_name, short_description=None):
#     def getter(self, obj):
#         return admin_detail_link(obj, getattr(obj, attribute_name), bold=True)
#     if short_description is None:
#         short_description = attribute_name.replace('_', ' ')
#     getter.short_description = short_description
#     getter.admin_order_field = attribute_name
#     getter.allow_tags = True
#     return getter


class AdminURLFieldWidget(widgets.AdminURLFieldWidget):
    def __init__(self, attrs=None):
        final_attrs = {'class': 'vURLField'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminURLFieldWidget, self).__init__(attrs=final_attrs)

    def render(self, name, value, attrs=None):
        markup = super(widgets.AdminURLFieldWidget, self).render(
            name, value, attrs)
        if value:
            value = force_text(self._format_value(value))
            final_attrs = {'href': html.smart_urlquote(value)}
            markup = html.format_html(
                '<p class="url">{}<br />{} <a{}>{}</a></p>',
                markup, _('Currently:'), flatatt(final_attrs), value,
            )
        return markup


class ModelAdmin(DjangoObjectActions, admin.ModelAdmin):
    formfield_overrides = {
        URLField: {'widget': AdminURLFieldWidget},
    }

    class Media:
        css = {
            'all': (
                'admin/css/overrides.css',
            ),
        }

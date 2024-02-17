import json

from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.postgres.forms import RangeWidget
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import html
from django.utils.safestring import mark_safe


try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


def simple_code_block(code):
    return html.format_html('<pre class="simple-code-block">\n{}</pre>', code)


def styledict(styles):
    return " ".join("{}: {};".format(k, v) for k, v in styles.items())


def boolean_icon_with_text(flag, text):
    return mark_safe(
        """
        <div style="float:left">{}</div>
        <div style="float:left; padding-left: 8px;">{}</div>
        """.format(
            _boolean_icon(flag),
            html.conditional_escape(text),
        )
    )


def html_list(items):
    items = html.format_html_join("\n", "<li>{}</li>", ((str(o),) for o in items))
    return mark_safe('<ul class="list">{items}</ul>'.format(items=items))


def formatted_json(data):
    return simple_code_block(json.dumps(data, cls=DjangoJSONEncoder, indent=2))


def admin_detail_link(
    instance, text=None, bold=False, action="change", site_name="admin"
):
    if instance is None:
        return "n/a"
    url = reverse(
        "admin:{app_label}_{model_name}_{action}".format(
            app_label=instance._meta.app_label,
            model_name=instance._meta.model_name,
            action=action,
        ),
        args=(instance.pk,),
        current_app=site_name,
    )
    text = str(instance) if text is None else text
    style = "font-weight: bold;" if bold else ""
    return html.format_html('<a href="{}" style="{}">{}</a>', url, style, text)


class AdminDateRangeWidget(RangeWidget):
    template_name = "admin/rangefield.html"

    def __init__(self, attrs=None):
        super().__init__(AdminDateWidget, attrs=attrs)

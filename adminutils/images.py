from django.utils.html import format_html

from .widgets import styledict


def simple_thumbnail(
    image_or_url,
    size,
    *,
    crop=True,
    relname=None,
    style=None,
    image_style=None
):
    # TODO: Qs auth?
    if isinstance(image_or_url, str):
        url = image_or_url
    else:
        try:
            from easy_thumbnails.files import get_thumbnailer
        except ImportError:
            raise ImportError(
                "Please install easy_thumbnails to use the "
                "adminutils.images module."
            )

        thumbnailer = get_thumbnailer(image_or_url, relname)
        thumbnail = thumbnailer.get_thumbnail(
            {
                "size": size,
                "crop": crop,
            }
        )
        url = thumbnail.url
        size = (thumbnail.width, thumbnail.height)

    default_style = {
        "border": "1px solid #ccc",
        "padding": "2px",
        "width": "{size[0]}px".format(size=size),
        "height": "{size[1]}px".format(size=size),
        "display": "inline-block",
    }
    default_style.update(style or {})

    default_image_style = {
        "display": "block",
        "width": "{size[0]}px".format(size=size),
        "height": "{size[1]}px".format(size=size),
    }
    default_image_style.update(image_style or {})

    return format_html(
        ('<div style="{}">' '    <img src="{}" style="{}"/>' "</div>"),
        styledict(default_style),
        url,
        styledict(default_image_style),
    )


def round_thumbnail(image_or_url, size, **kwargs):
    radius = max(size)
    default_style = {
        "border-radius": "{}px".format(radius),
        "overflow": "hidden",
    }
    default_style.update(kwargs.get("style", {}))
    kwargs["style"] = default_style
    kwargs["image_style"] = {
        "border-radius": "{}px".format(radius),
    }
    return simple_thumbnail(image_or_url, size, **kwargs)


def field_getter_factory(func):
    def factory(attribute_name, short_description=None, **kwargs):
        def getter(self, obj):
            for attr in attribute_name.split("__"):
                obj = getattr(obj, attr)
            return func(obj, **kwargs)

        if short_description is None:
            short_description = attribute_name.replace("__", " ").replace(
                "_", " "
            )
        getter.short_description = short_description
        getter.admin_order_field = attribute_name
        return getter

    return factory


@field_getter_factory
def image_preview(value, *, size, crop):
    return simple_thumbnail(value, size, crop=crop) if value else "-"

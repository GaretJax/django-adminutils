import functools

from django import http
from django.db import transaction
from django.shortcuts import render, redirect

from django_object_actions import takes_instance_or_queryset


class MethodsRequiredDecorator(object):
    def __init__(self, methods):
        self.methods = methods

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(instance, request, *args, **kwargs):
            if request.method not in self.methods:
                return http.HttpResponseBadRequest(
                    "{} not allowed".format(request.method)
                )
            return func(instance, request, *args, **kwargs)

        return wrapper


def require_method(method):
    return MethodsRequiredDecorator([method])


def queryset_action(func):
    return takes_instance_or_queryset(object_action(func))


def object_action(func):
    return require_method("POST")(func)


def form_processing_action(
    form_class, template_name="admin/generic_form.html", action_label=None
):
    def processor(func):
        def view(self, request, queryset):
            opts = self.model._meta
            tool = getattr(self, request.resolver_match.kwargs["tool"])
            tool_label = getattr(tool, "label")

            if request.method == "POST":
                form = form_class(request.POST, request.FILES)
                if form.is_valid():
                    with transaction.atomic():
                        resp = func(self, request, form)
                    if resp is None:
                        resp = redirect(
                            "admin:%s_%s_changelist"
                            % (opts.app_label, opts.model_name)
                        )
                    return resp
            else:
                form = form_class()

            return render(
                request,
                template_name,
                {
                    "form": form,
                    "opts": opts,
                    "app_label": opts.app_label,
                    "tool_label": tool_label,
                    "action_label": action_label,
                },
            )

        return view

    return processor

import functools

from django import http
from django.db import transaction
from django.shortcuts import redirect, render
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


def require_methods(methods):
    if not isinstance(methods, (list, tuple)):
        methods = [methods]
    return MethodsRequiredDecorator(methods)


def queryset_action(func):
    return takes_instance_or_queryset(object_action(func))


def object_action(func, methods="POST"):
    @functools.wraps(func)
    @require_methods(methods)
    def view(self, request, *args, **kwargs):
        object_id = request.resolver_match.captured_kwargs["pk"]
        actions = self.get_change_actions(request, object_id, form_url="")
        tool = request.resolver_match.captured_kwargs["tool"]
        if tool not in actions:
            raise http.Http404("Action does not exist")
        return func(self, request, *args, **kwargs)
    return view


def form_processing_action(
    form_class,
    *,
    takes_object=False,
    template_name="admin/generic_form.html",
    action_label=None
):
    def processor(func):
        def view(self, request, instance_or_queryset):
            opts = self.model._meta
            kwargs = {"instance": instance_or_queryset} if takes_object else {}
            tool = getattr(self, request.resolver_match.kwargs["tool"])
            tool_label = getattr(tool, "label")

            if request.method == "POST":
                form = form_class(request.POST, request.FILES, **kwargs)
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
                form = form_class(**kwargs)

            return render(
                request,
                template_name,
                {
                    **self.admin_site.each_context(request),
                    "form": form,
                    "opts": opts,
                    "takes_object": takes_object,
                    "object": instance_or_queryset if takes_object else None,
                    "app_label": opts.app_label,
                    "tool_label": tool_label,
                    "action_label": action_label,
                },
            )

        view.attrs = {"use_form": False}
        if takes_object:
            view = object_action(view, methods=["GET", "POST"])
        return view

    return processor

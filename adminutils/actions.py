import functools

from django import http
from django.db import transaction
from django.contrib.admin import helpers
from django.shortcuts import redirect, render
from django_object_actions import takes_instance_or_queryset
from django_object_actions.utils import ChangeActionView, ChangeListActionView


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


def object_action(func=None, *, methods="POST", validate=None, hide_button=False):
    if not func:
        return functools.partial(
            object_action, methods=methods, validate=validate, hide_button=hide_button
        )

    @functools.wraps(func)
    @require_methods(methods)
    def view(self, request, *args, **kwargs):
        view_class = getattr(request.resolver_match.func, "view_class", None)

        run_validation = validate or (
            validate is None
            and view_class
            and issubclass(view_class, (ChangeActionView, ChangeListActionView))
        )

        if run_validation:
            if issubclass(view_class, ChangeActionView):
                object_id = request.resolver_match.captured_kwargs["pk"]
                actions = self.get_change_actions(request, object_id, form_url="")
            elif issubclass(view_class, ChangeListActionView):
                actions = self.get_changelist_actions(request)

            tool = request.resolver_match.captured_kwargs["tool"]
            if tool not in actions:
                raise http.Http404("Action does not exist")
        return func(self, request, *args, **kwargs)

    view.attrs = {"show_button": not hide_button}
    return view


def form_processing_action(
    form_class,
    *,
    takes_object=False,
    template_name="admin/generic_form.html",
    action_label=None,
):
    def processor(func):
        @functools.wraps(func)
        def view(self, request, instance_or_queryset):
            opts = self.model._meta
            kwargs = {"instance": instance_or_queryset} if takes_object else {}

            try:
                tool_id = request.resolver_match.kwargs["tool"]
            except KeyError:
                # There can be multiple action forms on the page (at the top
                # and bottom of the change list, for example). Get the action
                # whose button was pushed.
                try:
                    action_index = int(request.POST.get("index", 0))
                except ValueError:
                    action_index = 0
                data = request.POST.copy()
                data.pop(helpers.ACTION_CHECKBOX_NAME, None)
                data.pop("index", None)

                # Use the action whose button was pushed
                try:
                    data.update({"action": data.getlist("action")[action_index]})
                except IndexError:
                    # If we didn't get an action from the chosen form that's invalid
                    # POST data, so by deleting action it'll fail the validation check
                    # below. So no need to do anything here
                    pass
                action_form = self.action_form(data, auto_id=None)
                action_form.fields["action"].choices = self.get_action_choices(request)

                assert action_form.is_valid()  # Has already been validated once by django

                tool_id = action_form.cleaned_data["action"]
                select_across = action_form.cleaned_data["select_across"]
                is_changelist_action = True
            else:
                is_changelist_action = False
                select_across = False
                action_index = 0

            tool = getattr(self, tool_id)
            tool_label = getattr(tool, "label", tool_id)

            if request.method == "POST" and "_submit" in request.POST:
                form = form_class(request.POST, request.FILES, **kwargs)
                if form.is_valid():
                    with transaction.atomic():
                        resp = func(self, request, instance_or_queryset, form)
                    if resp is None:
                        resp = redirect(
                            f"{self.admin_site.name}:{opts.app_label}_{opts.model_name}_changelist"
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
                    "object" if takes_object else "queryset": instance_or_queryset,
                    "app_label": opts.app_label,
                    "tool_label": tool_label,
                    "tool_id": tool_id,
                    "action_label": action_label,
                    "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
                    "is_changelist_action": is_changelist_action,
                    "action_index": action_index,
                    "select_across": select_across,
                },
            )

        if takes_object:
            view = object_action(view, methods=["GET", "POST"])
        view.attrs = {"use_form": False}
        return view

    return processor

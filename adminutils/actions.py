import functools

from django import http

from django_object_actions import takes_instance_or_queryset


class MethodsRequiredDecorator(object):
    def __init__(self, methods):
        self.methods = methods

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(instance, request, *args, **kwargs):
            if request.method not in self.methods:
                return http.HttpResponseBadRequest(
                    '{} not allowed'.format(request.method))
            return func(instance, request, *args, **kwargs)
        return wrapper


def require_method(method):
    return MethodsRequiredDecorator([method])


def queryset_action(func):
    return takes_instance_or_queryset(object_action(func))


def object_action(func):
    return require_method('POST')(func)

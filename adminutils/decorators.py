def options(**kwargs):
    map = {
        "desc": "short_description",
        "order": "admin_order_field",
    }

    def wrapper(func):
        for k, v in kwargs.items():
            setattr(func, map.get(k, k), v)
        return func

    return wrapper

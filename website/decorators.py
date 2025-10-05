from functools import wraps
from flask import redirect
from flask_login import current_user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function


def rol_required(rol_id):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect("/")
            if current_user.rol_id != rol_id:
                return redirect("/")
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def roles_required(roles_list):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect("/")
            if current_user.rol_id not in roles_list:
                return redirect("/")
            return f(*args, **kwargs)

        return decorated_function

    return decorator

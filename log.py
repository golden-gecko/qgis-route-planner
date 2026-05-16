from functools import wraps


def _safe_repr(value, max_len: int = 200) -> str:
    try:
        result = repr(value)
    except Exception as e:
        print(e)

        result = f'<unreprable {type(value).__name__}>'

    if len(result) > max_len:
        return f'{result[:max_len - 3]}...'

    return result


def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = ', '.join(_safe_repr(arg) for arg in args)
        kwargs_repr = ', '.join(f'{key}={_safe_repr(value)}' for key, value in kwargs.items())
        call_args = ', '.join(part for part in [args_repr, kwargs_repr] if part)

        print(f'{func.__qualname__}({call_args})')

        return func(*args, **kwargs)

    return wrapper

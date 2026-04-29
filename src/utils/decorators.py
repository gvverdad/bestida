
def method_chain(func):
    def wrapper(*args, **kwargs):
        self = args[0]
        func(*args, **kwargs)
        return self

    return wrapper


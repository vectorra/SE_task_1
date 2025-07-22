COUNT = 4

class SingletonMeta(type):
    _instances = {}

    def __call__(cls):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__()
        return cls._instances[cls]

    def __new__(cls, name, bases, attrs):
        print("SingletonMeta __new__")
        return super().__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        print("SingletonMeta __init__")
        super().__init__(name, bases, attrs)


class Singleton(metaclass=SingletonMeta):
    def __new__(cls):
        print("Singleton __new__")
        return super().__new__(cls)

    def __init__(self):
        print("Singleton __init__")
        self.attr = 5


class MultitonMeta(type):
    _instances = {}
    _remaining = COUNT

    def __call__(cls, key):
        if key not in cls._instances:
            if cls._remaining == 0:
                print(f"Instance limit reached. Returning fallback instance for key 'a'")
                return cls._instances['a']
            print(f"Creating instance for key '{key}'")
            cls._instances[key] = super().__call__()
            cls._remaining -= 1
        return cls._instances[key]

    def __new__(cls, name, bases, attrs):
        print("MultitonMeta __new__")
        return super().__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        print("MultitonMeta __init__")
        super().__init__(name, bases, attrs)


class Multiton(metaclass=MultitonMeta):
    def __new__(cls):
        print("Multiton __new__")
        return super().__new__(cls)

    def __init__(self):
        print("Multiton __init__")
        self.attr = 5


def test_singleton():
    print("\n--- Testing Singleton ---")
    x = Singleton()
    y = Singleton()
    x.attr = 7
    print(f"x.attr: {x.attr}, y.attr: {y.attr}")
    print(f"Same instance? {x is y}")


def test_multiton():
    print("\n--- Testing Multiton ---")
    keys = ['a', 'b', 'c', 'k']
    instances = [Multiton(k) for k in keys]
    extra = Multiton('d')
    for i, k in enumerate(keys):
        print(f"extra is instance[{i}] ({k}): {extra is instances[i]}")


if __name__ == "__main__":
    test_singleton()
    test_multiton()

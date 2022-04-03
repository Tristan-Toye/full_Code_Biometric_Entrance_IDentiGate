class SingletonClass():
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonClass, cls).__new__(cls)
        return cls.instance


singleton = SingletonClass()
new_singleton = SingletonClass()

print(singleton is new_singleton)

singleton.singl_variable = "Singleton Variable"

print(new_singleton.singl_variable)

singleton.singl_variable = "lqhgldh"
print(new_singleton.singl_variable)
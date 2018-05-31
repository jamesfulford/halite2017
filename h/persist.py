# persist.py


class Persist(object):

    def __init__(self, attr, default):
        self.attr = attr
        self.default = default

    def __get__(self, instance, owner):
        try:
            inst_rec = instance.__class__._memory[instance.id]
        except KeyError:
            instance.__class__._memory[instance.id] = {}
        finally:
            try:
                return inst_rec[self.attr]
            except KeyError:
                instance.__class__._memory[instance.id][self.attr] = self.default
                return self.default

    def __set__(self, instance, value):
        if instance.id not in instance.__class__._memory:
            instance.__class__._memory[instance.id] = {}
        instance.__class__._memory[instance.id][self.attr] = value

    def __delete__(self, instance):
        del instance.__class__._memory[instance.id][self.attr]

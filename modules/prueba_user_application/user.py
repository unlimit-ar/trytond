from trytond.pool import PoolMeta

class UserApplication(metaclass=PoolMeta):
    __name__ = 'res.user.application'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        apps = ('prueba', "Prueba"),
        cls.application.selection.extend(apps)
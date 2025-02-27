
from trytond.pool import Pool
from . import user
from . import routes

__all__ = ['register', 'routes']

def register():
    Pool.register(
        user.UserApplication,
        module='user_application', type_='model')
    Pool.register(
        module='user_application', type_='wizard')
    Pool.register(
        module='user_application', type_='report')
    

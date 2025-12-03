
from trytond.pool import Pool

def register():
    Pool.register(
        module='posadas', type_='model')
    Pool.register(
        module='posadas', type_='wizard')
    Pool.register(
        module='posadas', type_='report')
    

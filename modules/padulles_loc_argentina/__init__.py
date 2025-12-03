
from trytond.pool import Pool

def register():
    Pool.register(
        module='loc_argentina', type_='model')
    Pool.register(
        module='loc_argentina', type_='wizard')
    Pool.register(
        module='loc_argentina', type_='report')
    

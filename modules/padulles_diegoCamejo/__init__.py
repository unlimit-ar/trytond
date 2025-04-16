
from trytond.pool import Pool

def register():
    Pool.register(
        module='diegoCamejo', type_='model')
    Pool.register(
        module='diegoCamejo', type_='wizard')
    Pool.register(
        module='diegoCamejo', type_='report')
    

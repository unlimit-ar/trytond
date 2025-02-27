
from trytond.pool import Pool
from . import party
from . import studies

def register():
    Pool.register(
        party.Party,
        party.Studies,
        studies.LaboratoryStudy,
        studies.Determinations,
        module='laboratory_patients', type_='model')
    Pool.register(
        module='laboratory_patients', type_='wizard')
    Pool.register(
        module='laboratory_patients', type_='report')
    

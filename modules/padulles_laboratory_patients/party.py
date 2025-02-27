from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.model import fields, ModelSQL, ModelView
from trytond.pyson import Eval, Bool, Not, And, Or, If


class PatientStudy(ModelView, ModelSQL):
    'Study of patients'
    __name__ = 'laboratory_patients.study.determinations'

    result = fields.Char('Result', required=True)
    determinations = fields.Many2One('laboratory.determinations', 'Determinations', required=True)
    name = fields.Char('Name', required=True)


class PatientStudies(ModelView, ModelSQL):
    'Study of patients'
    __name__ = 'laboratory_patients.study.study'

    name = fields.Char('Name', required=True)
    determinations = fields.Many2One('laboratory_patients.study.determinations', 'Determinations', required=True)


class Studies(ModelView, ModelSQL):
    'Studies of patients'
    __name__ = 'laboratory_patients.studies'
 
    patient = fields.Many2One('party.party', 'Party', required=True, domain=[('patient', '=', True)])
    laboratory = fields.Many2One('party.party', 'Party', required=True, domain=[('laboratory', '=', True)])
    studies = fields.One2Many('laboratory_patients.studies', 'studies', 'Study')
    code = fields.Char('Code', required=True) #TODO autoincremental al crearse


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    patient = fields.Boolean('Patient', help='Check if the party is a patient')
    laboratory = fields.Boolean('Laboratory', help='Check if the party is a laboratory')
    dni = fields.Char('DNI', help='DNI of the party', states={'required': Eval('patient', False)})

    @classmethod
    def search_rec_name(cls, name, clause):
        record = super(Party, cls).search_rec_name(name, clause)
        record.append(('dni',) + clause[1:])
        return record



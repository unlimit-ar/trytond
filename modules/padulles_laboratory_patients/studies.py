from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.model import fields, ModelSQL, ModelView
from trytond.pyson import Eval, Bool, Not, And, Or, If



class LaboratoryStudy(ModelView, ModelSQL):
    'Studies of Laboratory'
    __name__ = 'laboratory.study'

    name = fields.Char('Name', required=True) #TODO UNICO E IRREPETIBLE
    determinations = fields.One2Many('laboratory.determinations', 'study', 'Determinations')


class Determinations(ModelView, ModelSQL):
    'Determinations of studies'
    __name__ = 'laboratory.determinations'

    study = fields.Many2One('laboratory.study', 'Study', required=True)
    name = fields.Char('Name', required=True) #TODO UNICO E IRREPETIBLE
    unidades = fields.Char('Unidades', required=True)
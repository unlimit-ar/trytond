from trytond.pool import Pool, PoolMeta
from trytond.model import fields, ModelSQL, ModelView, Workflow, DeactivableMixin
from trytond.pyson import Eval, Bool, Not, And, Or, If


class AlpiEquipos(ModelView, ModelSQL, Workflow, DeactivableMixin):
    'Equipos Alpi'
    __name__ = 'alpi.equipos'
    _rec_name = 'code'

    code = fields.Char('Code', required=True)
    product = fields.Many2One('product.product', 'Producto', required=True)
    quantity = fields.Integer('Cantidad', required=True)
    state = fields.Selection([
        ('en_deposito', 'En Depósito'),
        ('en_uso', 'En Uso'),
        ], 'States', readonly=True)
    movimientos = fields.One2Many('alpi.equipos.movimientos', 'product', 'Movimientos', readonly=True)

    @classmethod
    def __setup__(cls):
        super(AlpiEquipos, cls).__setup__()
        cls._transitions |= set((
                ('en_deposito', 'en_uso'),
                ('en_uso', 'en_deposito'),
                ))

    @staticmethod
    def default_quantity():
        return 1

    @staticmethod
    def default_state():
        return 'en_deposito'


class AlpiEquiposMovimientos(ModelView, ModelSQL):
    'Movimientos de Equipos Alpi'
    __name__ = 'alpi.equipos.movimientos'
    _rec_name = 'code'
    
    user = fields.Many2One('res.user', 'User')
    date = fields.DateTime('Date')
    equipo = fields.Many2One('alpi.equipos', 'Equipo')
    product = fields.Many2One('product.product', 'Producto', readonly=True)
    code = fields.Char('Code', readonly=True)
    quantity = fields.Integer('Cantidad', required=True)
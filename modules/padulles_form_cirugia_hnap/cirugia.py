from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.model import fields, ModelSQL, ModelView, Workflow, DeactivableMixin
from trytond.pyson import Eval, Bool, Not, And, Or, If
from trytond.wizard import Wizard, StateTransition, StateView, StateAction, \
    Button

from .tools import compute_age_from_dates


class FormCirugia(ModelView, ModelSQL, Workflow, DeactivableMixin):
    'Formulario de Cirugia'
    __name__ = 'hnap.form_cirugia'
    _rec_name = 'code'

    code = fields.Char('Code', readonly=True) #TODO tienen q ser secuenciales
    date = fields.Date('Fecha de Creacion', required=True) #TODO fecha de hoy
    insumos = fields.Boolean('Insumos')
    internado = fields.Boolean('Internado')
    estudios = fields.Boolean('Estudios')
    ambulatorio = fields.Boolean('Ambulatorio')
    name = fields.Char('Name', required=True)
    dni = fields.Char('DNI', required=True)
    date_of_birth = fields.Date('Date of Birth', required=True)
    edad = fields.Char('Edad', required=False)
    age = fields.Function(fields.Char('Age'), 'person_age')
    telefono = fields.Char('Telefono', required=True)
    correo = fields.Char('Correo', required=True)
    nro_historia_clinica = fields.Char('Historia Clinica', required=True)
    piso = fields.Char('Piso', states={'required': Bool(Eval('internado'))})
    cama = fields.Char('Cama', states={'required': Bool(Eval('internado'))})
    os = fields.Boolean('Obra Social')
    os_name = fields.Char('OS Name', states={'invisible': Not(Bool(Eval('os')))})
    diagnostico = fields.Char('Diagnostico', required=True)
    solisitud = fields.Char('Solicitud', required=True)
    historia_clinica = fields.Text('Historia Clinica', required=True)
    observaciones = fields.Text('Observaciones')
    user = fields.Many2One('res.user', 'Solicitante', states={'readonly': True})
    aprobacion_final = fields.Boolean('Aprobacion Final')
    lines = fields.One2Many('hnap.form_cirugia.line', 'cirugia', 'Lines', 
                            states={'readonly': True})
    state = fields.Selection([
        ('abierto', 'Abierto'),
        ('en_proceso', 'En Proceso'),
        ('denegado', 'Denegado'),
        ('cerrado', 'Cerrado'),
        ('aprobado', 'Aprobado'),
        ('done', 'Finalizado'),
        ], 'States', readonly=True)

    @classmethod
    def __setup__(cls):
        super(FormCirugia, cls).__setup__()
        cls._transitions |= set((
                ('abierto', 'en_proceso'),
                ('en_proceso', 'denegado'),
                ('en_proceso', 'aprobado'),
                ('aprobado', 'done'),
                ))
        cls._buttons.update({
                'aprobar': {
                    'invisible': Bool(Eval('aprobacion_final')),
                    },
                'aprobar2': {
                    'invisible': Not(Bool(Eval('aprobacion_final'))),
                    },
                'no_aprobar': {
                    },
                'finalizar': {
                    },
                })

    @staticmethod
    def default_state():
        return 'abierto'

    @classmethod
    def default_date(cls):
        pool = Pool()
        Date = pool.get('ir.date')
        return Date.today()
    
    @staticmethod
    def default_user():
        transaction = Transaction()
        user = transaction.user
        return user

    def person_age(self, name):
        return compute_age_from_dates(
            self.date_of_birth)

    @fields.depends('date_of_birth')
    def on_change_date_of_birth(self):
        """ Automatically show the age in Y-M-D format upon
            entering the date of birth
        """
        self.age = self.person_age(name='age')

    @classmethod
    @ModelView.button_action('form_cirugia_hnap.wiz_change_state_form_cirugia')
    def aprobar(cls, form):
        pass

    @classmethod
    @ModelView.button_action('form_cirugia_hnap.wiz_change_state_form_cirugia')
    def aprobar2(cls, form):
        pass

    @classmethod
    @ModelView.button_action('form_cirugia_hnap.wiz_change_state_form_cirugia')
    def no_aprobar(cls, form):
        pass



class FormCirugiaLine(ModelView, ModelSQL):
    'Lineas del Formulario de Cirugia'
    __name__ = 'hnap.form_cirugia.line'
    _rec_name = 'observaciones'
    
    user = fields.Many2One('res.user', 'User')
    date = fields.Date('Date')
    observaciones = fields.Text('Observaciones')
    cirugia = fields.Many2One('hnap.form_cirugia', 'Cirugia')


class ChangeStateFormCirugia(Wizard):
    'Change State Form Cirugia'
    __name__ = 'hnap.change_state.form_cirugia'

    start = StateView('hnap.form_cirugia.line',
        'form_cirugia_hnap.cirugia_line_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Guardar', 'done', 'tryton-ok', default=True),
            ])
    done = StateTransition()

    def default_start(self, fields):
        transaction = Transaction()
        user = transaction.user

        pool = Pool()
        Date = pool.get('ir.date')
        
        res = {
            'user': user,
            'date': Date.today(),
            }

        return res

    def transition_done(self):
        pool = Pool()
        FormCirugia = pool.get('hnap.form_cirugia')
        form_cirugia = FormCirugia(Transaction().context['active_id'])

        to_create = [{
            'cirugia': form_cirugia.id,
            'observaciones': self.start.observaciones,
            'user': self.start.user.id,
            'date': self.start.date,
            }]
        FormCirugia.write([form_cirugia], {
            'lines': [('create', to_create)],
            'state': 'en_proceso'
            })
        return 'end'

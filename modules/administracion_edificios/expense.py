import re
from datetime import date
from decimal import Decimal

from trytond.model import ModelSQL, ModelView, Unique, fields
from trytond.model.exceptions import ValidationError


PERIOD_PATTERN = re.compile(r'^\d{4}-\d{2}$')


class BuildingExpense(ModelSQL, ModelView):
    'Building Expense'
    __name__ = 'administracion.edificios.expense'

    building = fields.Many2One(
        'administracion.edificios.building', 'Building',
        required=True, ondelete='CASCADE')
    period = fields.Char(
        'Period', required=True,
        help='Monthly period in YYYY-MM format.')
    lines = fields.One2Many(
        'administracion.edificios.expense.line', 'expense', 'Expense Lines')
    total_amount = fields.Function(
        fields.Numeric('Total', digits=(16, 2)),
        'get_total_amount')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        table = cls.__table__()
        cls._sql_constraints += [
            ('building_period_uniq',
                Unique(table, table.building, table.period),
                'There can be only one expense per building and period.'),
            ]
        cls._order = [('period', 'DESC'), ('id', 'DESC')]

    @staticmethod
    def default_period():
        return date.today().strftime('%Y-%m')

    @classmethod
    def validate_fields(cls, expenses, field_names):
        super().validate_fields(expenses, field_names)
        cls.check_period(expenses, field_names)

    @classmethod
    def check_period(cls, expenses, field_names=None):
        if field_names and 'period' not in field_names:
            return
        for expense in expenses:
            if expense.period and not PERIOD_PATTERN.match(expense.period):
                raise ValidationError(
                    'Invalid period "%s". Use the YYYY-MM format.'
                    % expense.period)

    def get_rec_name(self, name):
        del name
        if self.building:
            return '%s - %s' % (self.building.rec_name, self.period)
        return self.period

    def get_total_amount(self, name):
        del name
        return sum(
            (line.amount or Decimal('0.00') for line in self.lines),
            Decimal('0.00'))


class ExpenseLine(ModelSQL, ModelView):
    'Expense Line'
    __name__ = 'administracion.edificios.expense.line'

    expense = fields.Many2One(
        'administracion.edificios.expense', 'Building Expense',
        required=True, ondelete='CASCADE')
    description = fields.Char('Description', required=True)
    amount = fields.Numeric('Amount', digits=(16, 2), required=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._order = [('id', 'ASC')]

from decimal import Decimal

from trytond.model import ModelSQL, ModelView, Unique, fields
from trytond.pool import Pool
from trytond.transaction import Transaction


class Department(ModelSQL, ModelView):
    'Department'
    __name__ = 'administracion.edificios.department'

    building = fields.Many2One(
        'administracion.edificios.building', 'Building',
        required=True, ondelete='CASCADE')
    party = fields.Many2One(
        'party.party', 'Party',
        required=True, ondelete='RESTRICT')
    floor = fields.Char('Floor', required=True)
    unit = fields.Char('Unit', required=True)
    coefficient = fields.Numeric(
        'Coefficient', digits=(16, 8), required=True,
        help='Reserved for future proration rules.')
    monthly_fee = fields.Function(
        fields.Numeric('Monthly Fee', digits=(16, 2)),
        'get_monthly_fee')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        table = cls.__table__()
        cls._sql_constraints += [
            ('building_floor_unit_uniq',
                Unique(table, table.building, table.floor, table.unit),
                'The combination of building, floor and unit must be unique.'),
            ]
        cls._order = [
            ('building', 'ASC'),
            ('floor', 'ASC'),
            ('unit', 'ASC'),
            ]

    @staticmethod
    def default_coefficient():
        return Decimal('1')

    def get_monthly_fee(self, name):
        expense = self._get_context_expense()
        if not expense:
            return Decimal('0.00')
        return self.calculate_monthly_fee(expense)

    def _get_context_expense(self):
        pool = Pool()
        Expense = pool.get('administracion.edificios.expense')
        context = Transaction().context

        expense_id = context.get('expense_id')
        if expense_id:
            return Expense(expense_id)

        period = context.get('period')
        if period and self.building:
            return self.building.get_expense_by_period(period)

        if self.building:
            return self.building.get_latest_expense()
        return None

    def calculate_monthly_fee(self, expense):
        return self._calculate_prorated_fee(expense)

    def _calculate_prorated_fee(self, expense):
        departments = list(self.building.departments or [])
        if not departments:
            return Decimal('0.00')

        total_weight = sum(
            (department.get_fee_weight(expense) for department in departments),
            Decimal('0.00'))
        if not total_weight:
            return Decimal('0.00')

        own_weight = self.get_fee_weight(expense)
        return (expense.total_amount or Decimal('0.00')) * own_weight / total_weight

    def get_fee_weight(self, expense):
        del expense
        return self.coefficient or Decimal('1')

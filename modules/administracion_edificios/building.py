from trytond.model import ModelSQL, ModelView, fields


class Building(ModelSQL, ModelView):
    'Building'
    __name__ = 'administracion.edificios.building'

    name = fields.Char('Name', required=True)
    address = fields.Char('Address')
    departments = fields.One2Many(
        'administracion.edificios.department', 'building', 'Departments')
    expenses = fields.One2Many(
        'administracion.edificios.expense', 'building', 'Monthly Expenses')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._order = [('name', 'ASC')]

    def get_expense_by_period(self, period):
        for expense in self.expenses:
            if expense.period == period:
                return expense
        return None

    def get_latest_expense(self):
        expenses = [expense for expense in self.expenses if expense.period]
        if not expenses:
            return None
        return max(expenses, key=lambda expense: expense.period)

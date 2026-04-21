# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool

from .building import Building
from .department import Department
from .expense import BuildingExpense, ExpenseLine

def register():
    Pool.register(
        Building,
        Department,
        BuildingExpense,
        ExpenseLine,
        module='administracion_edificios', type_='model')

# This file is part of lims_price_list module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool
from . import product


def register():
    Pool.register(
        product.Product,
        module='padulles_purchase_request', type_='model')
    Pool.register(
        module='padulles_purchase_request', type_='wizard')
    Pool.register(
        module='padulles_purchase_request', type_='report')

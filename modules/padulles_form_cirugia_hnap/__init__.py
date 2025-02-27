# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool

from . import cirugia


def register():
    Pool.register(
        cirugia.FormCirugia,
        cirugia.FormCirugiaLine,
        module='form_cirugia_hnap', type_='model')
    Pool.register(
        cirugia.ChangeStateFormCirugia,
        module='form_cirugia_hnap', type_='wizard')

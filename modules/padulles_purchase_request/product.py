# -*- coding: utf-8 -*-
# This file is part of lims_price_list module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.model import fields


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'

    stock_min = fields.Numeric('Min', digits=(12,2))
    stock_min = fields.Numeric('Max', digits=(12,2))

    @classmethod
    def get_sale_price(cls, products, quantity=0, method=None):
        pool = Pool()
        PriceList = pool.get('lims.price_list')
        context = Transaction().context

        prices = super(Product, cls).get_sale_price(products,
            quantity=quantity)
        if context.get('lims_price_list'):
            price_list = PriceList(Transaction().context['lims_price_list'])
            for product in products:
                price = price_list.compute(product, prices[product.id],
                    method=method)
                prices[product.id] = price

        return prices

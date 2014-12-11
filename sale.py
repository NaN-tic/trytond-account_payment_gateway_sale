# This file is part account_payment_gateway_sale module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from decimal import Decimal

__all__ = ['Sale']
__metaclass__ = PoolMeta


class Sale:
    __name__ = 'sale.sale'
    gateway_amount = fields.Function(fields.Numeric("Gateway Amount"), 
        "get_gateway_amount")

    @classmethod
    def get_gateway_amount(cls, sales, names):
        Transaction = Pool().get('account.payment.gateway.transaction')

        origins = ['sale.sale,%s' % sale.id for sale in sales]
        transactions = Transaction.search([
            ('origin', 'in', origins),
            ('state', '=', 'done'),
            ])

        result = {n: {s.id: Decimal(0) for s in sales} for n in names}
        for name in names:
            for sale in sales:
                for transaction in transactions:
                    if transaction.origin == sale:
                        result[name][sale.id] += transaction.amount
        return result

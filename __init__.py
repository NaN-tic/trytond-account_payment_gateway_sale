# This file is part account_payment_gateway_sale module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import gateway
from . import sale


def register():
    Pool.register(
        gateway.AccountPaymentGatewayTransaction,
        sale.Sale,
        module='account_payment_gateway_sale', type_='model')

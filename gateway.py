# This file is part account_payment_gateway_sale module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta


__all__ = ['AccountPaymentGatewayTransaction']
__metaclass__ = PoolMeta


class AccountPaymentGatewayTransaction:
    __name__ = 'account.payment.gateway.transaction'

    @classmethod
    def _get_origin(cls):
        res = super(AccountPaymentGatewayTransaction, cls)._get_origin()
        res.append('sale.sale')
        return res

    @classmethod
    def confirm(cls, transactions):
        pool = Pool()
        Sale = pool.get('sale.sale')

        for transaction in transactions:
            if isinstance(transaction.origin, Sale):
                sale = transaction.origin
                if not sale.reference:
                    Sale.set_reference([sale])
                sale.description = sale.reference
                sale.save()
                Sale.workflow_to_done([sale])

                for invoice in sale.invoices:
                    if invoice.total_amount == transaction.amount:
                        break

                setattr(transaction, 'origin', invoice)

        super(AccountPaymentGatewayTransaction, cls).confirm(transactions)

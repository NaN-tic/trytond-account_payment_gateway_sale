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

    def _set_invoice_as_origin_temporarily(self):
        pool = Pool()
        Sale = pool.get('sale.sale')
        if isinstance(self.origin, Sale):
            sale = self.origin
            if not sale.reference:
                Sale.set_reference([sale])
            sale.description = sale.reference
            sale.save()
            Sale.workflow_to_done([sale])

            invoice = None
            for invoice in sale.invoices:
                if invoice.total_amount == self.amount:
                    break

            if invoice:
                setattr(self, 'origin', invoice)

    @classmethod
    def confirm(cls, transactions):
        for transaction in transactions:
            transaction._set_invoice_as_origin_temporarily()

        super(AccountPaymentGatewayTransaction, cls).confirm(transactions)

    @classmethod
    def refund(cls, transactions):
        for transaction in transactions:
            transaction._set_invoice_as_origin_temporarily()

        super(AccountPaymentGatewayTransaction, cls).refund(transactions)

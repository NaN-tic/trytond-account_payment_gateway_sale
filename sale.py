# This file is part account_payment_gateway_sale module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from decimal import Decimal

__all__ = ['Sale']


class Sale:
    __metaclass__ = PoolMeta
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

    @classmethod
    def workflow_to_done(cls, sales):
        pool = Pool()
        Invoice = pool.get('account.invoice')
        Date = pool.get('ir.date')
        for sale in sales:
            if sale.state == 'draft':
                cls.quote([sale])
            if sale.state == 'quotation':
                cls.confirm([sale])
            if sale.state == 'confirmed':
                cls.process([sale])

            if not sale.invoices and sale.invoice_method == 'order':
                cls.raise_user_error('not_customer_invoice')

            grouping = getattr(sale.party, 'sale_invoice_grouping_method',
                False)
            if sale.invoices and not grouping:
                for invoice in sale.invoices:
                    if invoice.state == 'draft':
                        if not getattr(invoice, 'invoice_date', False):
                            invoice.invoice_date = Date.today()
                        if not getattr(invoice, 'accounting_date', False):
                            invoice.accounting_date = Date.today()
                        invoice.description = sale.number
                        invoice.save()
                Invoice.post(sale.invoices)
                for payment in sale.payments:
                    invoice = sale.invoices[0]
                    payment.invoice = invoice.id
                    # Because of account_invoice_party_without_vat module
                    # could be installed, invoice party may be different of
                    # payment party if payment party has not any vat
                    # and both parties must be the same
                    if payment.party != invoice.party:
                        payment.party = invoice.party
                    payment.save()

            if sale.is_done():
                cls.do([sale])

    @classmethod
    def delete(cls, sales):
        Transaction = Pool().get('account.payment.gateway.transaction')

        origins = ['sale.sale,%s' % sale.id for sale in sales]
        transactions = Transaction.search([
            ('origin', 'in', origins),
            ])
        if transactions:
            Transaction.delete(transactions)

        super(Sale, cls).delete(sales)

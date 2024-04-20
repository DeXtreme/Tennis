import logging

from django.conf import settings


def get_taxed_amount(amount: int) -> int:
    if not amount:
        amount = 0
    if not any([settings.MHC_COMMISSION, settings.TAX_RATE]):
        logging.critical("MHC_COMMISSION or TAX_RATE not set")
    tax = (amount * settings.MHC_COMMISSION) * settings.TAX_RATE
    return round((amount + tax) / 100, 2)


def get_float_taxed_amount(amount: float) -> int:
    if not amount:
        amount = 0
    if not any([settings.MHC_COMMISSION, settings.TAX_RATE]):
        logging.critical("MHC_COMMISSION or TAX_RATE not set")
    tax = (amount * settings.MHC_COMMISSION) * settings.TAX_RATE
    return round((amount + tax), 2)

from decimal import Decimal, getcontext


def calculate_net_and_tax(gross_amount, tax_rate=0.08):
    """
    Calculate the net amount and tax amount from the gross amount given a tax rate.
    Works with both Decimal and float types.

    Parameters:
    gross_amount (Decimal or float): The gross amount (brutto).
    tax_rate (Decimal or float): The tax rate (default is 0.08 for 8%).

    Returns:
    tuple: A tuple containing the net amount and tax amount, in the same type as gross_amount.
    """
    if isinstance(gross_amount, Decimal):
        # Ensure tax_rate is also a Decimal
        if not isinstance(tax_rate, Decimal):
            tax_rate = Decimal(str(tax_rate))
        one_plus_tax_rate = Decimal('1') + tax_rate
        net_amount = gross_amount / one_plus_tax_rate
        tax_amount = gross_amount - net_amount
    else:
        # Assume gross_amount is float
        net_amount = gross_amount / (1 + tax_rate)
        tax_amount = gross_amount - net_amount
    return round(net_amount, 2), round(tax_amount, 2)

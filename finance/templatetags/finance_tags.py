from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def tl(value):
    """
    Sayıyı Türk para formatına çevirir.
    Örnek: 15000 → 15.000₺  |  1500.50 → 1.500,50₺
    """
    try:
        value = Decimal(str(value))
    except Exception:
        return value

    # Ondalık kısım varsa göster, yoksa gösterme
    if value == value.to_integral_value():
        formatted = f"{int(value):,}".replace(",", ".")
    else:
        integer_part, decimal_part = f"{value:.2f}".split(".")
        formatted = f"{int(integer_part):,}".replace(",", ".") + "," + decimal_part

    return f"{formatted}₺"

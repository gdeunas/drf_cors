import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(course_name):
    """Создает продукт в Stripe."""
    product = stripe.Product.create(name=course_name)
    return product.id


def create_stripe_price(amount, product_id):
    """Создает цену в Stripe (сумма передается в рублях, конвертируется в копейки)."""
    price = stripe.Price.create(
        currency="rub",
        unit_amount=int(amount * 100),  # Stripe принимает копейки
        product=product_id,
    )
    return price.id


def create_stripe_session(price_id):
    """Создает сессию оплаты Checkout и возвращает ссылку на оплату и ID сессии."""
    session = stripe.checkout.Session.create(
        success_url="http://127.0.0",  # Ссылка при успешной оплате
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
    )
    return session.url, session.id

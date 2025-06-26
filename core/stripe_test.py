import stripe
import os
from dotenv import load_dotenv
from core.logger import logger
from models import subscription

load_dotenv()
api_key = os.getenv("API_KEY_TEST")

stripe.api_key = api_key


def create_product(name: str, description: str):
    product = stripe.Product.create(name=name, description=description)
    return product


def update_product(id: str, name: str | None = None, description: str | None = None):
    if name and description:
        stripe.Product.modify(id=id, name=name, description=description)
    elif name and not description:
        stripe.Product.modify(id=id, name=name)
    elif description and not name:
        stripe.Product.modify(id=id, description=description)
    return


def get_price(id: str):
    try:
        logger.info(f"[get_price] id recibido: {id}")
        price = stripe.Price.retrieve(id=id)
        return price
    except Exception as e:
        logger.error(f"[get_price] error: {e}")
        raise


def get_all_prices(product_id: str):
    prices = stripe.Price.list(product=product_id)
    return prices


def create_price(amount: int, money: str, product_id: str):
    subscription_price = stripe.Price.create(
        unit_amount=amount,
        currency=money,
        recurring={"interval": "month"},
        product=product_id,
    )
    print(subscription_price)
    return subscription_price


def deactivate_price(id: str):
    modified = stripe.Price.modify(id=id, active=False)
    logger.info(f"Price deleted: {modified['active']}")
    return


def deactivate_product_and_prices(product_id: str):
    # Desactiva
    stripe.Product.modify(product_id, active=False)

    prices = get_all_prices(product_id)
    for p in prices:
        stripe.Price.modify(id=p["id"], active=False)

    return {"detail": "The plan has been deactivated"}


def createCustomer(email: str, customer_id: str):
    customer = stripe.Customer.create(
        api_key=api_key, email=email, metadata={"customer_id": customer_id}
    )
    return customer


def createSubscription(customer_id: str, price_id: str):
    new_subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
        payment_behavior="default_incomplete",
        payment_settings={"save_default_payment_method": "on_subscription"},
        expand=["latest_invoice.payment_intent"],
    )
    try:
        logger.info(f"Items: {new_subscription.items}")
        current_period_end = new_subscription.items.data[0].current_period_end
    except AttributeError:
        current_period_end = None

    return {
        "subscription_id": new_subscription.id,
        "status": new_subscription.status,
        "clientSecret": new_subscription.latest_invoice.id,
        "current_period_end": current_period_end,
    }


def create_checkout_session():
    pass


def parse_webhook_event():
    pass

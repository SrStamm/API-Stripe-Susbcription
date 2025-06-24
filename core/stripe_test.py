import stripe
import os
from dotenv import load_dotenv
from core.logger import logger

load_dotenv()
api_key = os.getenv("API_KEY_TEST")

stripe.api_key = api_key


def create_product(name: str, description: str):
    product = stripe.Product.create(name=name, description=description)
    return product


def update_product(id: str, active: bool, name: str, description: str):
    if active is not active:
        stripe.Product.modify(id=id, active=active, name=name, description=description)
        return
    else:
        stripe.Product.modify(id=id, name=name, description=description)
        return


def get_price(id: str):
    try:
        price = stripe.Price.retrieve(id)
        return price
    except Exception as e:
        logger.error(f"[get_price] error: {e}")
        raise


def create_price(amount: int, money: str, product_id: str):
    subscription_price = stripe.Price.create(
        unit_amount=amount,
        currency=money,
        recurring={"interval": "month"},
        product=product_id,
    )
    print(subscription_price)
    return subscription_price


def delete_price(id: str):
    modified = stripe.Price.modify(id=id, active=False)
    logger.info(f"Price deleted: {modified['active']}")
    return


def createCustomer(email: str, customer_id: str):
    customer = stripe.Customer.create(
        api_key=api_key, email=email, metadata={"customer_id": customer_id}
    )
    return customer


def create_checkout_session():
    pass


def parse_webhook_event():
    pass

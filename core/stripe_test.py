import stripe
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY_TEST")

stripe.api_key = api_key


def create_product(name: str, description: str):
    product = stripe.Product.create(name=name, description=description)
    return product


def create_price(amount: int, money: str, product_id):
    subscription_price = stripe.Price.create(
        unit_amount=amount,
        currency=money,
        recurring={"interval": "month"},
        product=product_id,
    )
    print(subscription_price)
    return subscription_price


def createCustomer(email: str, customer_id: str):
    customer = stripe.Customer.create(
        api_key=api_key, email=email, metadata={"customer_id": customer_id}
    )
    return customer


def create_checkout_session():
    pass


def parse_webhook_event():
    pass

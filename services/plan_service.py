from fastapi import Depends, HTTPException
from repositories.plan_repositories import PlanRepository, get_plan_repo
from core.stripe_test import create_product, create_price, delete_price, get_price
from core.logger import logger


class PlanService:
    def __init__(self, repo: PlanRepository) -> None:
        self.repo = repo

    def get_all_plans(self):
        return self.repo.get_all_plans()

    def create(self, name: str, description: str, amount: int, money: str):
        product = create_product(name=name, description=description)
        logger.info(f"Product: {product}")

        price = create_price(amount=amount, money=money, product_id=product["id"])
        logger.info(f"Price: {price}")

        self.repo.create(
            price_id=price["id"],
            name=name,
            description=description,
            price_cents=price["unit_amount"],
            interval=price["recurring"]["interval"],
        )
        return {"detail": f"New plan created: {product['name']}"}

    def update_only_price(self, id: str, amount: int, money: str):
        product = self.repo.get_plan_by_id(id)
        if not product:
            raise HTTPException(404, detail=f"Product not found with ID {id}")

        price_found = get_price(product.stripe_price_id)

        if price_found:
            price = create_price(
                amount=amount, money=money, product_id=price_found["product"]
            )

            price_updated = self.repo.update_price_to_plan(
                old_price_id=price_found["id"],
                new_price_id=price["id"],
                price_cents=amount,
                interval=price["recurring"]["interval"],
            )

            delete_price(id=price_found["id"])

            return {
                "detail": f"Price to Product {product.name} updated: {price_updated}"
            }
        logger.error(f"Error not found: {price_found}")
        raise HTTPException(404, detail="Product or Price not found")


def get_plan_serv(repo: PlanRepository = Depends(get_plan_repo)):
    return PlanService(repo)

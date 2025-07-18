from fastapi import Depends, HTTPException
from repositories.plan_repositories import PlanRepository, get_plan_repo
from core.stripe_test import (
    create_product,
    create_price,
    deactivate_price,
    get_price,
    update_product,
    deactivate_product_and_prices,
)
from core.logger import logger
from schemas.exceptions import DatabaseError, PriceNotFound, ProductNotFound


class PlanService:
    def __init__(self, repo: PlanRepository) -> None:
        self.repo = repo

    def get_all_plans(self):
        return self.repo.get_all_plans()

    def create(self, name: str, description: str, amount: int, money: str):
        try:
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

        except DatabaseError as e:
            raise e

    def update(
        self,
        id: str,
        amount: int | None = None,
        money: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ):
        try:
            product = self.repo.get_plan_by_id(id)
            if not product:
                raise ProductNotFound(id)

            price_found = get_price(id)
            if not price_found:
                logger.error(f"Error not found: {price_found}")
                raise PriceNotFound(id)

            update_data = {}
            new_price_id = None

            # Manejo de actualización de datos
            if amount and money:
                new_price = create_price(
                    amount=amount, money=money, product_id=price_found["product"]
                )

                new_price_id = new_price["id"]
                deactivate_price(id=price_found["id"])

                update_data.update(
                    {
                        "new_price_id": new_price_id,
                        "price_cents": amount,
                        "interval": new_price["recurring"]["interval"],
                    }
                )

            # Manejo de actualización de producto
            if name or description:
                update_product(
                    id=price_found["product"], name=name, description=description
                )

                if name:
                    update_data["name"] = name
                if description:
                    update_data["description"] = description

            # actualización única en la base de datos
            if update_data:
                update_data["old_price_id"] = price_found["id"]

                self.repo.update(**update_data)

            return {"detail": f"Price to Product {product.name} updated"}

        except DatabaseError as e:
            raise e

    def deactivate_plan(self, id: str):
        try:
            price = get_price(id)
            logger.info(f"Product_id: {price['product']}")
            deactivate_product_and_prices(price["product"])

            self.repo.delete(id)

            return {"detail": "Plan and prices are been deactivated"}
        except DatabaseError as e:
            raise e


def get_plan_serv(repo: PlanRepository = Depends(get_plan_repo)):
    return PlanService(repo)

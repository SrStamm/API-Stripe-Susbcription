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
from schemas.exceptions import DatabaseError


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
            # Obtiene el plan por medio de price_id
            product = self.repo.get_plan_by_id(id)
            if not product:
                raise HTTPException(404, detail=f"Product not found with ID {id}")

            # Obtiene el Price por medio de
            price_found = get_price(id)

            if price_found:
                if amount and money:
                    # Crea un nuevo Price
                    price = create_price(
                        amount=amount, money=money, product_id=price_found["product"]
                    )

                    self.repo.update(
                        old_price_id=price_found["id"],
                        new_price_id=price["id"],
                        price_cents=amount,
                        interval=price["recurring"]["interval"],
                    )

                    deactivate_price(id=price_found["id"])

                # Se modifica un Product si se qiere modificar
                if name or description:
                    update_product(
                        id=price_found["product"], name=name, description=description
                    )

                    self.repo.update(
                        old_price_id=price_found["id"],
                        name=name,
                        description=description,
                    )

                return {"detail": "Price to Product {product.name} updated"}
            logger.error(f"Error not found: {price_found}")
            raise HTTPException(404, detail="Product or Price not found")
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

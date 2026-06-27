from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Product
from app.services.inventory_service import InventoryService

router = APIRouter()


@router.get(
    "/products",
    summary="Listar todos os produtos",
    description="Retorna uma lista com todos os produtos disponíveis no estoque.",
)
async def get_all_products(db: Session = Depends(get_db)):
    inventory_service = InventoryService(db)
    products = inventory_service.get_all_products()
    return [product.to_dict() for product in products]


@router.get(
    "/products/{product_id}",
    summary="Obter produto por ID",
    description="Retorna os detalhes de um produto específico usando seu ID.",
)
async def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.to_dict()

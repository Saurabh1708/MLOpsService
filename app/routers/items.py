from fastapi import APIRouter, HTTPException
from typing import List
from ..models.base import BaseSchema

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

# Sample data store (replace with database in production)
items = []

class Item(BaseSchema):
    name: str
    description: str | None = None
    price: float
    is_available: bool = True

@router.get("/", response_model=List[Item])
async def read_items():
    return items

@router.post("/", response_model=Item)
async def create_item(item: Item):
    items.append(item)
    return item

@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: int):
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found") 
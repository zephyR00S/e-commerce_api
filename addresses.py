from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import AddressCreate, AddressOut
from database import get_db
from auth import get_current_user
import crud, models


router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.post("/", response_model=AddressOut)
def add_address(
    data: AddressCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    return crud.create_address(db, user.id, data)


@router.get("/", response_model=list[AddressOut])
def get_addresses(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    return crud.list_addresses(db, user.id)


@router.put("/{address_id}/primary", response_model=AddressOut)
def make_primary(
    address_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    addr = crud.set_primary_address(db, user.id, address_id)
    if not addr:
        raise HTTPException(404, "Address not found")
    return addr

@router.delete("/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    success = crud.delete_address(db, user.id, address_id)
    if not success:
        raise HTTPException(404, "Address not found")
    return {"message": "Address deleted"}

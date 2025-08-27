from pydantic import BaseModel
from typing import Optional

# Schemas de Usuario
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool

# Schemas de Autenticación
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Schemas de Producto
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: int

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: int
    created_by: int

# Schemas de Favoritos
class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    product: ProductResponse
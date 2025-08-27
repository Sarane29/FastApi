from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Base, User, Product, Favorite
from database import engine, get_db
from schemas import *
from auth import *

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    hashed_pw = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    token = create_access_token({"sub": db_user.username})
    return {"access_token": token}

@app.get("/users/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/protected")
def protected(current_user: User = Depends(get_current_user)):
    return {"message": f"Hola {current_user.username}, estás autenticado"}

@app.get("/admin-only")
def admin_only(current_user: User = Depends(require_admin)):
    return {"message": f"Acceso concedido a admin {current_user.username}"}

# Opcionales
@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    new_product = Product(**product.dict(), created_by=current_user.id)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.get("/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.put("/products/{id}", response_model=ProductResponse)
def update_product(id: int, product: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    db_product = db.query(Product).get(id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    return db_product

@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    db_product = db.query(Product).get(id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(db_product)
    db.commit()
    return {"message": "Producto eliminado"}

@app.post("/favorites/{product_id}", response_model=FavoriteResponse)
def add_favorite(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fav = Favorite(user_id=current_user.id, product_id=product_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    product = db.query(Product).get(product_id)
    return FavoriteResponse(id=fav.id, user_id=fav.user_id, product_id=fav.product_id, product=product)

@app.get("/favorites", response_model=list[FavoriteResponse])
def get_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    favs = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    result = []
    for fav in favs:
        product = db.query(Product).get(fav.product_id)
        result.append(FavoriteResponse(id=fav.id, user_id=fav.user_id, product_id=fav.product_id, product=product))
    return result

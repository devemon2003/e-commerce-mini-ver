from fastapi import FastAPI
from app.database import Base,engine
from app.routes import user,categories,product,cart,order


Base.metadata.create_all(bind=engine)


app = FastAPI(title="E-Commerce API")

app.include_router(user.router)
app.include_router(categories.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(order.router)

@app.get("/")
def root():
    return{"Message":"E-Commerce API is running..."}
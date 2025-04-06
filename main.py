from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db import models, database, crud
from auth import auth_router
from stripe.stripe_webhook import router as stripe_router
from jose import JWTError, jwt
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)

app.include_router(auth_router, prefix="/auth")
app.include_router(stripe_router, prefix="/stripe")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# --- Auth helper ---
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload['sub']
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

# --- Routes ---
@app.post("/api/scan")
def receive_scan(scan: dict, authorization: str = Header(None), db: Session = Depends(database.get_db)):
    if authorization != f"Bearer {os.getenv('API_TOKEN')}":
        raise HTTPException(status_code=403, detail="Unauthorized")
    crud.store_tags(db, scan['tags'], scan['account_id'])
    return {"status": "success"}

@app.get("/api/scans")
def get_scans(db: Session = Depends(database.get_db)):
    return {"tags": crud.get_recent_tags(db)}

@app.get("/api/me")
def get_me(user_id: str = Depends(get_current_user), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    account = db.query(models.Account).filter(models.Account.id == user.account_id).first()
    return {"user_id": user.id, "plan": account.subscription_plan if account else "unknown"}

@app.post("/stripe/checkout")
def create_checkout(user_id: str = Depends(get_current_user), db: Session = Depends(database.get_db)):
    from stripe.checkout import Session as StripeSession
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    account = db.query(models.Account).filter(models.Account.id == user.account_id).first()
    session = StripeSession.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "8ightball Pro Subscription"},
                "unit_amount": 4900
            },
            "quantity": 1
        }],
        mode="subscription",
        customer_email=user.email,
        metadata={"account_id": user.account_id},
        success_url="http://localhost:3000/dashboard",
        cancel_url="http://localhost:3000/billing"
    )
    return {"url": session.url}


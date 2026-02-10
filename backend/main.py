



# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from routes.factures import router as factures_router

# app = FastAPI(title="Zero Saisie API")

# # ✅ CORS (pour autoriser le frontend à appeler l'API)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # plus tard: mettre l'URL exacte du frontend
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(factures_router)

# @app.get("/")
# def home():
#     return {"message": "API is running"}




from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.factures import router as factures_router

app = FastAPI(
    title="Zero Saisie API",
    version="0.1.0"
)

# ✅ CORS (autoriser le frontend à appeler l'API)
# Plus tard: remplace ["*"] par ["http://localhost:3000"] ou l'URL réelle du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Routes
app.include_router(factures_router)

# ✅ Home
@app.get("/")
def home():
    return {"message": "API is running"}

# ✅ Health check (utile pour tester rapidement)
@app.get("/health")
def health():
    return {"status": "ok"}



# # main.py
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from routes.factures import router as factures_router
# from routes.societes import router as societes_router

# app = FastAPI(title="PFE Zero Saisie API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/")
# def home():
#     return {"message": "API running"}

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# # ✅ include routers
# app.include_router(societes_router)
# app.include_router(factures_router)

















from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.factures import router as factures_router
from routes.societes import router as societes_router
from routes.ecritures import router as ecritures_router  # ✅

app = FastAPI(title="PFE Zero Saisie API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API running"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(societes_router)
app.include_router(factures_router)
app.include_router(ecritures_router)  # ✅

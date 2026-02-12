






# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from routes.factures import router as factures_router

# app = FastAPI(title="Zero Saisie API", version="0.1.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(factures_router)

# @app.get("/")
# def home():
#     return {"message": "API is running"}

# @app.get("/health")
# def health():
#     return {"status": "ok"}













# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from routes.factures import router as factures_router

# app = FastAPI(title="Zero Saisie API", version="0.1.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(factures_router)

# @app.get("/")
# def home():
#     return {"message": "API is running"}

# @app.get("/health")
# def health():
#     return {"status": "ok"}













from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.factures import router as factures_router

app = FastAPI(
    title="Zero Saisie API",
    version="0.1.0",
    description="Backend FastAPI pour extraction automatique de factures (OCR + parsing + DB)."
)

# CORS (autorise frontend React / Angular / etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod, mets l'URL du frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(factures_router)


@app.get("/")
def home():
    return {"message": "API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}

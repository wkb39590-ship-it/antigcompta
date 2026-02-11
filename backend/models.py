

# from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
# from sqlalchemy.orm import relationship
# from database import Base


# class Facture(Base):
#     __tablename__ = "factures"

#     id = Column(Integer, primary_key=True, index=True)

#     # Champs extraits / saisis
#     fournisseur = Column(String, nullable=True)     # ✅ fournisseur réel (ex: STE SHEMADRI)
#     date_facture = Column(Date, nullable=True)

#     montant_ht = Column(Float, nullable=True)
#     montant_tva = Column(Float, nullable=True)
#     montant_ttc = Column(Float, nullable=True)

#     statut = Column(String, default="brouillon")

#     # Infos facture
#     numero_facture = Column(String(50), nullable=True)   # ✅ ex: 2025-390
#     designation = Column(String(255), nullable=True)

#     # -------------------------
#     # Champs DED
#     # -------------------------

#     # ⚠️ Compat DB : on garde le nom if_frs,
#     # MAIS on l'utilise comme IF SOCIETE (émetteur) (ex: IF:25005226)
#     if_frs = Column(String(50), nullable=True)

#     # ICE du fournisseur (bloc encadré) (ex: ICE:003272689000032)
#     ice_frs = Column(String(50), nullable=True)

#     taux_tva = Column(Float, nullable=True)     # ex: 20.0
#     id_paie = Column(String(50), nullable=True)
#     date_paie = Column(Date, nullable=True)

#     # Ancien champ (compat)
#     ded_file_path = Column(String(255), nullable=True)

#     # Nouveaux chemins
#     ded_pdf_path = Column(String(255), nullable=True)
#     ded_xlsx_path = Column(String(255), nullable=True)

#     # Relations
#     ecritures = relationship(
#         "EcritureComptable",
#         back_populates="facture",
#         cascade="all, delete-orphan"
#     )


# class EcritureComptable(Base):
#     __tablename__ = "ecritures_comptables"

#     id = Column(Integer, primary_key=True, index=True)
#     facture_id = Column(Integer, ForeignKey("factures.id", ondelete="CASCADE"), nullable=False)

#     compte = Column(String(20), nullable=False)
#     libelle = Column(String(255), nullable=True)
#     debit = Column(Float, default=0)
#     credit = Column(Float, default=0)

#     facture = relationship("Facture", back_populates="ecritures")
















# from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
# from sqlalchemy.orm import relationship
# from database import Base


# class Facture(Base):
#     __tablename__ = "factures"

#     id = Column(Integer, primary_key=True, index=True)

#     # Qui vend (FOURNISSEUR)
#     fournisseur = Column(String, nullable=True)

#     # Date facture + num facture
#     date_facture = Column(Date, nullable=True)
#     numero_facture = Column(String(50), nullable=True)

#     # Désignation (libellé global)
#     designation = Column(String(255), nullable=True)

#     # Montants
#     montant_ht = Column(Float, nullable=True)
#     montant_tva = Column(Float, nullable=True)
#     montant_ttc = Column(Float, nullable=True)

#     # Statut
#     statut = Column(String, default="brouillon")

#     # --- Champs DED (FOURNISSEUR) ---
#     # IF du fournisseur (vendeur)
#     if_frs = Column(String(50), nullable=True)
#     # ICE du fournisseur (vendeur)
#     ice_frs = Column(String(50), nullable=True)

#     taux_tva = Column(Float, nullable=True)     # ex: 20
#     id_paie = Column(String(50), nullable=True) # si tu veux plus tard
#     date_paie = Column(Date, nullable=True)     # si tu veux plus tard

#     # Fichiers DED
#     ded_file_path = Column(String(255), nullable=True)  # compat ancien
#     ded_pdf_path = Column(String(255), nullable=True)
#     ded_xlsx_path = Column(String(255), nullable=True)

#     ecritures = relationship(
#         "EcritureComptable",
#         back_populates="facture",
#         cascade="all, delete-orphan",
#     )


# class EcritureComptable(Base):
#     __tablename__ = "ecritures_comptables"

#     id = Column(Integer, primary_key=True, index=True)
#     facture_id = Column(Integer, ForeignKey("factures.id", ondelete="CASCADE"), nullable=False)

#     compte = Column(String(20), nullable=False)
#     libelle = Column(String(255), nullable=True)
#     debit = Column(Float, default=0)
#     credit = Column(Float, default=0)

#     facture = relationship("Facture", back_populates="ecritures")

















# models.py
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Facture(Base):
    __tablename__ = "factures"

    id = Column(Integer, primary_key=True, index=True)

    fournisseur = Column(String, nullable=True)

    date_facture = Column(Date, nullable=True)
    numero_facture = Column(String(50), nullable=True)

    designation = Column(String(255), nullable=True)

    montant_ht = Column(Float, nullable=True)
    montant_tva = Column(Float, nullable=True)
    montant_ttc = Column(Float, nullable=True)

    statut = Column(String, default="brouillon", nullable=False)

    if_frs = Column(String(50), nullable=True)
    ice_frs = Column(String(50), nullable=True)

    taux_tva = Column(Float, nullable=True)
    id_paie = Column(String(50), nullable=True)
    date_paie = Column(Date, nullable=True)

    ded_file_path = Column(String(255), nullable=True)
    ded_pdf_path = Column(String(255), nullable=True)
    ded_xlsx_path = Column(String(255), nullable=True)

    ecritures = relationship(
        "EcritureComptable",
        back_populates="facture",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class EcritureComptable(Base):
    __tablename__ = "ecritures_comptables"

    id = Column(Integer, primary_key=True, index=True)
    facture_id = Column(
        Integer,
        ForeignKey("factures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    compte = Column(String(20), nullable=False)
    libelle = Column(String(255), nullable=True)
    debit = Column(Float, default=0, nullable=False)
    credit = Column(Float, default=0, nullable=False)

    facture = relationship("Facture", back_populates="ecritures")

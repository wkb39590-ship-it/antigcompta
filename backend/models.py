

# # models.py
# from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime, func
# from sqlalchemy.orm import relationship
# from database import Base


# class Societe(Base):
#     __tablename__ = "societes"

#     id = Column(Integer, primary_key=True, index=True)
#     raison_sociale = Column(String, nullable=False)

#     ice = Column(String, nullable=True, index=True)
#     if_fiscal = Column(String, nullable=True)
#     rc = Column(String, nullable=True)
#     adresse = Column(String, nullable=True)

#     created_at = Column(DateTime, nullable=False, server_default=func.now())

#     factures = relationship("Facture", back_populates="societe")


# class Facture(Base):
#     __tablename__ = "factures"

#     id = Column(Integer, primary_key=True, index=True)

#     societe_id = Column(Integer, ForeignKey("societes.id"), nullable=False, index=True)

#     operation_type = Column(String(50), nullable=False)      # achat / vente
#     operation_confidence = Column(Float, nullable=False)     # ex 0.99

#     fournisseur = Column(String, nullable=True)

#     date_facture = Column(Date, nullable=True)
#     numero_facture = Column(String(50), nullable=True)

#     designation = Column(String(255), nullable=True)

#     montant_ht = Column(Float, nullable=True)
#     montant_tva = Column(Float, nullable=True)
#     montant_ttc = Column(Float, nullable=True)

#     statut = Column(String, default="brouillon", nullable=False)

#     if_frs = Column(String(50), nullable=True)
#     ice_frs = Column(String(50), nullable=True)

#     taux_tva = Column(Float, nullable=True)
#     id_paie = Column(String(50), nullable=True)
#     date_paie = Column(Date, nullable=True)

#     devise = Column(String(20), nullable=True)  # ✅ AJOUT ICI

#     ded_file_path = Column(String(255), nullable=True)
#     ded_pdf_path = Column(String(255), nullable=True)
#     ded_xlsx_path = Column(String(255), nullable=True)

#     societe = relationship("Societe", back_populates="factures")

#     ecritures = relationship(
#         "EcritureComptable",
#         back_populates="facture",
#         cascade="all, delete-orphan",
#         passive_deletes=True,
#     )


# class EcritureComptable(Base):
#     __tablename__ = "ecritures_comptables"

#     id = Column(Integer, primary_key=True, index=True)

#     facture_id = Column(
#         Integer,
#         ForeignKey("factures.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     compte = Column(String(20), nullable=False)
#     libelle = Column(String(255), nullable=True)
#     debit = Column(Float, default=0, nullable=False)
#     credit = Column(Float, default=0, nullable=False)

#     facture = relationship("Facture", back_populates="ecritures")








from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class Societe(Base):
    __tablename__ = "societes"

    id = Column(Integer, primary_key=True, index=True)
    raison_sociale = Column(String, nullable=False)

    ice = Column(String, nullable=True, index=True)
    if_fiscal = Column(String, nullable=True)
    rc = Column(String, nullable=True)
    adresse = Column(String, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    factures = relationship("Facture", back_populates="societe")
    ecritures = relationship("EcritureComptable", back_populates="societe")


class Facture(Base):
    __tablename__ = "factures"

    id = Column(Integer, primary_key=True, index=True)
    societe_id = Column(Integer, ForeignKey("societes.id"), nullable=False, index=True)

    operation_type = Column(String(50), nullable=False)      # achat / vente
    operation_confidence = Column(Float, nullable=False)     # ex 0.99

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

    devise = Column(String(20), nullable=True)

    ded_file_path = Column(String(255), nullable=True)
    ded_pdf_path = Column(String(255), nullable=True)
    ded_xlsx_path = Column(String(255), nullable=True)

    societe = relationship("Societe", back_populates="factures")

    ecritures = relationship(
        "EcritureComptable",
        back_populates="facture",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ✅ HEADER / ENTÊTE (la pièce comptable)
class EcritureComptable(Base):
    __tablename__ = "ecritures_comptables"

    id = Column(Integer, primary_key=True, index=True)

    societe_id = Column(Integer, ForeignKey("societes.id"), nullable=False, index=True)
    facture_id = Column(Integer, ForeignKey("factures.id", ondelete="CASCADE"), nullable=False, index=True)

    operation = Column(String(50), nullable=False)  # achat/vente/...
    numero_piece = Column(String(50), nullable=False, index=True)
    date_operation = Column(Date, nullable=False, index=True)
    tiers_nom = Column(String(255), nullable=True)

    journal = Column(String(10), nullable=False, server_default="OD", index=True)

    statut = Column(String(50), nullable=False, server_default="brouillon")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    validated_at = Column(DateTime, nullable=True)

    libelle = Column(String(255), nullable=True)

    total_debit = Column(Float, nullable=False, server_default="0")
    total_credit = Column(Float, nullable=False, server_default="0")

    societe = relationship("Societe", back_populates="ecritures")
    facture = relationship("Facture", back_populates="ecritures")
    lignes = relationship(
        "EcritureLigne",
        back_populates="ecriture",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ✅ LIGNES (chaque compte débit/crédit)
class EcritureLigne(Base):
    __tablename__ = "ecritures_lignes"

    id = Column(Integer, primary_key=True, index=True)
    ecriture_id = Column(Integer, ForeignKey("ecritures_comptables.id", ondelete="CASCADE"), nullable=False, index=True)

    compte = Column(String(20), nullable=False)
    libelle = Column(String(255), nullable=True)
    debit = Column(Float, nullable=False, server_default="0")
    credit = Column(Float, nullable=False, server_default="0")

    ecriture = relationship("EcritureComptable", back_populates="lignes")




# from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.orm import declarative_base

# Base = declarative_base()

# class Facture(Base):
#     __tablename__ = "factures"
#     id = Column(Integer, primary_key=True, index=True)
#     fournisseur = Column(String, nullable=True)
#     date_facture = Column(Date, nullable=True)
#     montant_ht = Column(Float, nullable=True)
#     montant_tva = Column(Float, nullable=True)
#     montant_ttc = Column(Float, nullable=True)

#     ecritures = relationship("EcritureComptable", back_populates="facture", cascade="all, delete")


# class EcritureComptable(Base):
#     __tablename__ = "ecritures_comptables"

#     id = Column(Integer, primary_key=True, index=True)
#     facture_id = Column(Integer, ForeignKey("factures.id"), nullable=False)

#     compte = Column(String, nullable=False)         # ex: "401", "44566"
#     libelle = Column(String, nullable=True)
#     debit = Column(Float, default=0)
#     credit = Column(Float, default=0)

#     facture = relationship("Facture", back_populates="ecritures")




from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Facture(Base):
    __tablename__ = "factures"

    id = Column(Integer, primary_key=True, index=True)
    fournisseur = Column(String, nullable=True)
    date_facture = Column(Date, nullable=True)
    montant_ht = Column(Float, nullable=True)
    montant_tva = Column(Float, nullable=True)
    montant_ttc = Column(Float, nullable=True)

    # ✅ champ statut pour la route /valider
    statut = Column(String, nullable=True, default="brouillon")

    # ✅ relation vers les écritures
    ecritures = relationship(
        "EcritureComptable",
        back_populates="facture",
        cascade="all, delete-orphan"
    )


class EcritureComptable(Base):
    __tablename__ = "ecritures_comptables"

    id = Column(Integer, primary_key=True, index=True)
    facture_id = Column(Integer, ForeignKey("factures.id"), nullable=False)

    compte = Column(String, nullable=True)
    libelle = Column(String, nullable=True)
    debit = Column(Float, nullable=True)
    credit = Column(Float, nullable=True)

    facture = relationship("Facture", back_populates="ecritures")

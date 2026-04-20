from pydantic import BaseModel, field_validator
from typing import Optional
import re


class ProspectCreate(BaseModel):
    nom:         str
    secteur:     Optional[str] = None
    ville:       Optional[str] = None
    telephone:   Optional[str] = None
    description: Optional[str] = None
    source:      Optional[str] = None

    @field_validator("nom")
    @classmethod
    def nom_non_vide(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Le nom ne peut pas être vide.")
        return v.title()

    @field_validator("telephone", mode="before")
    @classmethod
    def normaliser_telephone(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        chiffres = re.sub(r"\D", "", v)
        if len(chiffres) == 8:
            d = chiffres
            return f"+229 {d[0:2]} {d[2:4]} {d[4:6]} {d[6:8]}"
        if len(chiffres) == 11 and chiffres.startswith("229"):
            d = chiffres[3:]
            return f"+229 {d[0:2]} {d[2:4]} {d[4:6]} {d[6:8]}"
        if len(chiffres) == 13 and chiffres.startswith("00229"):
            d = chiffres[5:]
            return f"+229 {d[0:2]} {d[2:4]} {d[4:6]} {d[6:8]}"
        return v


class ProspectUpdate(BaseModel):
    categorie:         Optional[str] = None
    score_ia:          Optional[str] = None
    pertinence_ishowo: Optional[str] = None
    justification_ia:  Optional[str] = None
    statut:            Optional[str] = None


class ProspectResponse(BaseModel):
    id:          int
    nom:         str
    secteur:     Optional[str]
    ville:       Optional[str]
    telephone:   Optional[str]
    description: Optional[str]
    source:      Optional[str]
    statut:      str
    categorie:         Optional[str] = None
    score_ia:          Optional[str] = None
    pertinence_ishowo: Optional[str] = None
    justification_ia:  Optional[str] = None

    class Config:
        from_attributes = True


class CollectRequest(BaseModel):
    query:   str       = "entreprises Bénin"
    sources: list[str] = ["goafrica", "google"]
    limit:   int       = 20


class CollectResponse(BaseModel):
    total_collectes: int
    total_inseres:   int
    total_doublons:  int
    message:         str
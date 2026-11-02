"""Preparación del examen PCAP guardada en la cuenta."""

from fastapi import APIRouter

from app import state_documents
from app.deps import CurrentUser, DbSession
from app.models import PcapState
from app.schemas import PcapStateIn, PcapStateOut

router = APIRouter(prefix="/pcap-state", tags=["pcap"])


@router.get("", response_model=PcapStateOut)
def get_pcap_state(user: CurrentUser, db: DbSession) -> PcapStateOut:
    return state_documents.to_out(db.get(PcapState, user.id))


@router.put("", response_model=PcapStateOut, responses={409: {"description": "La cuenta cambió"}})
def save_pcap_state(body: PcapStateIn, user: CurrentUser, db: DbSession) -> PcapStateOut:
    """Guarda el estado completo. El navegador ya lo ha fusionado con el de la cuenta.
    Con `version`, responde 409 si otra pestaña o dispositivo guardó entre medias."""
    return state_documents.save(db, PcapState, {"user_id": user.id}, body)

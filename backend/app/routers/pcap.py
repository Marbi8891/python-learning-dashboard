"""Preparación del examen PCAP guardada en la cuenta."""

from fastapi import APIRouter

from app import state_documents
from app.deps import CurrentUser, DbSession, WritingUser
from app.models import PcapState
from app.schemas import PcapStateIn, PcapStateOut
from app.state_documents import STATE_RESPONSES

router = APIRouter(prefix="/pcap-state", tags=["pcap"])


@router.get("", response_model=PcapStateOut)
def get_pcap_state(user: CurrentUser, db: DbSession) -> PcapStateOut:
    return state_documents.to_out(db.get(PcapState, user.id))


@router.put("", response_model=PcapStateOut, responses=STATE_RESPONSES)
def save_pcap_state(body: PcapStateIn, user: WritingUser, db: DbSession) -> PcapStateOut:
    """Guarda el estado completo. El navegador ya lo ha fusionado con el de la cuenta.
    Con `version`, responde 409 si otra pestaña o dispositivo guardó entre medias; sin ella, solo
    crea el documento (si ya existe, 428: no se sobrescribe sin comprobar)."""
    return state_documents.save(db, PcapState, {"user_id": user.id}, body)

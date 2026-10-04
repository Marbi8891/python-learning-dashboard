"""Preparación del examen PCAP guardada en la cuenta (ver ADR-0010)."""

from fastapi import APIRouter

from app.deps import CurrentUser, DbSession
from app.models import PcapState
from app.schemas import PcapStateIn, PcapStateOut

router = APIRouter(prefix="/pcap-state", tags=["pcap"])


@router.get("", response_model=PcapStateOut)
def get_pcap_state(user: CurrentUser, db: DbSession) -> PcapStateOut:
    state = db.get(PcapState, user.id)
    if state is None:
        return PcapStateOut(data={}, updated_at=None)
    return PcapStateOut(data=state.data, updated_at=state.updated_at)


@router.put("", response_model=PcapStateOut)
def save_pcap_state(body: PcapStateIn, user: CurrentUser, db: DbSession) -> PcapStateOut:
    """Guarda el estado completo. El navegador ya lo ha fusionado con el de la cuenta."""
    state = db.get(PcapState, user.id)
    if state is None:
        state = PcapState(user_id=user.id, data=body.data)
        db.add(state)
    else:
        state.data = body.data
    db.commit()
    db.refresh(state)
    return PcapStateOut(data=state.data, updated_at=state.updated_at)

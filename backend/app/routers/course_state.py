"""Estado de los cursos de DAW guardado en la cuenta (ver ADR-0018 y ADR-0021).

Lo comparten la app Android y la web. El PCAP sigue en /api/pcap-state (ADR-0010); aquí va cada
curso de DAW (Programación, Bases de datos, Entornos, JavaScript y Java) en su documento.
El usuario sale siempre del token de sesión, nunca del cuerpo de la petición.
"""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from app.deps import CurrentUser, DbSession
from app.models import CourseState
from app.schemas import COURSES, PcapStateIn, PcapStateOut

router = APIRouter(prefix="/api/course-state", tags=["cursos"])

CourseId = Annotated[str, Path(max_length=20)]


def _check(course: str) -> None:
    if course not in COURSES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso desconocido")


@router.get("/{course}", response_model=PcapStateOut)
def get_course_state(course: CourseId, user: CurrentUser, db: DbSession) -> PcapStateOut:
    _check(course)
    state = db.get(CourseState, (user.id, course))
    if state is None:
        return PcapStateOut(data={}, updated_at=None)
    return PcapStateOut(data=state.data, updated_at=state.updated_at)


@router.put("/{course}", response_model=PcapStateOut)
def save_course_state(
    course: CourseId, body: PcapStateIn, user: CurrentUser, db: DbSession
) -> PcapStateOut:
    """Guarda el documento completo. La app ya lo ha fusionado con el de la cuenta."""
    _check(course)
    state = db.get(CourseState, (user.id, course))
    if state is None:
        state = CourseState(user_id=user.id, course=course, data=body.data)
        db.add(state)
    else:
        state.data = body.data
    db.commit()
    db.refresh(state)
    return PcapStateOut(data=state.data, updated_at=state.updated_at)

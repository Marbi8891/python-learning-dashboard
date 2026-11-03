"""Estado de los cursos de DAW guardado en la cuenta.

El PCAP sigue en /api/pcap-state; aquí va cada
curso de DAW (Programación, Bases de datos, Entornos, JavaScript y Java) en su documento.
El usuario sale siempre del token de sesión, nunca del cuerpo de la petición.
"""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from app import state_documents
from app.deps import CurrentUser, DbSession, WritingUser
from app.models import CourseState
from app.schemas import COURSES, PcapStateIn, PcapStateOut

router = APIRouter(prefix="/course-state", tags=["cursos"])

CourseId = Annotated[str, Path(max_length=20)]


def _check(course: str) -> None:
    if course not in COURSES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso desconocido")


@router.get("/{course}", response_model=PcapStateOut)
def get_course_state(course: CourseId, user: CurrentUser, db: DbSession) -> PcapStateOut:
    _check(course)
    return state_documents.to_out(db.get(CourseState, (user.id, course)))


@router.put(
    "/{course}", response_model=PcapStateOut, responses={409: {"description": "La cuenta cambió"}}
)
def save_course_state(
    course: CourseId, body: PcapStateIn, user: WritingUser, db: DbSession
) -> PcapStateOut:
    """Guarda el documento completo. La app ya lo ha fusionado con el de la cuenta.
    Con `version`, responde 409 si otra pestaña o dispositivo guardó entre medias."""
    _check(course)
    return state_documents.save(db, CourseState, {"user_id": user.id, "course": course}, body)

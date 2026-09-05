from abc import ABC, abstractmethod

from backend.models import UserContext


class MemoryStore(ABC):
    """
    Abstract interface for session memory.

    The rest of the application should not care whether
    memory is stored locally or in PostgreSQL.
    """

    @abstractmethod
    def get_context(
        self,
        session_id: str,
    ) -> UserContext | None:
        pass

    @abstractmethod
    def update_context(
        self,
        session_id: str,
        context: UserContext,
    ) -> None:
        pass

    @abstractmethod
    def clear_session(
        self,
        session_id: str,
    ) -> None:
        pass


class LocalMemoryStore(MemoryStore):
    """
    In-memory storage for local development.
    """

    def __init__(self):
        self._sessions: dict[str, UserContext] = {}

    def get_context(
        self,
        session_id: str,
    ) -> UserContext | None:

        return self._sessions.get(session_id)

    def update_context(
        self,
        session_id: str,
        context: UserContext,
    ) -> None:

        self._sessions[session_id] = context

    def clear_session(
        self,
        session_id: str,
    ) -> None:

        self._sessions.pop(session_id, None)


# Current memory implementation
session_memory = LocalMemoryStore()
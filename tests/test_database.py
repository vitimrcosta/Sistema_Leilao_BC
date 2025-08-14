import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from models.database import get_db, create_db_tables, SessionLocal, engine
from models.base import Base


def test_get_db():
    """Testa o ciclo de vida da sessão de banco de dados."""
    with patch("models.database.SessionLocal") as mock_session_local:
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        db_gen = get_db()
        db_session = next(db_gen)
        
        assert db_session == mock_session
        
        try:
            next(db_gen)
        except StopIteration:
            pass
        
        mock_session.close.assert_called_once()


def test_create_db_tables():
    """Testa a função de criação de tabelas."""
    with patch.object(Base.metadata, 'create_all') as mock_create_all:
        create_db_tables()
        mock_create_all.assert_called_once_with(bind=engine)
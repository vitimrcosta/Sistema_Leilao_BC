from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base

# Define o caminho para o arquivo do banco de dados SQLite
DATABASE_URL = "sqlite:///./leilao.db"

# Cria o motor do banco de dados
# connect_args={"check_same_thread": False} é necessário para SQLite com FastAPI/Uvicorn,
# mas é uma boa prática para evitar problemas de concorrência em ambientes assíncronos.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Cria uma sessão de banco de dados
# autocommit=False: não faz commit automaticamente após cada operação
# autoflush=False: não faz flush automaticamente após cada operação
# bind=engine: associa a sessão ao nosso motor de banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função utilitária para obter uma sessão de banco de dados
# Usaremos isso para gerenciar o ciclo de vida da sessão (abrir e fechar)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para criar as tabelas no banco de dados
def create_db_tables():
    # Importar todos os modelos para que o SQLAlchemy os reconheça
    from models.participante import Participante
    from models.leilao import Leilao
    from models.lance import Lance
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")
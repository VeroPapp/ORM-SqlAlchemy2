import os
from typing import Optional
from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = "sqlite:///usuarios.db"
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[Optional[int]] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

def main():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        print("\n--- 1. CREAR (Insertar registros) ---")
        user1 = User(username="juan_perez", email="juan@example.com", age=30)
        user2 = User(username="ana_gomez",  email="ana@example.com",  age=25)
        session.add_all([user1, user2])
        session.commit()
        print(f"Usuarios creados: {user1}, {user2}")

        print("\n--- 2. LEER (Consultar registros) ---")
        users = session.scalars(select(User)).all()
        print(f"Todos los usuarios: {users}")

        juan = session.scalars(
            select(User).where(User.username == "juan_perez")
        ).first()
        print(f"Usuario filtrado: {juan}")

        print("\n--- 3. ACTUALIZAR (Modificar registros) ---")
        if juan:
            juan.age = 31
            session.commit()
            print(f"Usuario actualizado: {juan} con edad {juan.age}")

        print("\n--- 4. ELIMINAR (Borrar registros) ---")
        ana = session.scalars(
            select(User).where(User.username == "ana_gomez")
        ).first()
        if ana:
            session.delete(ana)
            session.commit()
            print("Usuario 'ana_gomez' eliminado con éxito.")

        todos_restantes = session.scalars(select(User)).all()
        print(f"Usuarios remanentes en BD: {todos_restantes}")


if __name__ == "__main__":
    main()
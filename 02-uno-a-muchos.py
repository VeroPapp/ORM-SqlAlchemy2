import os
from typing import List, Optional
from sqlalchemy import create_engine, String, ForeignKey, select
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker)

DATABASE_URL = "sqlite:///blog.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)

    posts: Mapped[List["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    author: Mapped["User"] = relationship(back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post(id={self.id}, title='{self.title}', user_id={self.user_id})>"

def main():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        print("\n--- 1. CREAR REGISTROS CON RELACIÓN ---")
        autor = User(username="carlos_dev", email="carlos@example.com")
        post1 = Post(title="Introducción a SQLAlchemy 2.0", content="Contenido del post 1...")
        post2 = Post(title="Relaciones Avanzadas en ORM",   content="Contenido del post 2...")
        autor.posts.extend([post1, post2])
        session.add(autor)
        session.commit()
        print(f"Usuario creado con {len(autor.posts)} posts asociados.")

        print("\n--- 2. LEER DATOS RELACIONADOS ---")
        usuario_db = session.scalars(
            select(User).where(User.username == "carlos_dev")
        ).first()
        if usuario_db:
            print(f"Autor: {usuario_db.username}")
            for post in usuario_db.posts:
                print(f" -> Post Titulo: '{post.title}' "
                      f"(Escrito por ID de usuario: {post.user_id})")

        print("\n--- 3. ELIMINAR EN CASCADA ---")
        if usuario_db:
            session.delete(usuario_db)
            session.commit()
            print("Usuario y todos sus posts asociados han sido eliminados.")


if __name__ == "__main__":
    main()
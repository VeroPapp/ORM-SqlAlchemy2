import os
from typing import List
from sqlalchemy import (create_engine, String, ForeignKey, Table, Column, select)
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker)

DATABASE_URL = "sqlite:///blog_tags.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

post_tag_association = Table(
    "post_tag",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id",  ForeignKey("tags.id",  ondelete="CASCADE"), primary_key=True),
)

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)

    tags: Mapped[List["Tag"]] = relationship(
        secondary=post_tag_association,
        back_populates="posts",
    )

    def __repr__(self) -> str:
        return f"<Post(id={self.id}, title='{self.title}')>"

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    posts: Mapped[List["Post"]] = relationship(
        secondary=post_tag_association,
        back_populates="tags",
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}')>"

def main():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        print("\n--- 1. CREAR REGISTROS Y ASOCIACIONES ---")
        tag_python = Tag(name="Python")
        tag_db     = Tag(name="Bases de Datos")
        tag_web    = Tag(name="Desarrollo Web")

        post1 = Post(title="Tutorial de SQLAlchemy 2.0")
        post2 = Post(title="Cómo usar FastAPI con PostgreSQL")

        post1.tags.extend([tag_python, tag_db])
        post2.tags.extend([tag_python, tag_web])

        session.add_all([post1, post2])
        session.commit()
        print("Posts y etiquetas creados con sus respectivas relaciones.")

        print("\n--- 2. LEER RELACIONES DESDE EL PADRE (Post -> Tags) ---")
        p1 = session.scalars(
            select(Post).where(Post.title == "Tutorial de SQLAlchemy 2.0")
        ).first()
        if p1:
            nombres_etiquetas = [t.name for t in p1.tags]
            print(f"El post '{p1.title}' tiene las etiquetas: {nombres_etiquetas}")

        print("\n--- 3. LEER RELACIONES DESDE EL HIJO (Tag -> Posts) ---")
        t_python = session.scalars(
            select(Tag).where(Tag.name == "Python")
        ).first()
        if t_python:
            titulos_posts = [p.title for p in t_python.posts]
            print(f"La etiqueta '{t_python.name}' está presente en: {titulos_posts}")

        print("\n--- 4. ELIMINAR UNA ASOCIACIÓN ---")
        if p1 and tag_db in p1.tags:
            p1.tags.remove(tag_db)
            session.commit()
            print(f"Etiqueta '{tag_db.name}' removida del post '{p1.title}'.")
            print(f"Etiquetas restantes del post: {[t.name for t in p1.tags]}")


if __name__ == "__main__":
    main()
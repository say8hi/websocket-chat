from sqlalchemy.orm import DeclarativeBase


# Base class for SQLAlchemy models, provides custom representation for debugging
class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols: tuple = tuple()

    # Generate a string representation of the model
    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"

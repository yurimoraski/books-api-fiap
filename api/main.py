from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from api.database import Base, engine, get_db
from api import models, schemas
from sqlalchemy import func, select

app = FastAPI(title="Books Public API", version="1.0.0")


# redirect root to docs
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


# init db
Base.metadata.create_all(bind=engine)


@app.get("/api/v1/health", response_model=schemas.HealthOut)
def health(db: Session = Depends(get_db)):
    count = db.scalar(select(func.count(models.Book.id))) or 0
    return {"status": "ok", "books": count}


@app.get("/api/v1/books", response_model=List[schemas.BookOut])
def list_books(
        db: Session = Depends(get_db),
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        title: Optional[str] = None,
        category: Optional[str] = None,
        min: Optional[float] = None,
        max: Optional[float] = None,
):
    stmt = select(models.Book)
    if title:
        stmt = stmt.where(models.Book.title.ilike(f"%{title}%"))
    if category:
        stmt = stmt.where(models.Book.category.ilike(f"%{category}%"))
    if min is not None:
        stmt = stmt.where(models.Book.price >= min)
    if max is not None:
        stmt = stmt.where(models.Book.price <= max)
    stmt = stmt.offset(offset).limit(limit)
    return list(db.scalars(stmt))


@app.get("/api/v1/books/top-rated", response_model=List[schemas.BookOut])
def top_rated(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    stmt = select(models.Book).order_by(models.Book.rating.desc(), models.Book.price.desc()).limit(limit)
    return list(db.scalars(stmt))


@app.get("/api/v1/books/{book_id}", response_model=schemas.BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.get("/api/v1/categories")
def list_categories(db: Session = Depends(get_db)):
    rows = db.execute(
        select(models.Book.category, func.count()).group_by(models.Book.category)
    ).all()
    return [{"name": r[0], "count": r[1]} for r in rows]


@app.get("/api/v1/stats/overview")
def stats_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    total = db.scalar(select(func.count(models.Book.id))) or 0
    avg_price = db.scalar(select(func.avg(models.Book.price))) or 0.0
    rating_dist = dict(
        db.execute(
            select(models.Book.rating, func.count()).group_by(models.Book.rating)
        ).all()
    )
    return {"total_books": int(total), "avg_price": float(avg_price), "rating_distribution": rating_dist}

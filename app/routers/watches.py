from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.watch import WatchDB
from app.models.user import UserDB
from app.schemas.watch import WatchAutoCreate, WatchResponse, WatchUpdate
from app.services.ai_service import analyze_watch_with_ai
from app.core.security import get_current_user
from app.schemas.watch import WatchTextPrompt
from app.services.ai_service import extract_watch_info_from_text
from typing import List
from fastapi import Query
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse
from fastapi import HTTPException
import uuid
import math
from app.schemas.watch import PaginatedWatchResponse
from sqlalchemy import func
from app.schemas.watch import WatchStatistics
from app.models.watch import FavoriteDB
from app.models.watch import ReviewDB
from app.schemas.watch import ReviewCreate, ReviewResponse
from app.services.ai_service import parse_recommendation_query

router = APIRouter(
    prefix="/api/v1/watches",
    tags=["Watches"]
)


@router.post("/auto-add", response_model=WatchResponse, status_code=201)
def auto_add_watch(
        prompt_data: WatchTextPrompt,
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):

    ai_data = extract_watch_info_from_text(prompt_data.description)


    existing_watch = db.query(WatchDB).filter(
        WatchDB.user_id == current_user.id,
        WatchDB.brand.ilike(ai_data["brand"]),
        WatchDB.model_name.ilike(ai_data["model_name"])
    ).first()

    if existing_watch:
        raise HTTPException(
            status_code=409,
            detail=f"You already have {ai_data['brand']} {ai_data['model_name']} in your collection."
        )


    needs_review = ai_data.get("ai_confidence", 0.0) < 0.80


    new_watch = WatchDB(
        brand=ai_data["brand"],
        model_name=ai_data["model_name"],
        is_automatic=ai_data["is_automatic"],
        movement_type=ai_data["movement_type"],
        case_size_mm=ai_data["case_size_mm"],
        crystal_type=ai_data["crystal_type"],
        water_resistance_m=ai_data["water_resistance_m"],
        strap_type=ai_data["strap_type"],
        ai_confidence=ai_data.get("ai_confidence", 0.0),
        needs_verification=needs_review,
        user_id=current_user.id
    )

    db.add(new_watch)
    db.commit()
    db.refresh(new_watch)
    return new_watch


@router.get("/", response_model=PaginatedWatchResponse, summary="Get paginated and filtered watches")
def get_my_watches(
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
        brand: str | None = Query(None, description="Filter by brand (e.g., Seiko, Tissot)"),
        movement: str | None = Query(None, description="Filter by movement type (e.g., Automatic, Quartz)"),
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):
    """
    Advanced paginated endpoint for retrieving the user's watch collection.
    Supports filtering by brand and movement type.
    """


    query = db.query(WatchDB).filter(WatchDB.user_id == current_user.id)


    if brand:
        query = query.filter(WatchDB.brand.ilike(f"%{brand}%"))
    if movement:
        query = query.filter(WatchDB.movement_type.ilike(f"%{movement}%"))


    total_items = query.count()
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 1


    skip = (page - 1) * limit
    watches = query.offset(skip).limit(limit).all()


    return {
        "items": watches,
        "page": page,
        "limit": limit,
        "total": total_items,
        "pages": total_pages
    }
@router.get("", response_model=list[WatchResponse])
def get_all_watches(
        brand: str | None = Query(None, description="Filter by brand name"),
        movement_type: str | None = Query(None, description="Filter by movement type"),
        is_automatic: bool | None = Query(None, description="Filter by automatic status"),
        crystal_type: str | None = Query(None, description="Filter by crystal type"),
        min_case_size: float | None = Query(None, description="Minimum case size in mm"),
        max_case_size: float | None = Query(None, description="Maximum case size in mm"),
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(10, ge=1, le=100, description="Items per page"),
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):

    query = db.query(WatchDB).filter(WatchDB.user_id == current_user.id)

    if brand:
        query = query.filter(WatchDB.brand.ilike(f"%{brand}%"))
    if movement_type:
        query = query.filter(WatchDB.movement_type.ilike(f"%{movement_type}%"))
    if is_automatic is not None:
        query = query.filter(WatchDB.is_automatic == is_automatic)
    if crystal_type:
        query = query.filter(WatchDB.crystal_type.ilike(f"%{crystal_type}%"))
    if min_case_size is not None:
        query = query.filter(WatchDB.case_size_mm >= min_case_size)
    if max_case_size is not None:
        query = query.filter(WatchDB.case_size_mm <= max_case_size)

    skip = (page - 1) * limit
    watches = query.offset(skip).limit(limit).all()
    return watches


@router.get("/ai-recommend", summary="Get AI-powered watch recommendations from natural language")
def get_ai_recommendations(
        user_query: str = Query(..., description="E.g., 'Find me an automatic Seiko under 1000 dollars around 40mm'"),
        db: Session = Depends(get_db)
):



    filters = parse_recommendation_query(user_query)


    sql_query = db.query(WatchDB)


    if "brand" in filters and filters["brand"]:
        sql_query = sql_query.filter(WatchDB.brand.ilike(f"%{filters['brand']}%"))

    if "movement_type" in filters and filters["movement_type"]:
        sql_query = sql_query.filter(WatchDB.movement_type.ilike(f"%{filters['movement_type']}%"))

    if "max_price" in filters and filters["max_price"]:
        sql_query = sql_query.filter(WatchDB.price <= filters["max_price"])

    if "min_price" in filters and filters["min_price"]:
        sql_query = sql_query.filter(WatchDB.price >= filters["min_price"])

    if "max_case_size" in filters and filters["max_case_size"]:
        sql_query = sql_query.filter(WatchDB.case_size_mm <= filters["max_case_size"])

    if "min_case_size" in filters and filters["min_case_size"]:
        sql_query = sql_query.filter(WatchDB.case_size_mm >= filters["min_case_size"])


    recommended_watches = sql_query.limit(10).all()


    return {
        "ai_understood_filters": filters,
        "recommendations": recommended_watches
    }


@router.post("/{watch_id}/favorite", summary="Add a watch to favorites")
def add_to_favorites(
        watch_id: int,
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):
    """
    Adds a specific watch to the logged-in user's favorites.
    """

    watch = db.query(WatchDB).filter(WatchDB.id == watch_id).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Watch not found.")


    existing_fav = db.query(FavoriteDB).filter(
        FavoriteDB.user_id == current_user.id,
        FavoriteDB.watch_id == watch_id
    ).first()

    if existing_fav:
        raise HTTPException(status_code=400, detail="Watch is already in your favorites.")


    new_fav = FavoriteDB(user_id=current_user.id, watch_id=watch_id)
    db.add(new_fav)
    db.commit()

    return {"message": f"Successfully added '{watch.brand} {watch.model_name}' to favorites."}


@router.get("/my/favorites", response_model=List[WatchResponse], summary="Get my favorite watches")
def get_favorite_watches(
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):
    """
    Retrieves a list of watches that the logged-in user has favorited.
    Uses SQL JOIN to combine 'watches' and 'favorites' tables.
    """

    favorite_watches = db.query(WatchDB).join(
        FavoriteDB, WatchDB.id == FavoriteDB.watch_id
    ).filter(
        FavoriteDB.user_id == current_user.id
    ).all()

    return favorite_watches

@router.get("/{watch_id}", response_model=WatchResponse)
def get_watch_by_id(
        watch_id: int,
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):

    watch = db.query(WatchDB).filter(
        WatchDB.id == watch_id,
        WatchDB.user_id == current_user.id
    ).first()

    if not watch:
        raise HTTPException(status_code=404, detail="Watch not found in your collection")
    return watch


@router.post("/{watch_id}/reviews", response_model=ReviewResponse, summary="Add a review and rating to a watch")
def add_watch_review(
        watch_id: int,
        review_data: ReviewCreate,
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):
    """
    Allows a logged-in user to add a 1-5 star rating and an optional comment to a specific watch.
    """

    watch = db.query(WatchDB).filter(WatchDB.id == watch_id).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Watch not found.")


    existing_review = db.query(ReviewDB).filter(
        ReviewDB.user_id == current_user.id,
        ReviewDB.watch_id == watch_id
    ).first()

    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this watch.")


    new_review = ReviewDB(
        rating=review_data.rating,
        comment=review_data.comment,
        user_id=current_user.id,
        watch_id=watch_id
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


@router.get("/{watch_id}/reviews", response_model=List[ReviewResponse], summary="Get all reviews for a watch")
def get_watch_reviews(
        watch_id: int,
        db: Session = Depends(get_db)
):
    """
    Public endpoint to view all reviews and ratings for a specific watch.
    Does NOT require authentication.
    """

    watch = db.query(WatchDB).filter(WatchDB.id == watch_id).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Watch not found.")


    reviews = db.query(ReviewDB).filter(ReviewDB.watch_id == watch_id).all()

    return reviews


@router.get("/statistics", response_model=WatchStatistics, summary="Get collection statistics")
def get_collection_statistics(
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):
    """
    Returns aggregated statistics for the user's watch collection.
    Demonstrates SQL COUNT, AVG, and GROUP BY operations.
    """


    total = db.query(func.count(WatchDB.id)).filter(WatchDB.user_id == current_user.id).scalar() or 0


    avg_price = db.query(func.avg(WatchDB.price)).filter(WatchDB.user_id == current_user.id).scalar() or 0.0


    auto_count = db.query(func.count(WatchDB.id)).filter(
        WatchDB.user_id == current_user.id,
        WatchDB.is_automatic == True
    ).scalar() or 0


    quartz_count = db.query(func.count(WatchDB.id)).filter(
        WatchDB.user_id == current_user.id,
        WatchDB.movement_type.ilike("%quartz%")
    ).scalar() or 0


    brand_counts = db.query(WatchDB.brand, func.count(WatchDB.id)).filter(
        WatchDB.user_id == current_user.id
    ).group_by(WatchDB.brand).all()


    brand_distribution = {brand: count for brand, count in brand_counts}

    return {
        "total_watches": total,
        "average_price": round(avg_price, 2),  # Virgülden sonra 2 basamak
        "automatic_count": auto_count,
        "quartz_count": quartz_count,
        "brand_distribution": brand_distribution
    }

@router.put("/{watch_id}", response_model=WatchResponse)
def update_watch(
        watch_id: int,
        watch_update: WatchUpdate,
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):
    db_watch = db.query(WatchDB).filter(
        WatchDB.id == watch_id,
        WatchDB.user_id == current_user.id
    ).first()

    if not db_watch:
        raise HTTPException(status_code=404, detail="Watch not found in your collection")

    update_data = watch_update.model_dump(exclude_unset=True)

    if "brand" in update_data or "model_name" in update_data:
        target_brand = update_data.get("brand", db_watch.brand)
        target_model = update_data.get("model_name", db_watch.model_name)
        existing_watch = db.query(WatchDB).filter(
            WatchDB.user_id == current_user.id,
            WatchDB.id != watch_id,
            WatchDB.brand.ilike(target_brand),
            WatchDB.model_name.ilike(target_model)
        ).first()
        if existing_watch:
            raise HTTPException(status_code=409,
                                detail="Another watch with the same brand and model already exists in your collection.")

    for key, value in update_data.items():
        setattr(db_watch, key, value)

    db.commit()
    db.refresh(db_watch)
    return db_watch


@router.delete("/{watch_id}")
def delete_watch(
        watch_id: int,
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):
    watch = db.query(WatchDB).filter(
        WatchDB.id == watch_id,
        WatchDB.user_id == current_user.id
    ).first()

    if not watch:
        raise HTTPException(status_code=404, detail="Watch not found in your collection")

    db.delete(watch)
    db.commit()
    return {"message": f"Watch with ID {watch_id} has been deleted successfully from your collection."}


@router.get("/export/csv", summary="Export collection as CSV")
def export_watches_to_csv(
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):
    """
    Exports the logged-in user's watch collection as a downloadable CSV file using Pandas.
    """

    watches = db.query(WatchDB).filter(WatchDB.user_id == current_user.id).all()

    if not watches:
        raise HTTPException(status_code=404, detail="No watches found to export.")


    watch_data = []
    for w in watches:
        watch_data.append({
            "Brand": w.brand,
            "Model": w.model_name,
            "Movement": w.movement_type,
            "Case Size (mm)": w.case_size_mm,
            "Crystal Type": w.crystal_type,
            "Water Resistance (m)": w.water_resistance_m,
            "AI Confidence Score": w.ai_confidence
        })


    df = pd.DataFrame(watch_data)


    stream = BytesIO()
    df.to_csv(stream, index=False, encoding="utf-8")
    stream.seek(0)


    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=watch_collection.csv"

    return response


@router.patch("/share", summary="Toggle collection visibility and generate link")
def toggle_collection_visibility(
        is_public: bool,
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):
    """
    Updates the public visibility of the logged-in user's collection.
    Generates a unique share token if the collection is made public for the first time.
    """
    current_user.is_public = is_public


    if is_public and not current_user.share_token:
        current_user.share_token = str(uuid.uuid4())

    db.commit()
    db.refresh(current_user)


    share_url = f"/api/v1/watches/shared/{current_user.share_token}" if is_public else None

    return {
        "is_public": current_user.is_public,
        "share_token": current_user.share_token,
        "share_url": share_url,
        "message": "Your collection is now public." if is_public else "Your collection is now private."
    }


@router.get("/shared/{share_token}", summary="View a shared public collection")
def get_shared_collection(
        share_token: str,
        db: Session = Depends(get_db)
):
    """
    Public endpoint to view a user's collection using their unique share token.
    Does NOT require JWT authentication.
    """

    user = db.query(UserDB).filter(
        UserDB.share_token == share_token,
        UserDB.is_public == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Collection not found or the owner has made it private."
        )


    watches = db.query(WatchDB).filter(WatchDB.user_id == user.id).all()

    return {
        "owner": user.username,
        "total_watches": len(watches),
        "collection": watches
    }



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import pandas as pd

from .recommendation import (
    smart_recommend_books,
    get_recommendations_with_confidence,
    detect_difficulty,
    detect_intent,
    wants_practical
)


# --------------------------------------------------
# APP SETUP
# --------------------------------------------------

app = FastAPI(
    title="Cognitive Library Assistant",
    description="AI-based Library Book Recommendation System",
    version="1.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"

DATASET_PATH = BASE_DIR / "Dataset" / "books.csv"


# --------------------------------------------------
# SERVE FRONTEND
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


# --------------------------------------------------
# HOME API
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Cognitive Library Assistant API is running!"
    }


# --------------------------------------------------
# WEBSITE
# --------------------------------------------------

@app.get("/website")
def website():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class QueryRequest(BaseModel):

    query: str


# --------------------------------------------------
# RECOMMENDATION REASON
# --------------------------------------------------

def generate_reason(book, query):

    reasons = []

    difficulty = detect_difficulty(query)

    intent = detect_intent(query)

    practical = wants_practical(query)


    # Difficulty match
    if (
        difficulty
        and book["Difficulty"] == difficulty
    ):

        reasons.append(
            f"matches your {difficulty.lower()} level"
        )


    # Practical preference
    if practical:

        book_text = str(
            book["Book_Text"]
        ).lower()

        practical_words = [
            "practical",
            "examples",
            "hands-on",
            "implementation",
            "projects"
        ]

        if any(
            word in book_text
            for word in practical_words
        ):

            reasons.append(
                "contains practical learning material"
            )


    # Intent
    if intent == "Exam Preparation":

        if book["Difficulty"] == "Beginner":

            reasons.append(
                "is suitable for exam preparation"
            )


    elif intent == "Research":

        if book["Difficulty"] == "Advanced":

            reasons.append(
                "is suitable for research-oriented learning"
            )


    elif intent in [
        "Project",
        "Practical Learning"
    ]:

        reasons.append(
            "can support practical or project-based learning"
        )


    # Availability
    if book["Available"] == "Yes":

        reasons.append(
            "is currently available"
        )


    # Default
    if not reasons:

        reasons.append(
            "has strong content similarity with your query"
        )


    return (
        "This book "
        + ", ".join(reasons)
        + "."
    )


# --------------------------------------------------
# RECOMMEND BOOKS
# --------------------------------------------------

@app.post("/recommend")
def recommend_books(request: QueryRequest):

    query = request.query.strip()


    if not query:

        return {
            "error": "Please enter a search query."
        }


    recommendations, confidence = (
        get_recommendations_with_confidence(
            query,
            top_n=5
        )
    )


    # No suitable result
    if recommendations is None:

        return {
            "query": query,
            "difficulty": detect_difficulty(query),
            "intent": detect_intent(query),
            "practical_preference": wants_practical(query),
            "confidence": confidence,
            "recommendations": []
        }


    books = []


    for _, book in recommendations.iterrows():

        books.append({

            "title": str(
                book["Title"]
            ),

            "author": str(
                book["Author"]
            ),

            "subject": str(
                book["Subject"]
            ),

            "difficulty": str(
                book["Difficulty"]
            ),

            "year": int(
                book["Year"]
            ),

            "available": str(
                book["Available"]
            ),

            "score": float(
                book["Final_Score"]
            ),

            "description": str(
                book["Description"]
            ),

            "keywords": str(
                book["Keywords"]
            ),

            "reason": generate_reason(
                book,
                query
            )
        })


    return {

        "query": query,

        "difficulty": detect_difficulty(
            query
        ),

        "intent": detect_intent(
            query
        ),

        "practical_preference": wants_practical(
            query
        ),

        "confidence": float(
            confidence
        ),

        "recommendations": books
    }


# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

@app.get("/analytics")
def analytics():

    df = pd.read_csv(
        DATASET_PATH
    )


    total_books = len(df)


    available_books = int(
        (
            df["Available"]
            .astype(str)
            .str.lower()
            .eq("yes")
        ).sum()
    )


    unavailable_books = (
        total_books
        - available_books
    )


    subject_counts = (
        df["Subject"]
        .value_counts()
        .to_dict()
    )


    difficulty_counts = (
        df["Difficulty"]
        .value_counts()
        .to_dict()
    )


    year_counts = (
        df["Year"]
        .value_counts()
        .sort_index()
        .to_dict()
    )


    return {

        "total_books": total_books,

        "available_books": available_books,

        "unavailable_books": unavailable_books,

        "books_by_subject": subject_counts,

        "books_by_difficulty": difficulty_counts,

        "books_by_year": year_counts
    }
from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey, JSON, DateTime, func
from database import metadata

users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(100), nullable=False),
    Column("email", String(100), nullable=False)
)

skills_table = Table(
    "skills",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("skill_name", String(100), nullable=False, unique=True)
)

user_skills_table = Table(
    "user_skills",
    metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True)
)

courses_table = Table(
    "courses",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("course_title", String(255), nullable=False),
    Column("description", Text, nullable=False),
    Column("platform", String(100), nullable=True),
    Column("price", String(50), nullable=True),
)

embeddings_table = Table(
    "embeddings",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("course_id", Integer, ForeignKey("courses.id"), nullable=False),
    Column("embedding", JSON, nullable=False)
)

recommendation_logs_table = Table(
    "recommendation_logs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=True),
    Column("input_text", Text, nullable=False),
    Column("extracted_skills_json", JSON, nullable=True),
    Column("recommended_courses_json", JSON, nullable=False),
    Column("created_at", DateTime, server_default=func.now())
)

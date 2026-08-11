from sqlalchemy import select, insert
from database import engine
from models import courses_table, embeddings_table
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def store_course_embeddings():
    with engine.begin() as connection:
        connection.execute(embeddings_table.delete())
        
        result = connection.execute(select(courses_table))
        courses = result.fetchall()

        for course in courses:
            text_to_embed = f"{course.course_title} - {course.description}"
            vector = model.encode(text_to_embed).tolist()

            connection.execute(
                insert(embeddings_table).values(course_id=course.id, embedding=vector)
            )

        print("Course embeddings stored successfully!")

if __name__ == "__main__":
    store_course_embeddings()
import numpy as np
from sqlalchemy import select
from database import engine
from models import users_table, skills_table, courses_table, embeddings_table
from ai_service import generate_embedding

def cosine_similarity(vec1, vec2):
    """
    Compute the cosine similarity between two vectors.
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def get_recommendations_for_user(user_id: int, top_n: int = 3):
    """
    Generate course recommendations for a specific user based on their skills
    using semantic similarity (cosine similarity).
    """
    with engine.begin() as connection:
        
        # 1. Fetch user info
        user_query = select(users_table).where(users_table.c.id == user_id)
        user = connection.execute(user_query).fetchone()
        if not user:
            return f"User with ID {user_id} not found."
        
        print(f"Generating recommendations for: {user.username} (ID: {user_id})")

        # 2. Fetch user's skills
        skills_query = select(skills_table).where(skills_table.c.user_id == user_id)
        skills = connection.execute(skills_query).fetchall()
        
        if not skills:
            return "No skills found for this user."

        print(f"Found {len(skills)} skill(s) for user.")

        # 3. Retrieve embeddings for the user's skills from the database
        skill_ids = [skill.id for skill in skills]
        skill_emb_query = select(embeddings_table).where(
            (embeddings_table.c.entity_type == 'skill') & 
            (embeddings_table.c.entity_id.in_(skill_ids))
        )
        skill_embeddings = connection.execute(skill_emb_query).fetchall()
        
        if not skill_embeddings:
            return "No skill embeddings found."

        # Extract vector lists and compute user profile vector (Average Pooling)
        vectors = [np.array(emb.embedding_vector) for emb in skill_embeddings]
        user_profile_vector = np.mean(vectors, axis=0).tolist()

        # 4. Fetch all course embeddings from the database
        course_emb_query = select(embeddings_table).where(embeddings_table.c.entity_type == 'course')
        course_embeddings = connection.execute(course_emb_query).fetchall()

        # 5. Compute similarity scores between user profile and each course
        recommendations = []
        for course_emb in course_embeddings:
            score = cosine_similarity(user_profile_vector, course_emb.embedding_vector)
            
            # Fetch course details
            course_query = select(courses_table).where(courses_table.c.id == course_emb.entity_id)
            course = connection.execute(course_query).fetchone()
            
            recommendations.append({
                "course_id": course.id,
                "course_title": course.course_title,
                "description": course.description,
                "similarity_score": float(score)
            })

        # 6. Sort courses by similarity score in descending order (highest score first)
        recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Return Top N recommendations
        return recommendations[:top_n]

if __name__ == "__main__":
    # Test recommendations for User ID 1
    top_courses = get_recommendations_for_user(user_id=1, top_n=3)
    
    print("\n--- Top Recommended Courses ---")
    for idx, rec in enumerate(top_courses, 1):
        print(f"{idx}. {rec['course_title']} (Score: {rec['similarity_score']:.4f})")
        print(f"   Description: {rec['description']}")
        print("-" * 50)
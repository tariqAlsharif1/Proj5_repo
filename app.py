from flask import Flask, request, jsonify, render_template
from sqlalchemy import select, insert
from database import engine
from models import users_table, skills_table, user_skills_table, courses_table, embeddings_table, recommendation_logs_table
from sentence_transformers import SentenceTransformer
import numpy as np
import math
import ast

app = Flask(__name__)
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- 1. Skill Extraction Agent ---
def skill_extraction_agent(text):
    text_lower = text.lower()
    keywords = [
        "python", "machine learning", "cyber security", "cybersecurity", 
        "sql", "database", "ai", "programming", "security", "data science"
    ]
    
    found_skills = []
    for kw in keywords:
        if kw in text_lower or kw.replace(" ", "") in text_lower.replace(" ", ""):
            found_skills.append(kw)
            
    if "security" in text_lower or "cyber" in text_lower:
        if "cyber security" not in found_skills and "cybersecurity" not in found_skills:
            found_skills.append("cyber security")
            
    return list(set(found_skills))

# --- 2. Workflow Orchestrator ---
def run_recommendation_workflow(user_id, user_text):
    with engine.connect() as connection:
        extracted_skills = []
        
        if user_id:
            skills_query = select(skills_table.c.skill_name).select_from(
                user_skills_table.join(skills_table, user_skills_table.c.skill_id == skills_table.c.id)
            ).where(user_skills_table.c.user_id == user_id)
            result_skills = connection.execute(skills_query).fetchall()
            extracted_skills = [row.skill_name for row in result_skills]
            if extracted_skills:
                user_text = f"Skills: {', '.join(extracted_skills)}. Interest: {user_text}"

        if not user_text or not user_text.strip():
            user_text = "general programming and python"

        agent_skills = skill_extraction_agent(user_text)
        combined_skills = list(set(extracted_skills + agent_skills))

        user_vector = model.encode(user_text)

        query = select(
            courses_table.c.id,
            courses_table.c.course_title,
            courses_table.c.description,
            courses_table.c.platform,
            courses_table.c.price,
            embeddings_table.c.embedding
        ).select_from(
            courses_table.join(embeddings_table, courses_table.c.id == embeddings_table.c.course_id)
        )
        
        result = connection.execute(query).fetchall()
        recommendations = []

        for row in result:
            course_id, title, description, platform, price, db_embedding = row
            
            try:
                if isinstance(db_embedding, str):
                    db_vector = np.array(ast.literal_eval(db_embedding), dtype=float)
                else:
                    db_vector = np.array(db_embedding, dtype=float)
                
                norm_user = np.linalg.norm(user_vector)
                norm_db = np.linalg.norm(db_vector)
                
                if norm_user == 0 or norm_db == 0 or np.isnan(norm_user) or np.isnan(norm_db):
                    similarity = 0.0
                else:
                    similarity = np.dot(user_vector, db_vector) / (norm_user * norm_db)
                
                if math.isnan(similarity):
                    similarity = 0.0
            except Exception:
                similarity = 0.0

            recommendations.append({
                "course_title": title,
                "description": description,
                "platform": platform,
                "price": price,
                "similarity_score": float(similarity)
            })

        recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_courses = recommendations[:3]

        if not top_courses or top_courses[0]["similarity_score"] < 0.1:
            top_courses = [{
                "course_title": "Advanced Python and Data Structures (Default)",
                "description": "Fallback default general course.",
                "platform": "Coursera",
                "price": "$49",
                "similarity_score": 0.8
            }]

        connection.execute(
            insert(recommendation_logs_table).values(
                user_id=user_id if user_id else None,
                input_text=user_text,
                extracted_skills_json=combined_skills,
                recommended_courses_json=top_courses
            )
        )
        connection.commit()

        return combined_skills, top_courses

# --- 3. Pages Routes ---
@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/recommendations')
def recommendations_page():
    return render_template('recommendations.html')

@app.route('/courses')
def courses_page():
    with engine.connect() as connection:
        query = select(courses_table)
        result = connection.execute(query).fetchall()
        courses_list = [{"title": row.course_title, "description": row.description, "platform": row.platform, "price": row.price} for row in result]
    return render_template('courses.html', courses=courses_list)

@app.route('/skills')
def skills_page():
    user_id = request.args.get('user_id', type=int)
    skills_list = []
    username = ""

    with engine.connect() as connection:
        if user_id:
            user_query = select(users_table).where(users_table.c.id == user_id)
            user_row = connection.execute(user_query).fetchone()
            if user_row:
                username = user_row.username if hasattr(user_row, 'username') else f"User {user_row.id}"

            skills_query = select(skills_table.c.skill_name).select_from(
                user_skills_table.join(skills_table, user_skills_table.c.skill_id == skills_table.c.id)
            ).where(user_skills_table.c.user_id == user_id)
            
            result = connection.execute(skills_query).fetchall()
            skills_list = [row.skill_name for row in result]

    return render_template('skills.html', skills=skills_list, user_id=user_id, username=username)

# --- 4. APIs ---
@app.route('/api/user/register', methods=['POST'])
def register_user():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    skills_input = data.get("skills", [])

    if not username:
        return jsonify({"error": "Username is required"}), 400

    with engine.connect() as connection:
        # إدخال المستخدم الجديد وضمان عمل commit لتخزينه بقاعدة البيانات بشكل دائم
        user_result = connection.execute(
            insert(users_table).values(username=username).returning(users_table.c.id)
        )
        new_user_id = user_result.fetchone().id

        for skill_name in skills_input:
            skill_name = skill_name.strip().lower()
            if not skill_name:
                continue
                
            skill_query = select(skills_table.c.id).where(skills_table.c.skill_name == skill_name)
            skill_row = connection.execute(skill_query).fetchone()
            
            if skill_row:
                skill_id = skill_row.id
            else:
                skill_res = connection.execute(
                    insert(skills_table).values(skill_name=skill_name).returning(skills_table.c.id)
                )
                skill_id = skill_res.fetchone().id
                
            connection.execute(
                insert(user_skills_table).values(user_id=new_user_id, skill_id=skill_id)
            )
        
        # حفظ التغييرات نهائياً في قاعدة البيانات
        connection.commit()
        
        return jsonify({
            "message": "User registered successfully!",
            "user_id": new_user_id, 
            "username": username,
            "skills": skills_input
        })

@app.route('/api/user/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    with engine.connect() as connection:
        user_query = select(users_table).where(users_table.c.id == user_id)
        user_row = connection.execute(user_query).fetchone()
        
        if not user_row:
            return jsonify({"error": "User not found"}), 404
        
        skills_query = select(skills_table.c.skill_name).select_from(
            user_skills_table.join(skills_table, user_skills_table.c.skill_id == skills_table.c.id)
        ).where(user_skills_table.c.user_id == user_id)
        skills_rows = connection.execute(skills_query).fetchall()
        
        return jsonify({
            "user_id": user_row.id,
            "username": user_row.username if hasattr(user_row, 'username') else f"User {user_row.id}",
            "skills": [row.skill_name for row in skills_rows]
        })

@app.route('/api/recommend', methods=['POST'])
def recommend_api():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    user_text = data.get("user_text", "")
    
    skills, courses = run_recommendation_workflow(user_id, user_text)
    
    formatted_courses = []
    for c in courses:
        score = max(0.0, min(100.0, round(c["similarity_score"] * 100, 1)))
        formatted_courses.append({**c, "match_score": f"{score}%"})

    return jsonify({
        "user_id": user_id if user_id else "Guest", 
        "extracted_skills": skills, 
        "recommended_courses": formatted_courses
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
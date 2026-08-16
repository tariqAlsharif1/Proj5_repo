from flask import Flask, request, jsonify, render_template
from sqlalchemy import select, insert
from database import engine
from models import users_table, skills_table, user_skills_table, courses_table

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/courses')
def courses_page():
    return render_template('courses.html')

@app.route('/skills')
def skills_page():
    return render_template('skills.html')

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        with engine.connect() as conn:
            rows = conn.execute(select(users_table)).fetchall()
            users = [{"id": r.id, "username": r.username} for r in rows]
        return jsonify(users)
    except Exception as e:
        print("Error fetching users:", e)
        return jsonify([])

@app.route('/api/user/create', methods=['POST'])
def create_user():
    try:
        data = request.get_json() or {}
        username = data.get("username", "").strip()
        email = data.get("email", "user@example.com").strip()
        skills_input = data.get("skills", [])
        
        if not username:
            return jsonify({"error": "Username is required"}), 400
        
        with engine.connect() as conn:
            # إدخال المستخدم متوافقاً مع أعمدة جدول users (username و email)
            user_res = conn.execute(
                insert(users_table)
                .values(username=username, email=email)
                .returning(users_table.c.id)
            )
            user_id = user_res.fetchone().id

            # إدخال المهارات وربطها بجدول user_skills
            for skill_name in skills_input:
                skill_name = skill_name.strip()
                if not skill_name: continue
                
                skill_query = select(skills_table.c.id).where(skills_table.c.skill_name.ilike(skill_name))
                skill_row = conn.execute(skill_query).fetchone()
                
                if skill_row:
                    skill_id = skill_row.id
                else:
                    skill_res = conn.execute(insert(skills_table).values(skill_name=skill_name).returning(skills_table.c.id))
                    skill_id = skill_res.fetchone().id
                    
                conn.execute(insert(user_skills_table).values(user_id=user_id, skill_id=skill_id))
            conn.commit()
            
        return jsonify({"success": True, "user_id": user_id})
    except Exception as e:
        print("Error creating user:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/<int:user_id>/courses', methods=['GET'])
def get_user_courses(user_id):
    with engine.connect() as conn:
        # جلب مهارات المستخدم الحقيقية لتصفية الكورسات المناسبة له فقط
        skill_query = select(skills_table.c.skill_name).select_from(
            user_skills_table.join(skills_table, user_skills_table.c.skill_id == skills_table.c.id)
        ).where(user_skills_table.c.user_id == user_id)
        user_skills = [r.skill_name.lower() for r in conn.execute(skill_query).fetchall()]
        
        rows = conn.execute(select(courses_table)).fetchall()
        courses = [{"title": r.course_title, "platform": r.platform, "price": r.price} for r in rows]
        
        if not user_skills:
            matched_courses = []
        else:
            matched_courses = [c for c in courses if any(sk in c['title'].lower() for sk in user_skills)]
            
    return jsonify(matched_courses)

@app.route('/api/user/<int:user_id>/skills', methods=['GET'])
def get_skills(user_id):
    with engine.connect() as conn:
        query = select(skills_table.c.skill_name).select_from(
            user_skills_table.join(skills_table, user_skills_table.c.skill_id == skills_table.c.id)
        ).where(user_skills_table.c.user_id == user_id)
        skills = [r.skill_name for r in conn.execute(query).fetchall()]
    return jsonify({"skills": skills})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
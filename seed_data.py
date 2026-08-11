from sqlalchemy import insert
from database import engine
from models import courses_table, embeddings_table, users_table, skills_table, user_skills_table

def seed_database():
    with engine.connect() as connection:
        courses_to_seed = [
            # Python & Data Science
            {"course_title": "Advanced Python for Data Science", "description": "Deep dive into Python programming, algorithms, data structures, and Pandas/NumPy.", "platform": "Coursera", "price": "$49"},
            {"course_title": "Python for Everybody Specialization", "description": "Learn to program and analyze data with Python from scratch, covering web scraping and databases.", "platform": "Coursera", "price": "Free"},
            {"course_title": "Mastering Pandas and NumPy", "description": "Advanced data manipulation, vectorization, and numerical computations for data analysis.", "platform": "Udemy", "price": "$79"},
            
            # Web Development & Flask
            {"course_title": "Full-Stack Web Development with Flask & PostgreSQL", "description": "Build end-to-end web applications, master database migrations, Alembic, and RESTful APIs.", "platform": "Udemy", "price": "$89"},
            {"course_title": "Modern JavaScript & React Frontend Architecture", "description": "Build reactive single-page applications, manage state, and consume REST APIs.", "platform": "Coursera", "price": "$69"},
            {"course_title": "Django REST Framework & Advanced Web APIs", "description": "Design secure, scalable backend APIs with authentication, serialization, and database integrations.", "platform": "Udemy", "price": "$95"},

            # Cybersecurity & Network Defense
            {"course_title": "Cybersecurity Essentials & Network Defense", "description": "Information security fundamentals, threat analysis, network protection, and ethical hacking basics.", "platform": "Coursera", "price": "Free"},
            {"course_title": "Ethical Hacking and Penetration Testing Bootcamp", "description": "Learn vulnerability assessment, network scanning, exploit frameworks, and defensive security measures.", "platform": "Udemy", "price": "$120"},
            {"course_title": "Advanced Cryptography and System Security", "description": "Study encryption algorithms, secure protocols, digital signatures, and system hardening.", "platform": "edX", "price": "$150"},

            # Machine Learning & AI
            {"course_title": "Machine Learning Engineering with Scikit-Learn", "description": "Foundational ML models, neural networks, hyperparameter tuning, and pipeline deployment.", "platform": "Udemy", "price": "$120"},
            {"course_title": "Deep Learning Specialization with PyTorch", "description": "Build deep neural networks, convolutional networks (CNN), sequence models, and computer vision apps.", "platform": "Coursera", "price": "$79"},
            {"course_title": "Natural Language Processing and Large Language Models", "description": "Master transformer architectures, Hugging Face pipelines, LangChain, and LangGraph agent workflows.", "platform": "Coursera", "price": "$99"},
            {"course_title": "AI Agents and Workflow Orchestration", "description": "Design autonomous AI agents, tool integration, multi-step workflows, and stateful graphs.", "platform": "Udemy", "price": "$110"},

            # Cloud & DevOps
            {"course_title": "Cloud Infrastructure & AWS Solutions Architect", "description": "Manage cloud resources, scalable architectures, EC2, S3, and automated CI/CD pipelines.", "platform": "Udacity", "price": "$200"},
            {"course_title": "Docker and Kubernetes Masterclass", "description": "Containerize microservices, manage container clusters, orchestration, and automated deployments.", "platform": "Udemy", "price": "$95"},
            {"course_title": "Linux System Administration & Bash Scripting", "description": "Master Linux environments, process management, shell scripting, and server security.", "platform": "Coursera", "price": "Free"},

            # Databases & Big Data
            {"course_title": "Big Data Analytics with Apache Spark", "description": "Processing large-scale datasets, distributed computing, and data engineering pipelines.", "platform": "edX", "price": "$150"},
            {"course_title": "Database Systems & SQL Optimization", "description": "Advanced relational database theory, query optimization, indexing, and PostgreSQL vector embeddings (pgvector).", "platform": "Coursera", "price": "$39"},
            {"course_title": "NoSQL Databases with MongoDB and Redis", "description": "Design non-relational database models, high-performance caching, and document storage systems.", "platform": "Udemy", "price": "$75"}
        ]

        connection.execute(embeddings_table.delete())
        connection.execute(courses_table.delete())
        connection.execute(insert(courses_table), courses_to_seed)
        connection.commit()
        print("Data seeded successfully!")

if __name__ == "__main__":
    seed_database()
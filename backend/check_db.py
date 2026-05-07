from backend.database import SessionLocal
from backend.models import Task


db = SessionLocal()

# Check tasks
tasks = db.query(Task).all()
print(f"Total tasks: {len(tasks)}")
for task in tasks:
    print(f"  ID: {task.id}, Title: {task.title}, Date: {task.date}")

db.close()
print("\nDatabase check complete!")

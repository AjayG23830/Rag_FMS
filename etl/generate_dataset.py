"""Generate sample feedback dataset with 150 records (intentionally dirty for ETL practice)."""
import csv, random
from datetime import datetime, timedelta

PROGRAMS = ["Python Bootcamp", "React Training", "Data Engineering", "FastAPI Workshop",
            "Machine Learning 101", "DevOps Fundamentals", "Cloud Architecture", "SQL Mastery"]
NAMES = ["Rahul Sharma","Ananya Iyer","Karthik M","Priya R","Suresh B","Meera K","Vikram S",
         "Sneha P","Arjun R","Divya N","Rohan G","Kavya M","Aditya K","Pooja S","Manoj T",
         "Lakshmi V","Naveen R","Shruti J","Tarun P","Anjali D","Harish K","Nisha B"]
COMMENTS = ["Excellent training!","Very informative","Could be better","Loved it","Average experience",
            "Great content","Trainer was knowledgeable","Pace was too fast","Hands-on sessions were great",
            "Need more examples","Highly recommended","Will attend again","Not what I expected", ""]

if __name__ == "__main__":
    rows = []
    start = datetime(2024, 1, 1)
    random.seed(42)
    for i in range(150):
        name = random.choice(NAMES)
        program = random.choice(PROGRAMS)
        rating = random.choices([1,2,3,4,5,7,0], weights=[5,10,20,35,28,1,1])[0]
        comment = random.choice(COMMENTS)
        if random.random() < 0.05: name = "  " + name + "  "
        if random.random() < 0.05: comment = comment.upper()
        date = start + timedelta(days=random.randint(0, 400), hours=random.randint(0,23))
        rows.append([name, program, rating, comment, date.strftime("%Y-%m-%d %H:%M:%S")])
    rows.extend(rows[:5])  # add duplicates

    with open("datasets/feedback_raw.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["participant_name","program_name","rating","comments","submitted_at"])
        w.writerows(rows)
    print(f"Generated {len(rows)} feedback records → datasets/feedback_raw.csv")

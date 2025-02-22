import json
from datetime import datetime, timedelta
import os

def load_study_data():
    if not os.path.exists('study_data.json'):
        return []
    try:
        with open('study_data.json', 'r') as f:
            return json.load(f)
    except:
        return []

def save_study_data(data):
    with open('study_data.json', 'w') as f:
        json.dump(data, f)

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def get_subject_stats(study_data, subject=None):
    if not study_data:
        return 0, 0

    if subject:
        subject_sessions = [session for session in study_data if session['subject'] == subject]
    else:
        subject_sessions = study_data

    total_time = sum(session['duration'] for session in subject_sessions)
    avg_time = total_time / len(subject_sessions) if subject_sessions else 0

    return total_time, avg_time

def get_daily_quote():
    """Get a motivational quote about studying or time."""
    quotes = [
        "Time you enjoy wasting is not wasted time.",
        "The journey of a thousand miles begins with one step.",
        "Focus on progress, not perfection.",
        "Every minute spent learning is an investment in your future.",
        "Small progress is still progress.",
        "The best time to start was yesterday. The next best time is now."
    ]
    # Use the day of the year as an index to ensure the same quote all day
    day_of_year = datetime.now().timetuple().tm_yday
    return quotes[day_of_year % len(quotes)]
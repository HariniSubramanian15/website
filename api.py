import json

# This function will act as a simple API endpoint that returns JSON data.
def get_tutor_data():
    """
    Returns a JSON string containing sample tutor data.
    """
    tutors = [
        {
            "id": 1,
            "name": "Jane Doe",
            "specializations": ["Math", "Physics"],
            "experience": 5,
            "rate_hourly": 25
        },
        {
            "id": 2,
            "name": "John Smith",
            "specializations": ["English", "History"],
            "experience": 10,
            "rate_hourly": 30
        },
        {
            "id": 3,
            "name": "Emily Chen",
            "specializations": ["Computer Science"],
            "experience": 3,
            "rate_hourly": 40
        }
    ]
    return json.dumps(tutors)

# Example usage:
# data = get_tutor_data()
# print(data)

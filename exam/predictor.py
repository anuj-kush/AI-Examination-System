import numpy as np
from sklearn.linear_model import LinearRegression
from .models import Result

def predict_next_score(user):
    # Fetch all results for this specific student, ordered by date
    results = Result.objects.filter(student=user).order_by('date')
    
    if results.count() < 2:
        return None  # We need at least 2 exams to find a trend

    # Prepare data: X = Exam Index (1, 2, 3...), Y = Scores
    X = np.array(range(len(results))).reshape(-1, 1)
    y = np.array([r.marks for r in results])

    # Initialize and train the model
    model = LinearRegression()
    model.fit(X, y)

    # Predict the score for the NEXT exam index
    next_exam_index = np.array([[len(results)]])
    prediction = model.predict(next_exam_index)

    # Return the predicted score, capped at 100% or total marks
    predicted_value = round(float(prediction[0]), 2)
    return max(0, predicted_value) # Ensure no negative predictions
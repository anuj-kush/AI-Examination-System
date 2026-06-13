from dotenv import load_dotenv
import google.generativeai as genai
import os
from .models import Result

load_dotenv()

# Configure once
genai.configure(api_key=os.getenv("AIzaSyCfuU0057dGe3uR1qW_mwPoG5Fyx73ZdCg"))

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config={
        "temperature": 0.3,
        "max_output_tokens": 150,
    }
)


def get_ai_tutor_response(user, user_message, chat_history=None, exam_mode=False):

    user_message_lower = user_message.lower()

    # 🔹 Detect if user is asking about performance
    performance_keywords = ["performance", "result", "score", "marks", "progress"]

    is_performance_query = any(word in user_message_lower for word in performance_keywords)

    # 🔹 Fetch all results
    results = Result.objects.filter(student=user)

    performance_text = ""
    if results.exists():
        performance_text = "Student Performance:\n"

        for r in results:
            percentage = (r.marks / r.exam.total_marks) * 100

            performance_text += (
                f"- {r.exam.course_name}: {r.marks}/{r.exam.total_marks} "
                f"({round(percentage, 2)}%)\n"
            )

    # 🔹 Chat history (memory)
    history_text = ""
    if chat_history:
        for msg in chat_history[-5:]:
            role = "Student" if msg["role"] == "user" else "Tutor"
            history_text += f"{role}: {msg['content']}\n"

    # 🔹 Exam mode rules
    exam_rule = ""
    if exam_mode:
        exam_rule = """
IMPORTANT:
- Student is in exam
- Do NOT give direct answers
- Only give hints or steps
"""

    # 🔥 PERFORMANCE PROMPT
    if is_performance_query and results.exists():

        prompt = f"""
You are an AI Academic Tutor.

{performance_text}

TASK:
1. Analyze subject-wise performance
2. Identify strong subjects (high %)
3. Identify weak subjects (low %)
4. Give improvement tips for weak subjects
5. Keep answer short (max 100 words)
6. Use simple student-friendly language

ANSWER:
"""

    # 🔥 NORMAL TUTOR PROMPT
    else:
        prompt = f"""
You are a helpful AI Tutor.

{history_text}

{exam_rule}

INSTRUCTIONS:
- Keep answer under 80 words
- Use simple explanation
- Explain step-by-step
- Give examples if needed

STUDENT QUESTION:
{user_message}

TUTOR RESPONSE:
"""

    # 🔹 Generate Response
    try:
        response = model.generate_content(prompt)

        if response and hasattr(response, "text"):
            return response.text.strip()
        else:
            return "I couldn't understand. Please ask again."

    except Exception as e:
        print("AI Error:", e)
        return "⚠️ AI service temporarily unavailable. Try again."
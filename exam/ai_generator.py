import PyPDF2
import google.generativeai as genai
import json
import re

# Replace with your actual Gemini API Key
genai.configure(api_key="AIzaSyCfuU0057dGe3uR1qW_mwPoG5Fyx73ZdCg")

def clean_json_response(text):
    """
    Cleans the AI response to ensure it only contains valid JSON.
    Removes markdown backticks like ```json ... ```
    """
    try:
        # Use regex to find content between [ ] if AI adds extra text
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(text)
    except Exception as e:
        print(f"JSON Parsing Error: {e}")
        return None

def generate_questions_from_ai(topic, num_questions=5):
    """Generates questions based on a text topic."""
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    Generate {num_questions} high-quality multiple choice questions about '{topic}'.
    Return the response ONLY as a JSON list.
    Format: [
        {{"question": "...", "option1": "...", "option2": "...", "option3": "...", "option4": "...", "answer": "Option1"}},
        ...
    ]
    Ensure 'answer' is exactly one of 'Option1', 'Option2', 'Option3', or 'Option4'.
    """
    
    try:
        response = model.generate_content(prompt)
        return clean_json_response(response.text)
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def generate_questions_from_pdf(pdf_file, num_questions=5):
    """Extracts text from a PDF and generates questions."""
    try:
        # 1. Extract Text
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text()
        
        # Limit context to avoid token limits (first 8000 chars)
        text_sample = text_content[:8000]

        # 2. Call AI
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""
        Analyze the following text and generate {num_questions} MCQ questions based on it.
        Return the response ONLY as a JSON list.
        
        TEXT: {text_sample}

        Format: [
            {{"question": "...", "option1": "...", "option2": "...", "option3": "...", "option4": "...", "answer": "Option1"}},
            ...
        ]
        """
        
        response = model.generate_content(prompt)
        return clean_json_response(response.text)
    except Exception as e:
        print(f"PDF Processing Error: {e}")
        return None
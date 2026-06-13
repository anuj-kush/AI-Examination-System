import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("AIzaSyDp4mExUgVM_NIwlsyTpakBelkPo_AoPRQ"))

model = genai.GenerativeModel("gemini-1.5-flash")
print(model.generate_content("Say OK").text)

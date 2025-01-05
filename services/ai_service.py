import google.generativeai as genai

class AIService:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name='gemini-1.5-flash')

    def generate_response(self, message):
        try:
            response = self.model.generate_content(message)
            return response.text
        except Exception as e:
            return f"Error generating AI response: {str(e)}"
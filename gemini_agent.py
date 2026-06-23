import google.generativeai as genai

genai.configure(api_key="")

def simple_agent(user_input):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    response = model.generate_content(user_input)
    
    return response.text

# Run
while True:
    user_input = input("You: ")
    print("Agent:", simple_agent(user_input))

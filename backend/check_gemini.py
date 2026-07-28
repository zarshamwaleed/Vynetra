from google import genai

API_KEY = "YOUR_REAL_AQ_KEY"

print("Key starts with:", API_KEY[:6])

client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Reply with the single word: WORKING"
)

print("SUCCESS:")
print(response.text)

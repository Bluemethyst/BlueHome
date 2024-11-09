import os
import openai
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Function to capture microphone input
def listen_for_wake_word(wake_word="hey assistant"):
    with sr.Microphone() as source:
        print("Listening for wake word...")
        while True:
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio).lower()
                if wake_word in text:
                    print("Wake word detected!")
                    return
            except sr.UnknownValueError:
                continue

# Function to capture user query
def listen_for_query():
    with sr.Microphone() as source:
        print("Listening for your query...")
        audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio)
            print(f"You said: {query}")
            return query
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None

# Function to get response from OpenAI
def get_openai_response(query):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful home assistant. try to keep your answers short and quick unless specifically asked for more information."},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content

# Function to speak out the response
def speak_response(response):
    engine.say(response)
    engine.runAndWait()

# Main function
def main():
    while True:
        listen_for_wake_word()
        query = listen_for_query()
        if query:
            response = get_openai_response(query)
            print(f"Assistant: {response}")
            speak_response(response)

if __name__ == "__main__":
    main()
import os
from pathlib import Path
from openai import OpenAI
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play

# Initialize OpenAI client
client = OpenAI()

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
def get_openai_response(query, memory):
    messages = [
        {"role": "system", "content": "You are a helpful home assistant. keep your answers short and quick unless specifically asked for more information."}
    ]
    messages.extend(memory)
    messages.append({"role": "user", "content": query})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True  # Enable streaming
    )
    
    full_response = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            full_response += content
            print(content, end="", flush=True)  # Print the streamed text
    
    return full_response

# Function to speak out the response using OpenAI's Whisper
def speak_response(response, voice):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    
    response_audio = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=response
    )
    
    # Stream the audio to a file
    response_audio.stream_to_file(speech_file_path)
    
    # Play the streamed audio
    audio_segment = AudioSegment.from_file(speech_file_path, format="mp3")
    play(audio_segment)

# Main function
def main():
    voices = ["echo", "alloy", "fable", "onyx", "nova", "shimmer"]
    ai_voice = "alloy"  # Default voice
    memory = []

    while True:
        try:
            listen_for_wake_word()
            conversation_active = True
            while conversation_active:
                query = listen_for_query()
                if query:
                    if "thanks assistant" in query.lower():
                        print("Ending conversation and waiting for wake word...")
                        conversation_active = False
                        memory.clear()
                    elif "change voice" in query.lower():
                        found_voice = False
                        for voice in voices:
                            if voice in query.lower():
                                ai_voice = voice
                                found_voice = True
                                print(f"Voice changed to {ai_voice}")
                                speak_response(f"Voice changed to {ai_voice} successfully", ai_voice)
                                break
                        
                        if not found_voice:
                            speak_response("No voice found with that name", ai_voice)
                    
                    else:
                        response = get_openai_response(query, memory)
                        memory.append({"role": "assistant", "content": response})
                        speak_response(response, ai_voice)
        except KeyboardInterrupt:
            os.remove("speech.mp3")
            print("Exiting cleanly...")
            os._exit(0)

if __name__ == "__main__":
    main()
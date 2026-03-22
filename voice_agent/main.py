import asyncio
from dotenv import load_dotenv
import speech_recognition as sr
from google import genai
import edge_tts
import pygame
import io
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai_client = genai.Client(api_key=api_key)

async def tts(speech: str):
    communicate = edge_tts.Communicate(speech, "en-US-AriaNeural")
    audio_data = b""
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.init()
    
    sound = pygame.mixer.Sound(io.BytesIO(audio_data))
    sound.play()
    
    while pygame.mixer.get_busy():
        await asyncio.sleep(0.1)
    
    pygame.mixer.quit()

def main():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 2

        SYSTEM_PROMPT = f"""
                You're an expert voice agent. You are given the transcript of what
                user has said using voice.
                You need to output as if you are a voice agent and whatever you speak
                will be converted back to audio using AI and played back to user.
            """

        messages = [
            { "role": "system", "content": SYSTEM_PROMPT },
        ]

        while True:
            print("\nSpeak Something...")
            audio = r.listen(source)

            print("Processing Audio... (STT)")
            
            try:
                stt = r.recognize_google(audio)
                print("You Said:", stt)
            except sr.UnknownValueError:
                print("Could not understand audio, please speak again")
                continue
            except sr.RequestError:
                print("Speech recognition service error, please try again")
                continue

            messages.append({ "role": "user", "content": stt })

            prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    prompt += f"System: {msg['content']}\n\n"
                elif msg["role"] == "user":
                    prompt += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"
            
            prompt += "Assistant: "
            
            response = genai_client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )

            print("AI Response:", response.text)
            
            messages.append({ "role": "assistant", "content": response.text })
            
            asyncio.run(tts(speech=response.text))

if __name__ == "__main__":
    main()
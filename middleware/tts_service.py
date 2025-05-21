# middleware/services/tts_service.py
from google.cloud import texttospeech
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
import base64
import random

class TTSService:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()
        self.last_announcement = None
        self.announcement_interval = timedelta(hours=1)
        
        # Configure voice settings
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-C",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=1.0,
            pitch=0.0
        )
    
    
    
    def generate_announcement(self, weather_data: Dict[str, Any], sensor_data: Dict[str, Any]) -> Optional[str]:
        """Generate appropriate announcement based on conditions"""
        announcements = []
        
        
        # General weather announcement
        temp = weather_data.get('temperature', 20)
        weather_desc = weather_data.get('description', 'clear')
        announcements.append(f"Hi! The temperature outside is {temp:.1f} degrees with {weather_desc}.")

        if 'forecast' in weather_data:
            for forecast in weather_data['forecast'][:8]:  # Next 24 hours
                if forecast.get('rain_probability', 0) > 50:
                    announcements.append("Good morning! It looks like it might rain today. Don't forget to take an umbrella.")
                    break
        
        # Choose a random announcement from the list
        if announcements:
            self.last_announcement = datetime.now()
            return random.choice(announcements)
        
        return None
    
    def text_to_speech(self, text: str, filename: str = "static/audio.wav") -> Optional[str]:
        """Convert text to speech using Google Cloud TTS and save to .wav file"""
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )
            
            # Créer le dossier si nécessaire
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Sauvegarder le fichier audio au format LINEAR16 (.wav)
            with open(filename, "wb") as out:
                out.write(response.audio_content)
            
            # Retourne le chemin relatif vers le fichier audio
            return filename
            
        except Exception as e:
            print(f"TTS Error: {str(e)}")
            return None
    
   
    

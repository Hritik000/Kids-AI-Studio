from abc import ABC, abstractmethod
import os
import wave
import struct
import math
from typing import Dict, Any

class BaseTTSProvider(ABC):
    @abstractmethod
    async def generate_speech(self, text: str, project_id: str, scene_number: int) -> str:
        """Synthesizes speech audio file and returns local file path or URL."""
        pass

class MockTTSProvider(BaseTTSProvider):
    async def generate_speech(self, text: str, project_id: str, scene_number: int) -> str:
        """Generates a clean silent/beep WAV audio file corresponding to narration length."""
        output_dir = f"/tmp/kidsAI/{project_id}"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/scene_{scene_number}.wav"
        
        # Calculate duration based on word count (~3 words per second)
        word_count = len(text.split())
        duration = max(3, math.ceil(word_count / 3))
        sample_rate = 22050
        num_samples = duration * sample_rate

        with wave.open(file_path, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Generate soft warm audio tone
            frequency = 440.0  # A4 note
            for i in range(num_samples):
                sample = int(1000 * math.sin(2 * math.pi * frequency * i / sample_rate))
                wav_file.writeframes(struct.pack('<h', sample))
                
        return file_path

class TTSAdapter:
    def __init__(self, provider: BaseTTSProvider | None = None):
        self.provider = provider or MockTTSProvider()

    async def generate_speech(self, text: str, project_id: str, scene_number: int) -> str:
        return await self.provider.generate_speech(text, project_id, scene_number)

tts_adapter = TTSAdapter()

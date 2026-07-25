from typing import Dict, List
from app.models.copilot import AIModelConfigItem

models_db: Dict[str, AIModelConfigItem] = {}

class ModelManagerService:
    @staticmethod
    def initialize_models():
        if not models_db:
            m1 = AIModelConfigItem(
                model_id="mod_flux_dev",
                provider="FLUX",
                model_type="IMAGE",
                display_name="FLUX.1-dev (3D Pixar Engine)",
                latency_ms=1240.0,
                cost_per_unit=0.003,
                status="OPERATIONAL",
                is_default=True
            )
            m2 = AIModelConfigItem(
                model_id="mod_wan_22",
                provider="Wan 2.2",
                model_type="ANIMATION",
                display_name="Wan 2.2 14B Video Generator",
                latency_ms=3400.0,
                cost_per_unit=0.015,
                status="OPERATIONAL",
                is_default=True
            )
            m3 = AIModelConfigItem(
                model_id="mod_kokoro_tts",
                provider="Kokoro",
                model_type="VOICE",
                display_name="Kokoro 82M Kid TTS Voice",
                latency_ms=280.0,
                cost_per_unit=0.0005,
                status="OPERATIONAL",
                is_default=True
            )
            models_db[m1.model_id] = m1
            models_db[m2.model_id] = m2
            models_db[m3.model_id] = m3

    @staticmethod
    def list_models() -> List[AIModelConfigItem]:
        ModelManagerService.initialize_models()
        return list(models_db.values())

    @staticmethod
    def update_model_status(model_id: str, status: str) -> AIModelConfigItem:
        ModelManagerService.initialize_models()
        if model_id in models_db:
            models_db[model_id].status = status
            return models_db[model_id]
        raise ValueError(f"Model '{model_id}' not found.")

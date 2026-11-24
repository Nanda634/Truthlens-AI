"""
AIImageDetector - spec section 14.
Pluggable interface for an AI-generated-image classifier (e.g. a fine-tuned
ConvNeXt/ViT). No trained model ships with this project. Per spec section 59,
this module NEVER fabricates a prediction: if MODEL_IMAGE_PATH is not
configured, it reports model_status="unavailable" and returns prediction=None.
"""
import os
from app.config import settings


class AIImageDetector:
    def __init__(self):
        self.model_path = settings.MODEL_IMAGE_PATH
        self.model_loaded = bool(self.model_path) and os.path.exists(self.model_path)
        self.model_name = "convnext-ai-image-detector" if self.model_loaded else None
        self.model_version = "unconfigured"

    def predict(self, image_path: str) -> dict:
        if not self.model_loaded:
            return {
                "model_status": "unavailable",
                "prediction": None,
                "ai_generated_probability": None,
                "human_generated_probability": None,
                "message": "Specialized AI-generation model is not configured.",
            }
        # Real inference would run here (e.g. torch model forward pass).
        # Left unimplemented intentionally: no model weights ship with this project.
        raise NotImplementedError("Configure MODEL_IMAGE_PATH and implement inference.")

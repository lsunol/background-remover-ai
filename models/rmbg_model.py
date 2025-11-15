from PIL import Image
import torch
from torchvision import transforms
from transformers import AutoModelForImageSegmentation
from typing import Tuple, Optional
import logging
import os
from huggingface_hub.errors import GatedRepoError, RepositoryNotFoundError, HFValidationError

from .base_model import BackgroundRemovalModel

logger = logging.getLogger(__name__)

class RMBGModel(BackgroundRemovalModel):
    """RMBG model implementation for background removal"""
    
    def __init__(self, model_name: str = "rmbg-2.0", device: Optional[str] = None):
        super().__init__(model_name, device)
        
        # Model configurations
        self.model_configs = {
            "rmbg-1.4": {
                "hf_model_name": "briaai/RMBG-1.4",
                "image_size": (1024, 1024),
                "normalize_params": ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            },
            "rmbg-2.0": {
                "hf_model_name": "briaai/RMBG-2.0",
                "image_size": (1024, 1024),
                "normalize_params": ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            }
        }
        
        if model_name not in self.model_configs:
            raise ValueError(f"Unsupported model: {model_name}. Available models: {list(self.model_configs.keys())}")
        
        self.config = self.model_configs[model_name]
        self.transform = None
    
    async def load_model(self) -> None:
        """Load the RMBG model with optional Hugging Face auth token support"""
        try:
            logger.info(f"Loading {self.model_name} model (hub: {self.config['hf_model_name']}) ...")

            hf_token = os.getenv("HUGGINGFACE_HUB_TOKEN") or os.getenv("HF_TOKEN")

            # Load model from Hugging Face. use_auth_token deprecated in newer transformers but still accepted; fallback to env var.
            load_kwargs = {"trust_remote_code": True}
            if hf_token:
                load_kwargs["use_auth_token"] = hf_token  # type: ignore[arg-type]

            self.model = AutoModelForImageSegmentation.from_pretrained(
                self.config["hf_model_name"],
                **load_kwargs
            ).eval().to(self.device)

            # Setup transforms
            self.transform = transforms.Compose([
                transforms.Resize(self.config["image_size"]),
                transforms.ToTensor(),
                transforms.Normalize(*self.config["normalize_params"])
            ])

            self.is_loaded = True
            logger.info(f"{self.model_name} model loaded successfully on {self.device}")

        except (GatedRepoError, RepositoryNotFoundError, HFValidationError) as e:
            logger.error(f"Hugging Face access error for {self.model_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading {self.model_name} model: {str(e)}")
            raise
    
    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image for RMBG model"""
        if not self.transform:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply transforms and add batch dimension
        transformed = self.transform(image)
        if not isinstance(transformed, torch.Tensor):
            raise RuntimeError("Transform did not return a tensor")
        input_tensor = transformed.unsqueeze(0).to(self.device)
        return input_tensor
    
    def postprocess_prediction(self, prediction: torch.Tensor, original_image: Image.Image) -> Tuple[Image.Image, Image.Image]:
        """
        Postprocess RMBG model prediction
        Returns: (image_with_transparent_bg, mask)
        """
        # Extract prediction and apply sigmoid
        pred = prediction[-1].sigmoid().cpu()
        pred = pred[0].squeeze()
        
        # Convert to PIL Image
        pred_pil = transforms.ToPILImage()(pred)
        
        # Resize mask to original image size
        mask = pred_pil.resize(original_image.size, Image.Resampling.LANCZOS)
        
        # Convert original image to RGBA
        if original_image.mode != 'RGBA':
            result_image = original_image.convert('RGBA')
        else:
            result_image = original_image.copy()
        
        # Apply mask as alpha channel
        result_image.putalpha(mask)
        
        return result_image, mask
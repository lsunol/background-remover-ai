from abc import ABC, abstractmethod
from PIL import Image
import torch
from typing import Dict, Any, Tuple, Optional
import base64
import io

class BackgroundRemovalModel(ABC):
    """Base class for background removal models"""
    
    def __init__(self, model_name: str, device: Optional[str] = None):
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.is_loaded = False
    
    @abstractmethod
    async def load_model(self) -> None:
        """Load the model"""
        pass
    
    @abstractmethod
    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image for the model"""
        pass
    
    @abstractmethod
    def postprocess_prediction(self, prediction: torch.Tensor, original_image: Image.Image) -> Tuple[Image.Image, Image.Image]:
        """
        Postprocess model prediction
        Returns: (image_with_transparent_bg, mask)
        """
        pass
    
    async def predict(self, image: Image.Image) -> torch.Tensor:
        """Run model prediction"""
        if not self.is_loaded or self.model is None:
            raise RuntimeError(f"Model {self.model_name} is not loaded")
        
        input_tensor = self.preprocess_image(image)
        
        with torch.no_grad():
            prediction = self.model(input_tensor)
        
        return prediction
    
    async def remove_background(self, image: Image.Image, include_mask: bool = False) -> Dict[str, Any]:
        """
        Complete background removal pipeline
        """
        original_size = image.size
        
        # Predict
        prediction = await self.predict(image)
        
        # Postprocess
        result_image, mask = self.postprocess_prediction(prediction, image)
        
        # Convert to base64
        result_base64 = self._image_to_base64(result_image)
        
        response = {
            "image_base64": result_base64,
            "original_size": original_size,
            "processed_size": result_image.size,
            "device_used": self.device
        }
        
        if include_mask:
            mask_base64 = self._image_to_base64(mask)
            response["mask_base64"] = mask_base64
        
        return response
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffer = io.BytesIO()
        
        # Save as PNG to preserve transparency
        if image.mode in ('RGBA', 'LA'):
            image.save(buffer, format='PNG')
        else:
            image.save(buffer, format='JPEG', quality=95)
        
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return image_base64
    
    def unload(self) -> None:
        """Unload model to free memory"""
        if self.model is not None:
            del self.model
            self.model = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.is_loaded = False
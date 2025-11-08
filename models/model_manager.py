from typing import Dict, List
from PIL import Image
import logging

from .base_model import BackgroundRemovalModel
from .rmbg_model import RMBGModel

logger = logging.getLogger(__name__)

class ModelManager:
    """Manager for multiple background removal models"""
    
    def __init__(self):
        self.loaded_models: Dict[str, BackgroundRemovalModel] = {}
        
        # Registry of available models
        self.model_registry = {
            "rmbg-1.4": {
                "class": RMBGModel,
                "description": "RMBG v1.4 - Bilateral Reference for High-Resolution Dichotomous Image Segmentation"
            },
            "rmbg-2.0": {
                "class": RMBGModel,
                "description": "RMBG v2.0 - Latest version with improved performance"
            }
        }
    
    def list_available_models(self) -> List[str]:
        """List all available model names"""
        return list(self.model_registry.keys())
    
    def list_loaded_models(self) -> List[str]:
        """List currently loaded model names"""
        return list(self.loaded_models.keys())
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Check if a model is currently loaded"""
        return model_name in self.loaded_models and self.loaded_models[model_name].is_loaded
    
    async def load_model(self, model_name: str) -> None:
        """Load a specific model"""
        if model_name not in self.model_registry:
            raise ValueError(f"Unknown model: {model_name}. Available models: {self.list_available_models()}")
        
        if self.is_model_loaded(model_name):
            logger.info(f"Model {model_name} is already loaded")
            return
        
        try:
            # Get model class and create instance
            model_class = self.model_registry[model_name]["class"]
            model_instance = model_class(model_name)
            
            # Load the model
            await model_instance.load_model()
            
            # Store in loaded models
            self.loaded_models[model_name] = model_instance
            
            logger.info(f"Model {model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            raise
    
    def unload_model(self, model_name: str) -> None:
        """Unload a specific model to free memory"""
        if model_name not in self.loaded_models:
            logger.warning(f"Model {model_name} is not loaded")
            return
        
        try:
            self.loaded_models[model_name].unload()
            del self.loaded_models[model_name]
            logger.info(f"Model {model_name} unloaded successfully")
            
        except Exception as e:
            logger.error(f"Error unloading model {model_name}: {str(e)}")
            raise
    
    def unload_all_models(self) -> None:
        """Unload all models to free memory"""
        model_names = list(self.loaded_models.keys())
        for model_name in model_names:
            self.unload_model(model_name)
    
    async def remove_background(self, image: Image.Image, model_name: str = "rmbg-2.0", include_mask: bool = False) -> dict:
        """
        Remove background using specified model
        """
        if not self.is_model_loaded(model_name):
            raise RuntimeError(f"Model {model_name} is not loaded. Load it first using load_model()")
        
        model = self.loaded_models[model_name]
        result = await model.remove_background(image, include_mask)
        
        # Add model info to result
        result["model_info"] = {
            "name": model_name,
            "description": self.model_registry[model_name]["description"]
        }
        
        return result
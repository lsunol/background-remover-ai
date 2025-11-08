from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import torch
import io
import base64
from typing import Dict, Any, Optional
import logging
from contextlib import asynccontextmanager
import os

from models.model_manager import ModelManager
from models.base_model import BackgroundRemovalModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model manager
model_manager: Optional[ModelManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global model_manager
    # Startup
    logger.info("Loading models...")
    model_manager = ModelManager()
    await model_manager.load_model("rmbg-2.0")
    logger.info("Models loaded successfully")
    
    yield
    
    # Shutdown
    if model_manager:
        model_manager.unload_all_models()
        logger.info("All models unloaded")

app = FastAPI(
    title="Background Remover API",
    description="API for removing backgrounds from images using multiple AI models",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Health check endpoint"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")
    return {"message": "Background Remover API is running", "available_models": model_manager.list_available_models()}

@app.get("/models")
async def list_models():
    """List all available models"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")
    return {
        "available_models": model_manager.list_available_models(),
        "loaded_models": model_manager.list_loaded_models()
    }

@app.post("/remove-background")
async def remove_background(
    file: UploadFile = File(...),
    model_name: str = "rmbg-2.0",
    include_mask: bool = False,
    return_metadata: bool = True
):
    """
    Remove background from an uploaded image
    
    Args:
        file: Image file to process
        model_name: Name of the model to use
        include_mask: Whether to include the mask in the response
        return_metadata: Whether to include metadata in the response
    """
    try:
        if not model_manager:
            raise HTTPException(status_code=503, detail="Model manager not initialized")
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Ensure model is loaded
        if not model_manager.is_model_loaded(model_name):
            logger.info(f"Loading model {model_name}")
            await model_manager.load_model(model_name)
        
        # Process image
        result = await model_manager.remove_background(
            image=image,
            model_name=model_name,
            include_mask=include_mask
        )
        
        # Prepare response
        response_data = {
            "success": True,
            "result_image": result["image_base64"]
        }
        
        if include_mask:
            response_data["mask"] = result["mask_base64"]
        
        if return_metadata:
            response_data["metadata"] = {
                "model_used": model_name,
                "original_size": result["original_size"],
                "processed_size": result["processed_size"],
                "device_used": result["device_used"]
            }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/load-model/{model_name}")
async def load_model_endpoint(model_name: str):
    """Load a specific model"""
    try:
        if not model_manager:
            raise HTTPException(status_code=503, detail="Model manager not initialized")
        await model_manager.load_model(model_name)
        return {"message": f"Model {model_name} loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

@app.delete("/unload-model/{model_name}")
async def unload_model_endpoint(model_name: str):
    """Unload a specific model to free memory"""
    try:
        if not model_manager:
            raise HTTPException(status_code=503, detail="Model manager not initialized")
        model_manager.unload_model(model_name)
        return {"message": f"Model {model_name} unloaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unloading model: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Read configuration from environment variables
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("API_DEBUG", "false").lower() == "true"
    
    uvicorn.run(app, host=host, port=port, log_level="info")
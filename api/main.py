# Add parent directory to path BEFORE importing models (when running directly)
import sys
from pathlib import Path
_api_dir = Path(__file__).parent
_project_root = _api_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
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

# Rate limiter configuration
ENABLE_RATE_LIMIT = os.getenv("ENABLE_RATE_LIMIT", "true").lower() == "true"
limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"]) if ENABLE_RATE_LIMIT else None


def apply_rate_limit(limit: str):
    if ENABLE_RATE_LIMIT and limiter:
        return limiter.limit(limit)

    def decorator(func):
        return func

    return decorator

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

# Add rate limiter to app if enabled
if limiter:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/models/{model_name}/info")
async def get_model_info(model_name: str):
    """Get detailed information about a specific model including citations"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")
    
    # Model metadata with citations
    model_citations = {
        "rmbg-1.4": {
            "name": "RMBG-1.4",
            "full_name": "Remove Background Model v1.4",
            "description": "Bilateral Reference for High-Resolution Dichotomous Image Segmentation",
            "authors": ["Zheng, Peng", "Gao, Dehong", "Fan, Deng-Ping", "Liu, Li", "Laaksonen, Jorma", "Ouyang, Wanli", "Sebe, Nicu"],
            "year": 2024,
            "journal": "CAAI Artificial Intelligence Research",
            "huggingface": "briaai/RMBG-1.4",
            "citation": """@article{BiRefNet,
  title={Bilateral Reference for High-Resolution Dichotomous Image Segmentation},
  author={Zheng, Peng and Gao, Dehong and Fan, Deng-Ping and Liu, Li and Laaksonen, Jorma and Ouyang, Wanli and Sebe, Nicu},
  journal={CAAI Artificial Intelligence Research},
  year={2024}
}""",
            "license": "Check Hugging Face model page",
            "attribution_required": True
        },
        "rmbg-2.0": {
            "name": "RMBG-2.0",
            "full_name": "Remove Background Model v2.0",
            "description": "Bilateral Reference for High-Resolution Dichotomous Image Segmentation - Latest version",
            "authors": ["Zheng, Peng", "Gao, Dehong", "Fan, Deng-Ping", "Liu, Li", "Laaksonen, Jorma", "Ouyang, Wanli", "Sebe, Nicu"],
            "year": 2024,
            "journal": "CAAI Artificial Intelligence Research",
            "huggingface": "briaai/RMBG-2.0",
            "citation": """@article{BiRefNet,
  title={Bilateral Reference for High-Resolution Dichotomous Image Segmentation},
  author={Zheng, Peng and Gao, Dehong and Fan, Deng-Ping and Liu, Li and Laaksonen, Jorma and Ouyang, Wanli and Sebe, Nicu},
  journal={CAAI Artificial Intelligence Research},
  year={2024}
}""",
            "license": "Check Hugging Face model page",
            "attribution_required": True
        }
    }
    
    if model_name not in model_citations:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    
    info = model_citations[model_name].copy()
    
    # Add loading status
    if model_manager:
        info["is_loaded"] = model_manager.is_model_loaded(model_name)
    
    return info

@app.post("/remove-background")
@apply_rate_limit("5/hour")
async def remove_background(
    request: Request,
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

# Serve static files in production (Docker) but not in development
# In development, Vite dev server runs separately on port 5173
from fastapi.staticfiles import StaticFiles
from pathlib import Path

web_dist = Path(__file__).parent.parent / "web" / "dist"

# Only mount static files if dist/ exists (production/Docker build)
if web_dist.exists() and web_dist.is_dir():
    try:
        # Mount static files at root, but API routes take precedence
        app.mount("/", StaticFiles(directory=str(web_dist), html=True), name="static")
        logger.info(f"✅ Serving static files from {web_dist}")
    except Exception as e:
        logger.warning(f"⚠️  Could not mount static files: {e}")
else:
    logger.info(f"ℹ️  Static files not found at {web_dist}")
    logger.info(f"ℹ️  For development: cd web && npm run dev")
    logger.info(f"ℹ️  For production: cd web && npm run build")

if __name__ == "__main__":
    import uvicorn
    
    # Read configuration from environment variables
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8080"))
    debug = os.getenv("API_DEBUG", "false").lower() == "true"
    
    uvicorn.run(app, host=host, port=port, log_level="info")
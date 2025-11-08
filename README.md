# 🎨 Background Remover AI

A modular, scalable FastAPI-based service for removing backgrounds from images using state-of-the-art AI models from Hugging Face.

## ✨ Features

- 🤖 **Multiple AI Models**: Support for RMBG-1.4 and RMBG-2.0 from Hugging Face
- 📦 **Modular Architecture**: Easy to add new models
- 🚀 **FastAPI**: Modern, async Python web framework
- 🔋 **Smart Memory Management**: Load/unload models on demand
- 🎭 **Mask Output**: Get both the background-removed image and the segmentation mask
- 📊 **Metadata**: Includes processing info (device used, sizes, model info)
- 🔌 **Base64 JSON Responses**: Easy integration with web frontends

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- **AI/ML**: [PyTorch](https://pytorch.org/), [Transformers](https://huggingface.co/transformers/), [torchvision](https://pytorch.org/vision/)
- **Models**: [RMBG](https://huggingface.co/briaai/RMBG-2.0) - Bilateral Reference for High-Resolution Dichotomous Image Segmentation
- **Image Processing**: [Pillow](https://python-pillow.org/)
- **Server**: [Uvicorn](https://www.uvicorn.org/)

## 📂 Project Structure

```
background-remover-ai/
├── api/
│   └── main.py              # FastAPI application with endpoints
├── models/
│   ├── base_model.py        # Abstract base class for models
│   ├── rmbg_model.py        # RMBG-specific implementation
│   ├── model_manager.py     # Model lifecycle management
│   └── __init__.py
├── tests/
│   └── test_api.py          # End-to-end API testing
├── assets/
│   └── lena.png             # Test image
├── learn/
│   └── demo.py              # Original demo script
├── requirements.txt
└── README.md
```

## 📦 Installation

### Prerequisites

- Python 3.9+
- pip or conda

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/background-remover-ai.git
   cd background-remover-ai
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Starting the API

```bash
python api/main.py
```

By default, the API runs on `http://localhost:8000`

You can customize via environment variables:
```bash
API_HOST=0.0.0.0 API_PORT=5000 python api/main.py
```

### API Endpoints

#### Health Check
```bash
GET /
```

#### List Models
```bash
GET /models
```

#### Remove Background
```bash
POST /remove-background
```

**Parameters:**
- `file` (required): Image file (multipart/form-data)
- `model_name` (optional): `"rmbg-2.0"` (default) or `"rmbg-1.4"`
- `include_mask` (optional): `true` to include segmentation mask
- `return_metadata` (optional): `true` to include metadata (default: true)

**Response:**
```json
{
  "success": true,
  "result_image": "base64_encoded_png_image",
  "mask": "base64_encoded_mask_image",
  "metadata": {
    "model_used": "rmbg-2.0",
    "original_size": [width, height],
    "processed_size": [width, height],
    "device_used": "cuda"
  }
}
```

#### Load Model
```bash
POST /load-model/{model_name}
```

#### Unload Model
```bash
DELETE /unload-model/{model_name}
```

### Testing

Run the end-to-end test (ensure API is running first):

```bash
# Terminal 1: Start the API
python api/main.py

# Terminal 2: Run tests
python tests/test_api.py
```

The test will:
1. Check API health
2. List available models
3. Process `assets/lena.png`
4. Save results to `assets/lena_no_bg.png` and `assets/lena_mask.png`

## 🏗️ Architecture

### Layer 1: Models (`models/`)

- **`base_model.py`**: Abstract base class defining the contract for all models
- **`rmbg_model.py`**: RMBG implementation (supports multiple versions)
- **`model_manager.py`**: Registry/factory pattern for model lifecycle management

### Layer 2: API (`api/`)

- **`main.py`**: FastAPI application with endpoints that orchestrate model operations

### Layer 3: Client (`tests/`)

- **`test_api.py`**: Example client showing how to call the API

## 🔄 Model Pipeline

For each image:
1. **Preprocess**: Resize to 1024x1024, normalize with ImageNet params, add batch dimension
2. **Inference**: Run through the model with `torch.no_grad()` (no gradient computation)
3. **Postprocess**: Apply sigmoid, resize mask back to original size, apply as alpha channel
4. **Encode**: Convert to base64 for JSON response

## � Adding New Models

To add a new background removal model:

1. Create a new class in `models/` inheriting from `BackgroundRemovalModel`
2. Implement the abstract methods:
   - `load_model()`
   - `preprocess_image()`
   - `postprocess_prediction()`
3. Register in `ModelManager.model_registry`

Example:
```python
class MyNewModel(BackgroundRemovalModel):
    async def load_model(self) -> None:
        # Your implementation
        pass
    
    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        # Your implementation
        pass
    
    def postprocess_prediction(self, prediction: torch.Tensor, original_image: Image.Image) -> Tuple[Image.Image, Image.Image]:
        # Your implementation
        pass
```

## � Docker

Build and run with Docker:

```bash
docker build -t background-remover-ai .
docker run -p 8000:8000 -e API_PORT=8000 background-remover-ai
```

## 📝 License

This project uses a **custom non-commercial license**.

- ✅ You can view and study this code
- ✅ Perfect for learning and educational purposes
- ❌ Commercial use is not permitted
- ❌ Redistribution is not allowed

See the [LICENSE](LICENSE) file for full details.

## � References

If you use this project in your research, please cite the original RMBG paper:

```bibtex
@article{BiRefNet,
  title={Bilateral Reference for High-Resolution Dichotomous Image Segmentation},
  author={Zheng, Peng and Gao, Dehong and Fan, Deng-Ping and Liu, Li and Laaksonen, Jorma and Ouyang, Wanli and Sebe, Nicu},
  journal={CAAI Artificial Intelligence Research},
  year={2024}
}
```

## 🤝 Contributing

For now, this is a personal learning project. Feedback and suggestions are welcome via issues.

## 📧 Contact

For questions or collaboration inquiries: [your-email@example.com](mailto:your-email@example.com)

## 📝 License

This project uses a **custom non-commercial license**.

- ✅ You can view and study this code
- ✅ Perfect for learning and educational purposes
- ❌ Commercial use is not permitted
- ❌ Redistribution is not allowed

See the [LICENSE](LICENSE) file for full details.

For commercial licensing or collaboration: tu-email@ejemplo.com
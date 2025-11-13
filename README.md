# 🎨 Background Remover AI

A production-ready, full-stack web application for removing backgrounds from images using state-of-the-art AI models (RMBG-1.4 and RMBG-2.0) from Hugging Face. Features a modern Vue.js frontend, FastAPI backend, and Docker deployment.

## ✨ What it does

- **Remove Backgrounds**: Upload an image and instantly get a background-free version with transparency
- **Compare Models**: Side-by-side comparison of RMBG-1.4 vs RMBG-2.0 results
- **Download Results**: Get both the processed image and segmentation mask
- **Rate Limited API**: 5 requests per hour per IP (prevents abuse)
- **Modern UI**: Responsive web interface with drag-and-drop support

## 🚀 Quick Start

### Option 1: Docker (Recommended for Production)

```bash
# Build and run the complete application
docker-compose up --build

# Open http://localhost:8080 in your browser
```

The Docker setup includes:
- ✅ FastAPI backend + Vue.js frontend in one container
- ✅ Pre-built and optimized for deployment
- ✅ HuggingFace models cached in a volume (no re-downloads on restart)
- ✅ Health checks included

### Option 2: Local Development

#### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
python api/main.py
# Server runs on http://localhost:8080
```

#### 2. Frontend Setup (in another terminal)

```bash
cd web

# Install Node dependencies (first time only)
npm install

# Start dev server with hot reload
npm run dev
# Frontend runs on http://localhost:5173
# API calls are automatically proxied to http://localhost:8080
```

Then open http://localhost:5173 in your browser.

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI, Python 3.11 |
| Frontend | Vue 3, TypeScript, Tailwind CSS |
| AI/ML | PyTorch, Transformers, RMBG models |
| Rate Limiting | SlowAPI |
| Deployment | Docker, docker-compose |

## 📁 Project Structure

```
├── api/                 # FastAPI backend
│   └── main.py         # REST API + static file serving
├── models/             # AI model implementations
│   ├── base_model.py   # Abstract base class
│   ├── rmbg_model.py   # RMBG-1.4 & RMBG-2.0
│   └── model_manager.py # Model lifecycle
├── web/                # Vue 3 frontend
│   ├── src/
│   │   ├── App.vue     # Main component
│   │   └── services/api.ts
│   ├── vite.config.ts  # Build config
│   └── package.json
├── tests/              # API tests
├── assets/             # Test images
├── Dockerfile          # Multi-stage build
├── docker-compose.yml  # Container orchestration
└── requirements.txt    # Python dependencies
```

## 🧪 Testing

### Local Testing

```bash
# Start the backend first
python api/main.py

# In another terminal, run tests
python tests/test_api.py
```

### Via Web UI

1. Open http://localhost:5173 (dev) or http://localhost:8080 (production)
2. Upload an image
3. Select a model (RMBG-1.4 or RMBG-2.0)
4. Download the result

## 📚 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/` | Web interface |
| `GET` | `/models` | List available models |
| `POST` | `/remove-background` | Process image (rate limited: 5/hour) |
| `GET` | `/models/{name}/info` | Model information |
| `POST` | `/load-model/{name}` | Preload model |
| `DELETE` | `/unload-model/{name}` | Unload model |

**Example**: Remove background from image
```bash
curl -X POST http://localhost:8080/remove-background \
  -F "file=@image.jpg" \
  -F "model_name=rmbg-2.0" \
  -F "include_mask=true"
```

## 🐳 Docker Deployment on Server

### Deploy on a Linux Server

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/background-remover-ai.git
   cd background-remover-ai
   ```

2. **Build and run**
   ```bash
   docker-compose up --build -d
   ```

3. **Access the application**
   - Open http://your-server-ip:8080

### With Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Environment Variables

Create a `.env` file to customize:

```bash
API_HOST=0.0.0.0
API_PORT=8080
API_DEBUG=false
```

## 🔧 Adding New Models

To add a new background removal model:

1. Create a model class in `models/your_model.py` extending `BackgroundRemovalModel`
2. Implement `load_model()`, `preprocess_image()`, and `postprocess_prediction()` methods
3. Register in `models/model_manager.py`
4. Test via the API or web UI

## 📊 Performance

| Model | Speed (CPU) | Speed (GPU) | Memory |
|-------|-------------|-------------|--------|
| RMBG-1.4 | ~3-4s | ~0.5s | ~2GB |
| RMBG-2.0 | ~3-5s | ~0.6s | ~2.5GB |

**Tip**: Use GPU for 6-8x faster processing

## 📚 References

This project uses models based on the **BiRefNet** (Bilateral Reference Network) architecture:

```bibtex
@article{BiRefNet,
  title={Bilateral Reference for High-Resolution Dichotomous Image Segmentation},
  author={Zheng, Peng and Gao, Dehong and Fan, Deng-Ping and Liu, Li and 
          Laaksonen, Jorma and Ouyang, Wanli and Sebe, Nicu},
  journal={CAAI Artificial Intelligence Research},
  year={2024}
}
```

**Models**: [RMBG-1.4](https://huggingface.co/briaai/RMBG-1.4) & [RMBG-2.0](https://huggingface.co/briaai/RMBG-2.0) by [BRIA AI](https://huggingface.co/briaai)

## 📝 License

This project is provided for learning and educational purposes. See the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for learning AI and full-stack development**

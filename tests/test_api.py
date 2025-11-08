"""
Example script to test the Background Remover API
"""
import requests
import base64
from PIL import Image
import io
import json
from pathlib import Path

# API configuration
API_BASE_URL = "http://localhost:8080"

# Get the assets directory (relative to this script)
ASSETS_DIR = Path(__file__).parent.parent / "assets"
TEST_IMAGE_PATH = ASSETS_DIR / "lena.png"

def test_api_health():
    """Test if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print("API Health Check:", response.json())
        return True
    except Exception as e:
        print(f"API not available: {e}")
        return False

def list_models():
    """List available models"""
    try:
        response = requests.get(f"{API_BASE_URL}/models")
        models_info = response.json()
        print("\nAvailable Models:")
        print(json.dumps(models_info, indent=2))
        return models_info
    except Exception as e:
        print(f"Error listing models: {e}")
        return None

def remove_background_from_file(image_path: str, model_name: str = "rmbg-2.0", include_mask: bool = True):
    """
    Remove background from image file
    
    Args:
        image_path: Path to input image
        model_name: Model to use for background removal
        include_mask: Whether to include mask in response
    """
    try:
        image_path = Path(image_path)
        
        if not image_path.exists():
            print(f"❌ Image not found: {image_path}")
            return False
        
        # Prepare the file
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, 'image/jpeg')}
            data = {
                'model_name': model_name,
                'include_mask': include_mask,
                'return_metadata': True
            }
            
            # Make request
            response = requests.post(
                f"{API_BASE_URL}/remove-background",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            
            # Save result image
            if 'result_image' in result:
                # Decode base64 image
                image_data = base64.b64decode(result['result_image'])
                result_image = Image.open(io.BytesIO(image_data))
                
                # Save to assets directory with proper naming
                output_dir = image_path.parent
                stem = image_path.stem
                output_path = output_dir / f"{stem}_no_bg.png"
                
                result_image.save(output_path)
                print(f"✅ Background removed! Saved to: {output_path}")
                
                # Save mask if included
                if include_mask and 'mask' in result:
                    mask_data = base64.b64decode(result['mask'])
                    mask_image = Image.open(io.BytesIO(mask_data))
                    mask_path = output_dir / f"{stem}_mask.png"
                    mask_image.save(mask_path)
                    print(f"✅ Mask saved to: {mask_path}")
                
                # Print metadata
                if 'metadata' in result:
                    print("\nMetadata:")
                    print(json.dumps(result['metadata'], indent=2))
                
                return True
            else:
                print("❌ No result image in response")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Testing Background Remover API")
    print("=" * 50)
    
    # Test API health
    if not test_api_health():
        print("❌ API is not running. Start it with: python api/main.py")
        return
    
    # List models
    list_models()
    
    # Test background removal
    print("\n" + "=" * 50)
    print("🖼️  Testing Background Removal")
    
    print(f"Processing: {TEST_IMAGE_PATH}")
    
    # Test with RMBG-2.0
    success = remove_background_from_file(
        image_path=str(TEST_IMAGE_PATH),
        model_name="rmbg-2.0",
        include_mask=True
    )
    
    if success:
        print("✅ Background removal completed successfully!")
    else:
        print("❌ Background removal failed!")

if __name__ == "__main__":
    main()

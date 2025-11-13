from PIL import Image
import torch
from torchvision import transforms
from transformers import AutoModelForImageSegmentation

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = AutoModelForImageSegmentation.from_pretrained('briaai/RMBG-2.0', trust_remote_code=True).eval().to(device)

# Data settings
image_size = (1024, 1024)
transform_image = transforms.Compose([
    transforms.Resize(image_size),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

image = Image.open('C:\\temp\\a6d323cb-26dd-4e67-90c1-55f93040ddef.png').convert("RGB")
transformed = transform_image(image)
if isinstance(transformed, torch.Tensor):
    input_images = transformed.unsqueeze(0).to(device)
else:
    raise RuntimeError("Transform did not return a tensor")

# Prediction
with torch.no_grad():
    preds = model(input_images)[-1].sigmoid().cpu()
pred = preds[0].squeeze()
pred_pil = transforms.ToPILImage()(pred)
mask = pred_pil.resize(image.size)
image.putalpha(mask)

image.save("C:\\temp\\no_bg_image.png")

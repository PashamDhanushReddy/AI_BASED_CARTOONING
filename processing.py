import cv2
import numpy as np

def classic_cartoon(image_bgr):
    bilateral = cv2.bilateralFilter(image_bgr, 15, 80, 80)
    gray = cv2.cvtColor(bilateral, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.medianBlur(gray, 7)
    edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 7, 7)
    data = np.float32(bilateral).reshape((-1, 3))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 3, 1.0)
    _, labels, centers = cv2.kmeans(data, 8, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()].reshape(bilateral.shape)
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    cartoon = cv2.bitwise_and(quantized, edges_bgr)
    return cartoon

def sketch_effect(image_bgr):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    gray_inv = 255 - gray
    gray_blur = cv2.GaussianBlur(gray_inv, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - gray_blur, scale=256)
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

def pencil_color_effect(image_bgr):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - gray_blur, scale=256)
    bilateral = cv2.bilateralFilter(image_bgr, 9, 300, 300)
    data = np.float32(bilateral).reshape((-1, 3))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 3, 1.0)
    _, labels, centers = cv2.kmeans(data, 12, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()].reshape(bilateral.shape)
    sketch_3d = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    pencil_color = cv2.multiply(sketch_3d, quantized, scale=1/256)
    return pencil_color

_ANIME_CACHE = {}

def _ensure_pytorch_available():
    try:
        import torch
        from PIL import Image
        return torch, Image
    except Exception as e:
        raise RuntimeError("PyTorch and Pillow required. Install with:\n"
                           "pip install pillow\n"
                           "pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu\n"
                           f"Original error: {e}")

def _load_anime_components(pretrained: str, size: int = 512):
    key = (pretrained, int(size))
    if key in _ANIME_CACHE:
        return _ANIME_CACHE[key]
    torch, Image = _ensure_pytorch_available()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        try:
            gen = torch.hub.load("bryandlee/animegan2-pytorch:main", "generator",
                                 pretrained=pretrained, device=device, progress=False)
        except TypeError:
            gen = torch.hub.load("bryandlee/animegan2-pytorch:main", "generator", pretrained=pretrained)
            gen.to(device)
        gen.eval()
    except Exception as e:
        raise RuntimeError(f"Failed to load generator {pretrained}: {e}")
    face2paint = None
    try:
        try:
            face2paint = torch.hub.load("bryandlee/animegan2-pytorch:main", "face2paint",
                                        size=size, device=device, progress=False)
        except TypeError:
            face2paint = torch.hub.load("bryandlee/animegan2-pytorch:main", "face2paint", size=size)
    except Exception:
        face2paint = None
    _ANIME_CACHE[key] = (gen, face2paint, device)
    return _ANIME_CACHE[key]

def _anime_to_bgr(image_bgr: np.ndarray, pretrained: str, size: int = 512) -> np.ndarray:
    torch, Image = _ensure_pytorch_available()
    gen, face2paint, device = _load_anime_components(pretrained, size=size)
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(rgb)
    if face2paint is not None:
        try:
            out = face2paint(gen, pil)
            if isinstance(out, (tuple, list)):
                out = out[0]
            out_rgb = np.array(out.convert("RGB"))
            return cv2.cvtColor(out_rgb.astype(np.uint8), cv2.COLOR_RGB2BGR)
        except Exception:
            pass
    import torchvision.transforms as T
    transform = T.Compose([T.Resize((size, size)), T.ToTensor()])
    tensor = transform(pil).unsqueeze(0).to(device)
    with torch.no_grad():
        out_t = gen(tensor)
    out_t = out_t.squeeze(0).cpu()
    minv, maxv = float(out_t.min()), float(out_t.max())
    if minv < -0.5 and maxv <= 1.5:
        out_t = (out_t + 1.0) / 2.0
    elif maxv > 1.1:
        out_t = (out_t - minv) / (maxv - minv + 1e-8)
    out_t = out_t.clamp(0.0, 1.0)
    out_np = (out_t.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
    return cv2.cvtColor(out_np, cv2.COLOR_RGB2BGR)

def anime_paprika(image_bgr):
    return _anime_to_bgr(image_bgr, pretrained="paprika", size=512)

def anime_facepaint_v1(image_bgr):
    return _anime_to_bgr(image_bgr, pretrained="face_paint_512_v1", size=512)

def anime_facepaint_v2(image_bgr):
    return _anime_to_bgr(image_bgr, pretrained="face_paint_512_v2", size=512)

STYLE_MAP = {
    "Classic Cartoon": classic_cartoon,
    "Sketch": sketch_effect,
    "Pencil Color": pencil_color_effect,
    "Anime - Paprika": anime_paprika,
    "Anime - FacePaint v1": anime_facepaint_v1,
    "Anime - FacePaint v2": anime_facepaint_v2,
}

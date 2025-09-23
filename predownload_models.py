import torch
import sys

MODELS = ["paprika", "face_paint_512_v1", "face_paint_512_v2"]
REPO = "bryandlee/animegan2-pytorch:main"
device = "cuda" if torch.cuda.is_available() else "cpu"

print("Predownloading AnimeGAN models to device:", device)
for name in MODELS:
    try:
        print(f"-> Loading generator pretrained='{name}' ...")
        try:
            gen = torch.hub.load(REPO, "generator", pretrained=name, device=device, progress=True)
        except TypeError:
            gen = torch.hub.load(REPO, "generator", pretrained=name, progress=True)
        gen.to(device)
        gen.eval()
        del gen
        print(f" generator '{name}' downloaded.")
    except Exception as e:
        print(f" FAILED to load generator '{name}': {e}", file=sys.stderr)

print("Done. Models cached in torch hub cache (TORCH_HOME/hub).")

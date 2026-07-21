from PIL import Image, ImageOps
import os

BASE = r"C:\Users\Infinity Tech\Desktop\Mis Cosas\Proyecto Luna\LunaDeck v1.7.55"
ASSETS_OUT = os.path.join(BASE, "msix-package", "assets")

isotipo_path = os.path.join(BASE, "assets", "brand", "Icono EXE.png")
logotipo_path = os.path.join(BASE, "assets", "brand", "c.png")

isotipo = Image.open(isotipo_path).convert("RGBA")
logotipo = Image.open(logotipo_path).convert("RGBA")

def make_square(img, size):
    """Scale isotipo to fit inside size x size square with padding, centered on transparent"""
    # Max dimension to fit with 85% fill
    target = int(size * 0.82)
    factor = min(target / img.width, target / img.height)
    new_w = int(img.width * factor)
    new_h = int(img.height * factor)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - new_w) // 2
    y = (size - new_h) // 2
    canvas.paste(resized, (x, y), resized)
    return canvas

def make_wide(img, size):
    """Scale to fit 310x150 wide tile"""
    target_w = size[0] - 20
    target_h = size[1] - 20
    factor = min(target_w / img.width, target_h / img.height)
    new_w = int(img.width * factor)
    new_h = int(img.height * factor)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    x = (size[0] - new_w) // 2
    y = (size[1] - new_h) // 2
    canvas.paste(resized, (x, y), resized)
    return canvas

def make_splash():
    """620x300 splash: dark background + isotipo centered"""
    canvas = Image.new("RGBA", (620, 300), (13, 13, 13, 255))
    target_size = 120
    factor = min(target_size / isotipo.width, target_size / isotipo.height)
    new_w = int(isotipo.width * factor)
    new_h = int(isotipo.height * factor)
    resized = isotipo.resize((new_w, new_h), Image.LANCZOS)
    x = (620 - new_w) // 2
    y = (300 - new_h) // 2
    canvas.paste(resized, (x, y), resized)
    return canvas

# Square logos (from isotipo)
assets = {
    "Square44x44Logo.png": (44, 44),
    "Square71x71Logo.png": (71, 71),
    "Square150x150Logo.png": (150, 150),
    "Square310x310Logo.png": (310, 310),
    "StoreLogo.png": (50, 50),
    "BadgeLogo.png": (24, 24),
    "PackageIcon.png": (256, 256),
}

for name, (w, h) in assets.items():
    img = make_square(isotipo, w)
    path = os.path.join(ASSETS_OUT, name)
    img.save(path, "PNG")
    print(f"  {name}  {img.size}")

# Wide logo (from logotipo)
wide = make_wide(logotipo, (310, 150))
wide.save(os.path.join(ASSETS_OUT, "Wide310x150Logo.png"), "PNG")
print(f"  Wide310x150Logo.png  {wide.size}")

# Splash
splash = make_splash()
splash.save(os.path.join(ASSETS_OUT, "SplashScreen.png"), "PNG")
print(f"  SplashScreen.png  {splash.size}")

print("\nAll 9 assets generated.")

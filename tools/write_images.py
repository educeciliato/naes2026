import base64
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
IMG_DIR = os.path.join(BASE_DIR, 'static', 'img')
os.makedirs(IMG_DIR, exist_ok=True)

# 1x1 transparent PNG
png_b64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=='
png_data = base64.b64decode(png_b64)

files = {
    os.path.join(IMG_DIR, 'caso_de_uso.png'): png_data,
    os.path.join(IMG_DIR, 'diagrama_classes.png'): png_data,
}

for path, data in files.items():
    with open(path, 'wb') as f:
        f.write(data)
    print('Wrote', path)

import base64
from PIL import Image, ImageDraw
from io import BytesIO

def _to_data_uri(image_bytes: bytes, mime: str = "image/jpeg") -> str:
    """Превращает байты изображения в data-URI для передачи в API"""
    b64 = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime};base64,{b64}"

def add_grid(image_bytes: BytesIO, rows: int = 15, cols: int = 20, line_thickness: int = 3) -> BytesIO:
    """
    Наносит сетку на изображение.
    :param image_bytes: BytesIO с исходным изображением
    :param rows: количество строк (горизонтальных ячеек)
    :param cols: количество столбцов (вертикальных ячеек)
    :param line_thickness: толщина линий в пикселях
    :return: BytesIO с изображением, на котором нарисована сетка
    """
    image_bytes.seek(0)
    img = Image.open(image_bytes).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size

    for i in range(1, rows):
        y = int(height * i / rows)
        draw.line([(0, y), (width, y)], fill=(255, 255, 255), width=line_thickness)

    for j in range(1, cols):
        x = int(width * j / cols)
        draw.line([(x, 0), (x, height)], fill=(255, 255, 255), width=line_thickness)

    for k in range(line_thickness):
        draw.rectangle(
            [k, k, width - 1 - k, height - 1 - k],
            outline=(255, 255, 255),
        )

    out = BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    return out

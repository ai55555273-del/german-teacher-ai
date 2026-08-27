from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests
import os
import textwrap
from datetime import datetime

OUT = Path("output")
OUT.mkdir(exist_ok=True)

LESSONS = [
    ("Deutsch leicht", "Heute lernen wir:", "Ich habe Hunger.", "أنا جائع."),
    ("Deutsch leicht", "Heute lernen wir:", "Wie geht es dir?", "كيف حالك؟"),
    ("Deutsch leicht", "Heute lernen wir:", "Ich lerne Deutsch.", "أنا أتعلم الألمانية."),
    ("Deutsch leicht", "Heute lernen wir:", "Was machst du?", "ماذا تفعل؟"),
]

def font(size):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def make_card():
    title, label, german, arabic = LESSONS[datetime.now().day % len(LESSONS)]
    img = Image.new("RGB", (1080, 1080), "white")
    d = ImageDraw.Draw(img)

    d.rectangle((0, 0, 1080, 220), fill=(30, 55, 90))
    d.text((60, 60), title, font=font(72), fill="white")
    d.text((60, 270), label, font=font(48), fill=(30, 55, 90))
    d.text((60, 400), german, font=font(78), fill="black")
    d.text((60, 560), arabic, font=font(58), fill="black")
    d.text((60, 900), "احفظ الجملة واكتب مثالًا في التعليقات 👇",
           font=font(40), fill=(30, 55, 90))

    path = OUT / "lesson.png"
    img.save(path)
    return path, german, arabic

def make_caption(german, arabic):
    return (
        f"🇩🇪 جملة ألمانية في دقيقة!\n\n"
        f"{german}\n"
        f"{arabic}\n\n"
        "لو عايز تتعلم ألماني بطريقة بسيطة، تابع الصفحة ❤️\n"
        "#تعلم_الألمانية #اللغة_الألمانية #Deutsch #German"
    )

def publish_to_facebook(image_path, caption):
    page_id = os.getenv("META_PAGE_ID")
    token = os.getenv("META_PAGE_ACCESS_TOKEN")
    version = os.getenv("META_API_VERSION", "v23.0")

    if not page_id or not token:
        print("Meta secrets are not configured. Skipping Facebook publishing.")
        return

    url = f"https://graph.facebook.com/{version}/{page_id}/photos"
    with open(image_path, "rb") as f:
        r = requests.post(
            url,
            data={"caption": caption, "access_token": token},
            files={"source": f},
            timeout=60,
        )
    print("Facebook:", r.status_code, r.text)
    r.raise_for_status()

if __name__ == "__main__":
    image, german, arabic = make_card()
    caption = make_caption(german, arabic)
    print("Created:", image)
    publish_to_facebook(image, caption)

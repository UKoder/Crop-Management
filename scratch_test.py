import base64
from google.genai import types

def test():
    # dummy base64 1x1 pixel image
    b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
    image_bytes = base64.b64decode(b64)
    part = types.Part(
        inline_data=types.Blob(
            mime_type="image/png",
            data=image_bytes
        )
    )
    content = types.UserContent(parts=[part])
    print(content)

test()

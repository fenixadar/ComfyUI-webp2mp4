from .nodes import WebpToMp4Converter

NODE_CLASS_MAPPINGS = {
    "WebpToMp4Converter": WebpToMp4Converter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WebpToMp4Converter": "WEBP转MP4转换器"
}

try:
    import PIL
    import moviepy
except ImportError as e:
    print(f"WEBP转MP4节点缺少依赖: {e}")
    print("请安装: pip install Pillow moviepy")
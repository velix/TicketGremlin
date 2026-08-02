from PIL import Image
import os

MAX_PRINT_WIDTH_PX = 576
MAX_PRINT_HEIGHT_PX = 400


def resize_image_for_printer(filepath, max_width=MAX_PRINT_WIDTH_PX):
    base, ext = os.path.splitext(filepath)
    output_path = f"{base}_resized{ext}"
    
    with Image.open(filepath) as img:
        ratio = max_width / float(img.size[0])
        new_height = int(float(img.size[1]) * float(ratio))
        
        if new_height > MAX_PRINT_HEIGHT_PX:
            ratio = MAX_PRINT_HEIGHT_PX / float(img.size[1])
            new_width = int(float(img.size[0]) * float(ratio))
            new_height = MAX_PRINT_HEIGHT_PX
        else:
            new_width = max_width
        
        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        resized.save(output_path)
    
    return output_path

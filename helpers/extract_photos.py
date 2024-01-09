import os
import base64
from xml.etree import ElementTree as ET
from PIL import Image
import io

def extract_and_save_images(svg_path, output_folder):
    # Create folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Parse SVG file
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Register namespaces to preserve the structure
    namespaces = {
        '': 'http://www.w3.org/2000/svg',  # Default namespace
        'xlink': 'http://www.w3.org/1999/xlink',
        'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
        'inkscape': 'http://www.inkscape.org/namespaces/inkscape',
        'serif': 'http://www.serif.com/'
    }
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)

    # Find and replace embedded images
    for elem in root.findall('.//{http://www.w3.org/2000/svg}image', namespaces):
        href = elem.attrib.get('{http://www.w3.org/1999/xlink}href')
        if href and 'base64,' in href:
            print("\nAn image!")

            # Extract base64-encoded image data
            img_data = href.split('base64,')[1]

            # Decode base64
            img_bytes = base64.b64decode(img_data)

            # Resize the image to a web-safe size maintaining aspect ratio
            img = Image.open(io.BytesIO(img_bytes))
            web_safe_size = calculate_web_safe_size(img.size, max_dimension=600)
            img.thumbnail(web_safe_size)

            # Save image to the folder in WebP format
            img_filename = f"image_{len(os.listdir(output_folder)) + 1}.webp"
            img.save(os.path.join(output_folder, img_filename), 'WEBP')

            # Update the SVG to use external link with correct namespace
            elem.attrib['{http://www.w3.org/1999/xlink}href'] = img_filename

    # Save the modified SVG file
    modified_svg_path = os.path.join(output_folder, "modified_svg.svg")
    tree.write(modified_svg_path)

    return modified_svg_path

def calculate_web_safe_size(original_size, max_dimension):
    width, height = original_size
    aspect_ratio = width / height

    if width > height:
        new_width = max_dimension
        new_height = int(max_dimension / aspect_ratio)
    else:
        new_height = max_dimension
        new_width = int(max_dimension * aspect_ratio)

    return new_width, new_height

# Example usage
svg_path = "to_use.svg"
output_folder = "output"
resulting_svg = extract_and_save_images(svg_path, output_folder)
print(f"Modified SVG saved to: {resulting_svg}")

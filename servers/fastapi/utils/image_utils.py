from typing import List

from PIL import Image, ImageDraw

from models.pptx_models import PptxObjectFitEnum, PptxObjectFitModel


def clip_image(
    image: Image.Image,
    width: int,
    height: int,
    focus_x: float = 50.0,
    focus_y: float = 50.0,
) -> Image.Image:
    img_width, img_height = image.size

    img_aspect = img_width / img_height
    box_aspect = width / height

    if img_aspect > box_aspect:
        new_height = height
        new_width = int(new_height * img_aspect)
    else:
        new_width = width
        new_height = int(new_width / img_aspect)

    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    # Calculate clipping position based on focus
    # Convert focus percentages (0-100) to position in the resized image
    focus_x = max(0.0, min(100.0, focus_x))  # Clamp to 0-100 range
    focus_y = max(0.0, min(100.0, focus_y))  # Clamp to 0-100 range

    # Calculate the center point based on focus
    center_x = int((new_width - width) * (focus_x / 100.0))
    center_y = int((new_height - height) * (focus_y / 100.0))

    # Calculate clipping box
    left = center_x
    top = center_y
    right = left + width
    bottom = top + height

    clipped_image = resized_image.crop((left, top, right, bottom))

    return clipped_image


def round_image_corners(image: Image.Image, radii: List[int]) -> Image.Image:
    if len(radii) != 4:
        raise ValueError(
            "Image Border Radius - radii must contain exactly 4 values for each corner"
        )

    w, h = image.size

    # Clamp border radius to not exceed half the width or height
    max_radius = min(w // 2, h // 2)
    clamped_radii = [min(radius, max_radius) for radius in radii]

    # Ensure the image has an alpha channel (RGBA)
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Use higher resolution for smoother anti-aliasing
    scale_factor = 4  # 4x supersampling for better quality
    high_res_w, high_res_h = w * scale_factor, h * scale_factor
    
    # Scale up the image for processing
    high_res_image = image.resize((high_res_w, high_res_h), Image.LANCZOS)
    
    # Scale up radii accordingly
    high_res_radii = [radius * scale_factor for radius in clamped_radii]

    # Create high-resolution mask
    mask = Image.new("L", (high_res_w, high_res_h), 0)
    draw = ImageDraw.Draw(mask)

    # Draw the rounded rectangle mask
    # Start with the main rectangle (excluding corners)
    max_high_radius = max(high_res_radii)
    draw.rectangle((max_high_radius, 0, high_res_w - max_high_radius, high_res_h), fill=255)
    draw.rectangle((0, max_high_radius, high_res_w, high_res_h - max_high_radius), fill=255)

    # Draw each rounded corner with anti-aliasing
    for i, radius in enumerate(high_res_radii):
        if radius > 0:
            # Calculate corner position
            if i == 0:  # top-left
                x, y = 0, 0
            elif i == 1:  # top-right
                x, y = high_res_w - radius * 2, 0
            elif i == 2:  # bottom-right
                x, y = high_res_w - radius * 2, high_res_h - radius * 2
            else:  # bottom-left
                x, y = 0, high_res_h - radius * 2

            # Draw quarter circle for this corner
            draw.pieslice(
                (x, y, x + radius * 2, y + radius * 2),
                start=i * 90,
                end=(i + 1) * 90,
                fill=255
            )

    # Apply the mask to the high-resolution image
    high_res_image.putalpha(mask)

    # Scale back down with high-quality resampling for smooth edges
    result = high_res_image.resize((w, h), Image.LANCZOS)

    return result


def invert_image(img: Image.Image) -> Image.Image:
    # Get image data
    data = img.getdata()

    # Process each pixel
    new_data = []
    for item in data:
        # Get current pixel values
        r, g, b, a = item

        # Invert RGB values while preserving transparency
        if a != 0:  # Skip fully transparent pixels
            new_data.append((255 - r, 255 - g, 255 - b, a))
        else:
            new_data.append((0, 0, 0, 0))

    # Create new image with modified data
    new_img = Image.new("RGBA", img.size)
    new_img.putdata(new_data)
    return new_img


def create_circle_image(
    image: Image.Image,
) -> Image.Image:
    # Convert to RGBA if not already
    img = image.convert("RGBA")
    # Get the original image size
    w, h = img.size
    
    # Use higher resolution for smoother anti-aliasing
    scale_factor = 4  # 4x supersampling for better quality
    high_res_w, high_res_h = w * scale_factor, h * scale_factor
    
    # Scale up the image for processing
    high_res_img = img.resize((high_res_w, high_res_h), Image.LANCZOS)
    
    # Use the smaller dimension for the circle
    circle_size = min(high_res_w, high_res_h)
    radius = circle_size // 2
    
    # Create high-resolution mask
    mask = Image.new("L", (high_res_w, high_res_h), 0)
    draw = ImageDraw.Draw(mask)

    # Calculate center position
    center_x = high_res_w // 2
    center_y = high_res_h // 2

    # Create a circular mask with anti-aliasing
    draw.ellipse(
        (
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
        ),
        fill=255,
    )

    # Apply the mask to the high-resolution image
    high_res_img.putalpha(mask)

    # Scale back down with high-quality resampling for smooth edges
    result = high_res_img.resize((w, h), Image.LANCZOS)
    
    return result


def set_image_opacity(image: Image.Image, opacity: float) -> Image.Image:
    # Clamp opacity to valid range
    opacity = max(0.0, min(1.0, opacity))

    # Convert to RGBA if not already
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Get the original alpha channel
    original_alpha = image.getchannel("A")

    # Create new alpha channel with adjusted opacity
    new_alpha = original_alpha.point(lambda x: int(x * opacity))

    # Create new image with modified alpha channel
    result = Image.new("RGBA", image.size)
    result.paste(image.convert("RGB"), (0, 0))
    result.putalpha(new_alpha)

    return result


def fit_image(
    image: Image.Image, width: int, height: int, object_fit: PptxObjectFitModel
) -> Image.Image:
    if not object_fit.fit:
        return image

    img_width, img_height = image.size
    img_aspect = img_width / img_height
    box_aspect = width / height

    if object_fit.fit == PptxObjectFitEnum.CONTAIN:
        # Scale image to fit within the box while maintaining aspect ratio
        if img_aspect > box_aspect:
            new_width = width
            new_height = int(width / img_aspect)
        else:
            new_height = height
            new_width = int(height * img_aspect)
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        # Use focus point for positioning if available
        focus_x = 50.0
        focus_y = 50.0
        if object_fit.focus and len(object_fit.focus) == 2:
            focus_x, focus_y = object_fit.focus[0], object_fit.focus[1]

        # Calculate paste position based on focus
        paste_x = int((width - new_width) * (focus_x / 100.0))
        paste_y = int((height - new_height) * (focus_y / 100.0))

        result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        result.paste(resized_image, (paste_x, paste_y))
        return result

    elif object_fit.fit == PptxObjectFitEnum.COVER:
        # Scale image to cover the box while maintaining aspect ratio
        if img_aspect > box_aspect:
            new_height = height
            new_width = int(height * img_aspect)
        else:
            new_width = width
            new_height = int(width / img_aspect)
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        # Use focus point for positioning if available
        focus_x = 50.0
        focus_y = 50.0
        if object_fit.focus and len(object_fit.focus) == 2:
            focus_x, focus_y = object_fit.focus[0], object_fit.focus[1]

        # Calculate paste position based on focus
        paste_x = int((new_width - width) * (focus_x / 100.0))
        paste_y = int((new_height - height) * (focus_y / 100.0))

        # Clip the image to the box size
        return resized_image.crop((paste_x, paste_y, paste_x + width, paste_y + height))

    elif object_fit.fit == PptxObjectFitEnum.FILL:
        # Stretch image to fill the box exactly
        return image.resize((width, height), Image.LANCZOS)

    return image

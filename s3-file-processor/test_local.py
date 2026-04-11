from image_processor import is_house_image, get_media_type

test_image_filename = "anthropictestimage.jpg"

print(f"Testing image: {test_image_filename}")
print("-" * 40)

with open(test_image_filename, "rb") as f:
    image_bytes = f.read()

media_type = get_media_type(test_image_filename)
is_house, details = is_house_image(image_bytes, media_type)

print(f"Is a house: {is_house}")
print(f"Confidence: {details.get('confidence')}")
print(f"Reason: {details.get('reason')}")
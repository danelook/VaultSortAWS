import anthropic
import base64


def encode_image(image_bytes):
    return base64.standard_b64encode(image_bytes).decode('utf-8')


def is_house_image(image_bytes, media_type='image/jpeg'):
    client = anthropic.Anthropic()
    
    image_data = encode_image(image_bytes)
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": """Look at this image and determine if it shows a house or residential building.
                        
Answer with ONLY a JSON object in this exact format, nothing else:
{
    "is_house": true or false,
    "confidence": "high", "medium", or "low",
    "reason": "one sentence explanation"
}"""
                    }
                ],
            }
        ],
    )
    
    import json
    response_text = message.content[0].text.strip()
    
    try:
        clean_text = response_text.replace('```json', '').replace('```', '').strip()
        result = json.loads(clean_text)
        return result.get('is_house', False), result
    except json.JSONDecodeError:
        if 'true' in response_text.lower():
            return True, {"is_house": True, "confidence": "low", "reason": response_text}
        return False, {"is_house": False, "confidence": "low", "reason": response_text}


def get_media_type(filename):
    filename_lower = filename.lower()
    if filename_lower.endswith('.png'):
        return 'image/png'
    elif filename_lower.endswith('.gif'):
        return 'image/gif'
    elif filename_lower.endswith('.webp'):
        return 'image/webp'
    else:
        return 'image/jpeg'
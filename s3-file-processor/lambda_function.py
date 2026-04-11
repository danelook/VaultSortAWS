import json
import boto3
import os
from image_processor import is_house_image, get_media_type
from address_processor import process_addresses
from encryption_handler import encrypt_data, get_or_create_key

s3_client = boto3.client('s3')

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
TEXT_EXTENSIONS = {'.txt', '.csv'}

ENCRYPTION_KEY = get_or_create_key()


def lambda_handler(event, context):
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']

        print(f"Processing file: {object_key} from bucket: {bucket_name}")

        if object_key.startswith('Houses/') or object_key.startswith('Addresses/'):
            print(f"Skipping already processed file: {object_key}")
            return response(200, "Skipped already processed file")

        file_extension = os.path.splitext(object_key)[1].lower()

        if file_extension in IMAGE_EXTENSIONS:
            return handle_image(bucket_name, object_key)
        elif file_extension in TEXT_EXTENSIONS:
            return handle_text(bucket_name, object_key)
        else:
            print(f"Unsupported file type: {file_extension}")
            return response(200, f"Unsupported file type: {file_extension}")

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise e


def handle_image(bucket_name, object_key):
    print(f"Handling image: {object_key}")

    s3_object = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    image_bytes = s3_object['Body'].read()

    media_type = get_media_type(object_key)
    is_house, details = is_house_image(image_bytes, media_type)

    print(f"House detection result: {is_house}, details: {details}")

    if is_house:
        filename = os.path.basename(object_key)
        destination_key = f"Houses/{filename}.enc"

        encrypted_image = encrypt_data(image_bytes, ENCRYPTION_KEY)

        s3_client.put_object(
            Bucket=bucket_name,
            Key=destination_key,
            Body=encrypted_image,
            ContentType='application/octet-stream'
        )

        print(f"Encrypted house image saved to: {destination_key}")
        return response(200, f"House image encrypted and saved to {destination_key}")
    else:
        print(f"Image is not a house, no action taken")
        return response(200, "Image is not a house, no action taken")


def handle_text(bucket_name, object_key):
    print(f"Handling text file: {object_key}")

    s3_object = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    content = s3_object['Body'].read().decode('utf-8')

    us_content, non_us_content = process_addresses(content)

    base_filename = os.path.splitext(os.path.basename(object_key))[0]

    if us_content:
        us_key = f"Addresses/US/{base_filename}_us.txt.enc"
        encrypted_us = encrypt_data(us_content.encode('utf-8'), ENCRYPTION_KEY)
        s3_client.put_object(
            Bucket=bucket_name,
            Key=us_key,
            Body=encrypted_us,
            ContentType='application/octet-stream'
        )
        print(f"Encrypted US addresses saved to: {us_key}")

    if non_us_content:
        non_us_key = f"Addresses/NonUS/{base_filename}_non_us.txt.enc"
        encrypted_non_us = encrypt_data(non_us_content.encode('utf-8'), ENCRYPTION_KEY)
        s3_client.put_object(
            Bucket=bucket_name,
            Key=non_us_key,
            Body=encrypted_non_us,
            ContentType='application/octet-stream'
        )
        print(f"Encrypted non-US addresses saved to: {non_us_key}")

    return response(200, "Address file encrypted and processed successfully")


def response(status_code, message):
    return {
        'statusCode': status_code,
        'body': json.dumps({'message': message})
    }
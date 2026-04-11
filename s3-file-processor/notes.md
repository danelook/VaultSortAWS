# S3 File Processor — Solution Notes

## Overview
This solution automatically processes files uploaded to an AWS S3 bucket using 
an AWS Lambda function. When a file is uploaded, Lambda is triggered and routes 
the file to the appropriate processor based on its type.

---

## Architecture
---

## File Structure
- `lambda_function.py` — main entry point, handles S3 events and routes files
- `image_processor.py` — uses Claude AI API to detect if an image is a house
- `address_processor.py` — parses and splits addresses by US vs non-US
- `requirements.txt` — Python dependencies (boto3, anthropic)

---

## Approach & Decisions

### Image Detection
I chose to use the Claude AI API (claude-sonnet-4-6) for house detection rather 
than a traditional machine learning model for several reasons:
- No model training required
- Handles edge cases well (apartments, townhouses, partial views)
- Returns structured JSON with a confidence level and reason, making 
  results transparent and debuggable
- Easy to swap out or adjust the prompt if requirements change

The API is prompted to return a strict JSON response so the result is 
predictable and easy to parse in code.

### Address Classification
Addresses are classified as US or non-US using three signals:
1. Explicit country indicators (USA, United States, U.S.A.)
2. US state abbreviations (e.g. ", TX" or ", NY")
3. US ZIP code pattern (5 digits, optionally followed by a 4-digit extension)

If any of these signals are found the address is classified as US. 
Otherwise it is classified as non-US.

### Loop Prevention
The Lambda function checks if an uploaded file is already inside a processed 
folder (Houses/ or Addresses/). If it is, the function exits immediately. 
This prevents an infinite loop where moving a file to Houses/ would trigger 
Lambda again.

---

## Assumptions
- Images are uploaded directly to the root of the bucket, not inside subfolders
- Text files contain one address per line with no blank lines between entries
- The Claude API key is stored as a Lambda environment variable named 
  ANTHROPIC_API_KEY (not hardcoded in the code)
- The S3 bucket already exists and is configured before deployment
- Images that are not houses are left in place and not deleted or moved
- Mixed files (e.g. a text file containing both addresses and other content) 
  are not expected

---

## Monitoring
In a production environment the following monitoring would be set up:

- **AWS CloudWatch Logs** — Lambda automatically sends all print() statements 
  to CloudWatch, providing a full log of every file processed and the outcome
- **CloudWatch Alarms** — alerts would be set up to notify the team if the 
  Lambda error rate exceeds a threshold or if the function times out
- **AWS CloudWatch Metrics** — track invocation count, error count, and 
  duration over time to spot unusual patterns
- **Dead Letter Queue (DLQ)** — a failed Lambda invocation would send the 
  event to an SQS queue for later inspection and reprocessing rather than 
  silently dropping it

---

## Security

- **API Keys** — the Anthropic API key is never hardcoded in the code. It 
  would be stored in AWS Secrets Manager or as an encrypted Lambda environment 
  variable
- **IAM Roles** — the Lambda function would be assigned an IAM role with the 
  minimum permissions needed: only read/write access to the specific S3 bucket, 
  nothing else
- **Bucket Policy** — the S3 bucket would be set to private with no public 
  access. Only the Lambda IAM role can read and write to it
- **Input Validation** — the Lambda function checks file extensions before 
  processing to avoid acting on unexpected file types
- **Encryption** — S3 server-side encryption (SSE-S3 or SSE-KMS) would be 
  enabled on the bucket so files are encrypted at rest

---

## Other Production Concerns

- **Error Handling** — the Lambda function wraps all logic in a try/except 
  block. Errors are logged to CloudWatch and re-raised so AWS can mark the 
  invocation as failed and retry it
- **Retries** —

---

## Encryption Implementation

Files are encrypted before being stored in S3 using the `cryptography` 
library with Fernet symmetric encryption. Fernet guarantees that data 
encrypted cannot be read or modified without the key.

### How it works
- A secret key is generated once and stored securely (in AWS Secrets 
  Manager in production)
- When a house image is detected, it is encrypted before being saved 
  to the Houses/ folder
- When addresses are processed, both the US and non-US output files 
  are encrypted before being saved to S3
- Encrypted files are saved with a `.enc` extension so they are clearly 
  identifiable as encrypted
- Only a system or user with access to the secret key can decrypt and 
  read the files

### Why Fernet
- Industry standard symmetric encryption
- Built into the Python `cryptography` library
- Simple key management — one key encrypts and decrypts
- The same library was battle tested in a prior phishing detection 
  project with 130,000+ emails

### Local Demo
Running `test_encryption.py` demonstrates the full encrypt/decrypt 
cycle locally without requiring AWS credentials or an S3 bucket.
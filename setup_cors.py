import boto3
import json


s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    region_name='us-east-1'
)

bucket_name = 'learnflow-local'


cors_configuration = {
    'CORSRules': [
        {
            'AllowedOrigins': ['http://localhost:3000'],
            'AllowedMethods': ['GET', 'PUT', 'POST', 'HEAD'],
            'AllowedHeaders': ['*'],
            'ExposeHeaders': ['ETag'],
            'MaxAgeSeconds': 3000
        }
    ]
}

try:
    s3_client.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_configuration)
    print(f"✅ CORS configured for {bucket_name}")
except Exception as e:
    print(f"❌ CORS error: {e}")


try:
    result = s3_client.get_bucket_cors(Bucket=bucket_name)
    print("\n📋 Current CORS:")
    print(json.dumps(result, indent=2, default=str))
except Exception as e:
    print(f"❌ No CORS configured: {e}")


policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": ["*"]},
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
        }
    ]
}

try:
    s3_client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
    print(f"\n✅ Public read policy set for {bucket_name}")
except Exception as e:
    print(f"❌ Policy error: {e}")
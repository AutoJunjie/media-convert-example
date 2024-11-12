import boto3
import json
from botocore.exceptions import ClientError

def create_video_bucket(bucket_name='video-test', region='us-west-2'):
    """
    创建用于 MediaConvert 的 S3 存储桶并设置相应的策略
    
    参数:
    bucket_name (str): 要创建的存储桶名称
    region (str): AWS 区域
    
    返回:
    str: 创建的存储桶名称
    """
    s3_client = boto3.client('s3', region_name=region)
    
    # 定义存储桶策略
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "MediaConvertInput",
                "Effect": "Allow",
                "Principal": {
                    "Service": "mediaconvert.amazonaws.com"
                },
                "Action": [
                    "s3:GetObject",
                    "s3:GetObjectACL"
                ],
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            },
            {
                "Sid": "MediaConvertOutput",
                "Effect": "Allow",
                "Principal": {
                    "Service": "mediaconvert.amazonaws.com"
                },
                "Action": [
                    "s3:PutObject",
                    "s3:PutObjectACL",
                    "s3:PutObjectTagging"
                ],
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }
    
    try:
        # 创建存储桶
        if region == 'us-east-1':
            s3_client.create_bucket(
                Bucket=bucket_name
            )
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': region
                }
            )
        
        print(f"成功创建存储桶: {bucket_name}")
        
        # 设置存储桶策略
        policy_string = json.dumps(bucket_policy)
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=policy_string
        )
        
        print(f"已应用存储桶策略")
        return bucket_name
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyOwnedByYou':
            print(f"存储桶 {bucket_name} 已存在且属于您")
            # 更新现有存储桶的策略
            policy_string = json.dumps(bucket_policy)
            s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=policy_string
            )
            print("已更新存储桶策略")
            return bucket_name
        elif error_code == 'BucketAlreadyExists':
            print(f"存储桶名称 {bucket_name} 已被其他用户使用")
            raise
        else:
            print(f"创建存储桶时发生错误: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        bucket_name = create_video_bucket()
        print(f"存储桶设置完成: {bucket_name}")
    except Exception as e:
        print(f"发生错误: {str(e)}") 
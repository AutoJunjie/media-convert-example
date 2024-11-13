import boto3
import json
import time
from datetime import datetime
from botocore.config import Config
from botocore.exceptions import ClientError
from create_mediaconvert_role import create_mediaconvert_role
from create_video_bucket import create_video_bucket

def create_frame_extraction_job(input_bucket, input_key, output_bucket, region='us-west-2', frame_capture_interval=88):
    """
    Create a MediaConvert job to extract frames from a video
    
    Parameters:
    input_bucket (str): Source S3 bucket name
    input_key (str): Source video key in S3
    output_bucket (str): Destination bucket for extracted frames
    region (str): AWS region for MediaConvert
    frame_capture_interval (int): Interval between frame captures in seconds
    """
    
    config = Config(
        region_name=region,
        signature_version='v4',
        retries={
            'max_attempts': 3,
            'mode': 'standard'
        }
    )
    
    try:
        mediaconvert_client = boto3.client('mediaconvert', config=config)
        endpoints = mediaconvert_client.describe_endpoints()
        
        mediaconvert = boto3.client('mediaconvert', 
                                   endpoint_url=endpoints['Endpoints'][0]['Url'],
                                   region_name=region,
                                   config=config)
        
        job_settings = {
            "TimecodeConfig": {
                "Source": "ZEROBASED"
            },
            "Inputs": [{
                "TimecodeSource": "ZEROBASED",
                "VideoSelector": {},
                "AudioSelectors": {
                    "Audio Selector 1": {
                        "DefaultSelection": "DEFAULT"
                    }
                },
                "FileInput": f"s3://{input_bucket}/{input_key}"
            }],
            "FollowSource": 1,
            "OutputGroups": [
                # Frame Capture Output Group
                {
                    "Name": "Frame Capture",
                    "OutputGroupSettings": {
                        "Type": "FILE_GROUP_SETTINGS",
                        "FileGroupSettings": {
                            "Destination": f"s3://{output_bucket}/frames/"
                        }
                    },
                    "Outputs": [{
                        "ContainerSettings": {
                            "Container": "RAW"
                        },
                        "VideoDescription": {
                            "CodecSettings": {
                                "Codec": "FRAME_CAPTURE",
                                "FrameCaptureSettings": {
                                    "FramerateNumerator": 30,
                                    "FramerateDenominator": frame_capture_interval,
                                    "MaxCaptures": 1,
                                    "Quality": 80
                                }
                            },
                            "Width": 1920,
                            "Height": 1080
                        }
                    }]
                },
                # Video Output Group
                {
                    "Name": "Video Output",
                    "OutputGroupSettings": {
                        "Type": "FILE_GROUP_SETTINGS",
                        "FileGroupSettings": {
                            "Destination": f"s3://{output_bucket}/video/"
                        }
                    },
                    "Outputs": [{
                        "ContainerSettings": {
                            "Container": "MP4",
                            "Mp4Settings": {
                                "CslgAtom": "INCLUDE",
                                "FreeSpaceBox": "EXCLUDE",
                                "MoovPlacement": "PROGRESSIVE_DOWNLOAD"
                            }
                        },
                        "VideoDescription": {
                            "CodecSettings": {
                                "Codec": "H_264",
                                "H264Settings": {
                                    "MaxBitrate": 5000000,
                                    "RateControlMode": "QVBR",
                                    "SceneChangeDetect": "TRANSITION_DETECTION",
                                    "QualityTuningLevel": "SINGLE_PASS",
                                    "QvbrSettings": {
                                        "QvbrQualityLevel": 7
                                    },
                                    "FramerateControl": "SPECIFIED",
                                    "FramerateNumerator": 30,
                                    "FramerateDenominator": 1
                                }
                            },
                            "Width": 640,
                            "Height": 480
                        }
                    }]
                }
            ]
        }
        
        job = mediaconvert.create_job(
            Role=create_mediaconvert_role(),
            Settings=job_settings,
            Queue="arn:aws:mediaconvert:us-west-2:955643200499:queues/Default",
            UserMetadata={},
            BillingTagsSource="JOB",
            AccelerationSettings={
                "Mode": "DISABLED"
            },
            StatusUpdateInterval="SECONDS_60",
            Priority=0
        )
        return job['Job']['Id']
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"AWS Error: {error_code} - {error_message}")
        if error_code == 'BadRequestException':
            print("Check your job settings and IAM role ARN")
        elif error_code == 'ForbiddenException':
            print("Check your IAM permissions")
        elif error_code == 'NotFoundException':
            print("Check if the input file exists and IAM role is correct")
        raise
    except Exception as e:
        print(f"Failed to create MediaConvert job: {str(e)}")
        raise

def check_job_status(job_id, region='us-west-2'):
    """
    Check the status of a MediaConvert job
    
    Parameters:
    job_id (str): The ID of the MediaConvert job
    region (str): AWS region for MediaConvert
    """
    config = Config(
        region_name=region,
        signature_version='v4'
    )
    
    try:
        mediaconvert_client = boto3.client('mediaconvert', config=config)
        endpoints = mediaconvert_client.describe_endpoints()
        
        mediaconvert = boto3.client('mediaconvert', 
                                   endpoint_url=endpoints['Endpoints'][0]['Url'],
                                   region_name=region,
                                   config=config)
        
        response = mediaconvert.get_job(Id=job_id)
        return response['Job']['Status']
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"AWS Error: {error_code} - {error_message}")
        raise

def main():
    # Configuration
    bucket_name = create_video_bucket()  # 创建并获取存储桶名称
    input_bucket = bucket_name
    input_key = 'VideoClipping0911.mp4'
    output_bucket = bucket_name  # 使用同一个存储桶作为输出
    region = 'us-west-2'
    frame_interval = 88
    
    try:
        job_id = create_frame_extraction_job(
            input_bucket,
            input_key,
            output_bucket,
            region,
            frame_interval
        )
        print(f"Job created with ID: {job_id}")
        
        while True:
            status = check_job_status(job_id, region)
            print(f"Job Status: {status}")
            
            if status in ['COMPLETE', 'ERROR', 'CANCELED']:
                break
                
            time.sleep(30)
            
        if status == 'COMPLETE':
            print("Frame extraction completed successfully!")
            print(f"Frames are available in s3://{output_bucket}/frames/")
            print(f"Video output is available in s3://{output_bucket}/video/")
        else:
            print(f"Job ended with status: {status}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
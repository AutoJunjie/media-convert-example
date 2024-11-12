# AWS MediaConvert Video Frame Extraction

This README provides instructions on how to set up and run the video frame extraction process using AWS MediaConvert.

## 1. Configure AKSK (Access Key and Secret Key)

To configure your AWS credentials, you need to set up your Access Key and Secret Key. Follow these steps:

1. Create an IAM user in your AWS account with the necessary permissions.
2. Generate an Access Key and Secret Key for this user.
3. Configure your local environment with these credentials using one of the following methods:
   - Create or edit the `~/.aws/credentials` file and add your credentials:
     ```
     [default]
     aws_access_key_id = YOUR_ACCESS_KEY
     aws_secret_access_key = YOUR_SECRET_KEY
     ```
   - Set environment variables:
     ```
     export AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
     export AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
     ```
   - Use the AWS CLI to configure your credentials:
     ```
     aws configure
     ```

## 2. Create MediaConvert Role

The `create_mediaconvert_role()` function in `create_mediaconvert_role.py` creates the necessary IAM role for MediaConvert. This role allows MediaConvert to access your S3 buckets and other required AWS services.

To create the role:

1. Ensure you have the necessary permissions to create IAM roles.
2. Run the `create_mediaconvert_role()` function. This will:
   - Create a role named 'MediaConvert_Default_Role'
   - Attach the required policies (AmazonAPIGatewayInvokeFullAccess and AmazonS3FullAccess)

## 3. Create Video Bucket

The `create_video_bucket()` function in `create_video_bucket.py` creates an S3 bucket for storing your videos and extracted frames.

To create the bucket:

1. Decide on a bucket name (default is 'video-test')
2. Choose an AWS region (default is 'us-west-2')
3. Run the `create_video_bucket()` function. This will:
   - Create the S3 bucket
   - Set up the necessary bucket policies for MediaConvert access

## 4. Run video2frame

The `main()` function in `video2frame.py` orchestrates the frame extraction process:

1. Ensure your video file is uploaded to the input S3 bucket.
2. Update the following variables in the `main()` function if needed:
   - `input_key`: The name of your video file in the S3 bucket
   - `region`: The AWS region you're using
   - `frame_interval`: The interval between frame captures (default is 88 seconds)
3. Run the `main()` function. This will:
   - Create a MediaConvert job to extract frames
   - Monitor the job status
   - Print the location of the extracted frames and output video when complete

To run the script:
```
python video2frame.py
```

After the job completes, you can find the extracted frames in `s3://{output_bucket}/frames/` and the processed video in `s3://{output_bucket}/video/`.

Note: Make sure you have the required Python libraries installed (boto3) and your AWS credentials are properly configured before running the script.
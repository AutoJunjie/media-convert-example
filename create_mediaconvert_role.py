import boto3
import json
from botocore.exceptions import ClientError

def create_mediaconvert_role():
    """
    创建 MediaConvert 服务角色并附加所需策略
    
    返回:
    str: 创建的角色 ARN
    """
    iam = boto3.client('iam')
    
    # 定义信任关系策略
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "mediaconvert.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        # 创建 IAM 角色
        response = iam.create_role(
            RoleName='MediaConvert_Default_Role',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Default role for AWS MediaConvert service'
        )
        
        role_arn = response['Role']['Arn']
        
        # 附加所需的策略
        policy_arns = [
            'arn:aws:iam::aws:policy/AmazonAPIGatewayInvokeFullAccess',
            'arn:aws:iam::aws:policy/AmazonS3FullAccess'
        ]
        
        for policy_arn in policy_arns:
            iam.attach_role_policy(
                RoleName='MediaConvert_Default_Role',
                PolicyArn=policy_arn
            )
            
        print(f"成功创建角色 MediaConvert_Default_Role")
        print(f"角色 ARN: {role_arn}")
        return role_arn
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("角色 'MediaConvert_Default_Role' 已存在")
            role = iam.get_role(RoleName='MediaConvert_Default_Role')
            return role['Role']['Arn']
        else:
            print(f"创建角色时发生错误: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        role_arn = create_mediaconvert_role()
    except Exception as e:
        print(f"发生错误: {str(e)}") 
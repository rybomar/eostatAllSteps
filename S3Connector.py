import os
import boto3
import botocore


class S3Connector:
    def __init__(self, s3AccessKey, s3SecretKey, s3Host, s3BucketName):
        self.s3AccessKey = s3AccessKey
        self.s3SecretKey = s3SecretKey
        self.s3Host = s3Host
        self.s3BucketName = s3BucketName
        self.s3Resource = boto3.resource('s3', aws_access_key_id=self.s3AccessKey, aws_secret_access_key=self.s3SecretKey, endpoint_url=self.s3Host)

    def uploadFile(self, filePath, keyFile):
        self.s3Resource.meta.client.upload_file(str(filePath), self.s3BucketName, str(keyFile))

    def checkIsKey(self, keyFile):
        try:
            self.s3Resource.Object(self.s3BucketName, keyFile).load()
            return True
        except:
            return False

    def checkSizeOfKey(self, keyFile):
        size = self.s3Resource.Bucket(self.s3BucketName).Object(keyFile).content_length
        return size

    def getAllKeyNames(self):
        keyList = []
        bucket = self.s3Resource.Bucket(self.s3BucketName)
        for my_bucket_object in bucket.objects.all():
            keyList.append(str(my_bucket_object))
        return keyList

    def uploadFileAndRemoveFromDisk(self, filePath, keyFile):
        self.uploadFile(filePath, keyFile)
        if os.path.exists(filePath):
            os.remove(filePath)

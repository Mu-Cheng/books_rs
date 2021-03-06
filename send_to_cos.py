# -*- coding=utf-8
import os

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosServiceError
from qcloud_cos import CosClientError

import sys
import logging



def main():
    # 腾讯云COSV5Python SDK, 目前可以支持Python2.6与Python2.7

    # pip安装指南:pip install -U cos-python-sdk-v5

    # cos最新可用地域,参照https://www.qcloud.com/document/product/436/6224

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    # 设置用户属性, 包括secret_id, secret_key, region
    # appid已在配置中移除,请在参数Bucket中带上appid。Bucket由bucketname-appid组成
    secret_id = 'AKIDX2Bw3v7j4vBs2pthNOIDAYjHwyazG9jJ'     # 替换为用户的secret_id
    secret_key = 'MwRrt58TEaLQnnUrMKpve8Emb1AybpbC'     # 替换为用户的secret_key
    region = 'ap-shanghai'    # 替换为用户的region
    token = ''                 # 使用临时秘钥需要传入Token，默认为空,可不填
    config = CosConfig(Region=region, Secret_id=secret_id, Secret_key=secret_key, Token=token)  # 获取配置对象
    client = CosS3Client(config)

    # response = client.get_object(
    #     Bucket='img-1252422469',
    #     Key='articles_article.csv',
    # )
    # response['Body'].get_stream_to_file('articles_article.csv')
    #
    # response = client.get_object(
    #     Bucket='img-1252422469',
    #     Key='auth_user.csv',
    # )
    # response['Body'].get_stream_to_file('auth_user.csv')
    #
    # 文件流 简单上传

    name_list = os.listdir('/home/bookimg')
    # print(name_list)

    # file_name = 'test.txt'
    # with open('test.txt', 'rb') as fp:
    for name in name_list:
        with open('/home/bookimg/'+name, 'rb') as fp:
            response = client.put_object(
                Bucket='img-1252422469',  # Bucket由bucketname-appid组成
                Body=fp,
                Key='big_bookimg/'+name,
                StorageClass='STANDARD',
                CacheControl='no-cache',
                ContentDisposition='download.txt'
            )
            print(response['ETag'])
            # break




































if __name__ == '__main__':
    main()

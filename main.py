import logging
import sys
import os
import boto3
from botocore.exceptions import ClientError
import json
import schedule
import time

AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
JENKINS_URL = os.getenv('JENKINS_URL')
JENKINS_USER = os.getenv('JENKINS_USER')
JENKINS_PASSWD = os.getenv('JENKINS_PASSWD')
SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')

# logger config
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')
sqs_client = boto3.client('sqs', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
                          aws_secret_access_key=AWS_SECRET_KEY)


def receive_queue_message(queue_url):
    """
    Retrieves one or more messages (up to 10), from the specified queue.
    """
    try:
        response = sqs_client.receive_message(QueueUrl=queue_url)
    except ClientError:
        logger.exception(
            f'Could not receive the message from the - {queue_url}.')
        raise
    else:
        return response


def delete_queue_message(queue_url, receipt_handle):
    """
    Deletes the specified message from the specified queue.
    """
    try:
        response = sqs_client.delete_message(QueueUrl=queue_url,
                                             ReceiptHandle=receipt_handle)
    except ClientError:
        logger.exception(
            f'Could not delete the meessage from the - {queue_url}.')
        raise
    else:
        return response


def run_job_jenkins(job_name: str):
    import jenkins
    server = jenkins.Jenkins(JENKINS_URL, username=JENKINS_USER, password=JENKINS_PASSWD)
    user = server.get_whoami()
    version = server.get_version()
    print('Hello %s from Jenkins %s' % (user['fullName'], version))

    jobs = server.get_jobs()
    server.build_job(job_name)


def search_for_commits():
    QUEUE_URL = SQS_QUEUE_URL
    messages = receive_queue_message(QUEUE_URL)
    print(messages)
    if not 'Messages' in messages:
        logger.info('Not message found =/')
        return False
    for msg in messages['Messages']:
        msg_body = json.loads(msg['Body'])
        receipt_handle = msg['ReceiptHandle']
        logger.info(f'The message body: {msg_body}')

        if msg_body is None:
            return False

        if 'Message' in msg_body:

            real_message_str = msg_body['Message']
            print(f"Received message: {real_message_str}")
            try:
                if real_message_str is None:
                    return False
                run_job_jenkins(real_message_str)
            except Exception as e:
                print(e)
                return False

        logger.info('Deleting message from the queue...')
        delete_queue_message(QUEUE_URL, receipt_handle)
    logger.info(f'Received and deleted message(s) from {QUEUE_URL}.')
    return True


def ignore_errors():
    try:
        search_for_commits()
    except:
        print('Ignoring errors')


if __name__ == '__main__':
    isrunning = True
    schedule.every(30).seconds.do(ignore_errors)

    while isrunning:
        schedule.run_pending()
        time.sleep(1)

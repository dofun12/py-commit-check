# py-commit-checker
A python project that verify a SQS queue to start build jobs on Jenkins

## ENVIRONMENT VARS
You need set this vars to use the service
````ini
AWS_REGION=xxxxx
AWS_ACCESS_KEY=xxxxx
AWS_SECRET_KEY=xxxx


JENKINS_URL=http://my.jenkins.host.com 
JENKINS_USER=yyyyy
JENKINS_PASSWD=xxxxx

SQS_QUEUE_URL=https://sqs.xxxxx.amazonaws.com/1234512312312/xxxxxxxx
````
The service will verify the Aws SQS once time for a minute, and if get some message it will trigger a jenkins build.

## Setting your GITHUB Repository
Your github action example

Add this file to your repo
``File: .github/workflows/sns-pub.yml ``
````yaml
name: Publish SNS Topic

on: push

jobs:
  prebuild:
    runs-on: ubuntu-latest
    steps:
      - name: sns-pub-job
        uses: nothingalike/sns-publish-topic@v1.6
        with:
            MESSAGE: "<your jenkins build name>"
            TOPIC_ARN: "<your SNS topic ARN>"
        env:
            AWS_REGION: ${{ secrets.AWS_REGION }}
            AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
            AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
````
Set the Secrets on your github project settings

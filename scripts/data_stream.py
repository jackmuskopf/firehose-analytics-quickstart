import boto3
import time
import argparse
import random
import base64
import logging

parser = argparse.ArgumentParser(description='stream data to a kinesis firehose')
parser.add_argument('--delivery-stream-name', '-n', type=str, required=True, help='The KMS CMK ID to used to generate the data key.')
parser.add_argument('--profile', type=str, default='', required=False, help="AWS profile to use")
parser.add_argument('--region', type=str, default='us-east-1', required=False, help="Stage of deployment; affects naming of ssm parameter")
parser.add_argument('--interval', type=float, default=0.3)
args = parser.parse_args()

logger = logging.getLogger()

session_kwargs = {}
if args.profile:
	session_kwargs['profile_name'] = args.profile
if args.region:
	session_kwargs['region_name'] = args.region

session = boto3.session.Session(**session_kwargs)
firehose = session.client('firehose')

def feed_data(stream, interval=0.2):

	while True:

		# wait some time
		time.sleep(interval)

		# put some data
		x = random.randint(0, 1e9)
		logger.info("Putting value {}".format(x))

		firehose.put_record(
			DeliveryStreamName=stream,
			Record={
				"Data" : str(x).encode('utf-8')
			}
		)

if __name__ == '__main__':

	logging.basicConfig(level=logging.INFO)
	feed_data(stream=args.delivery_stream_name)
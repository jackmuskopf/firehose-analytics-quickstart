import sys
import logging
import json
import base64
from app.utils import dutil, is_prime

# avoid double logging in AWS Lambda
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logger.handlers=[]
logger.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler()
formatter = logging.Formatter(
    "{'time':'%(asctime)s', 'name': '%(name)s', \
    'level': '%(levelname)s', 'message': '%(message)s'}"
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.propogate= False


# used to separate records in each file in s3
record_separator = "\n"

def process_content(content):

	number = float(content)

	# a complex type may be returned here, so take abs (however, it shouldn't theoretically, since x**(1/3): R->R)
	cube_root = abs(number**(1/3))*(1 if number >= 0 else -1)	
	
	return dict(
			content=content,
			number=number,
			size=sys.getsizeof(content),
			isPrime=is_prime(int(number)),
			cubeRoot=cube_root
		)

def transform_records(event, context):

	# to get an idea of the event structure
	paths = dutil.dot_paths(event, expand_lists=True)
	logger.debug("Event contains paths: {}".format(json.dumps(paths, indent=2)))

	# get the records and process them
	records = event.get('records') or list()
	logger.info("Received {} records".format(len(records)))

	for record in records:

		# kinesis records are base64 encoded; let's decode it
		content = base64.b64decode(
				record['data'].encode('utf-8')
			).decode('utf-8')

		# debug; don't use in production
		logger.debug(content)

		# try to process the record; otherwise, this record fails
		try:
			data_item = process_content(content)
		except Exception as e:
			logger.error("Failed to process record {}; {} {}".format(record['recordId'], type(e), e))
			record['result'] = 'ProcessingFailed'
			continue

		# dump it, encode it
		data_string = json.dumps(data_item) + record_separator
		record['data'] = base64.b64encode(data_string.encode('utf-8')).decode('utf-8')

		# debug; don't use in production! shows base64 encoded data
		logger.debug("Passing data: {}".format(record['data']))

		# mark it as 'Ok' so that Kinesis knows processing of this record was successful
		record['result'] = 'Ok'

	return {"records": records}

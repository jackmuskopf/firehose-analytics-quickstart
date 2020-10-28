SHELL=/usr/local/bin/zsh
TEST_RECORD='{"Data":"SGVsbG8gd29ybGQ="}'
AWS_REGION=us-west-1

zip:
	rm -f app.zip && zip -r9 app.zip app

put-test:
	aws firehose put-record \
		--delivery-stream-name $$(terraform output DeliveryStreamName) \
		--record ${TEST_RECORD} \
		--region ${AWS_REGION}

stream:
	python3 scripts/data_stream.py --interval=0.001 --delivery-stream-name $$(terraform output DeliveryStreamName) --region ${AWS_REGION}

apply: zip
	terraform apply

uuid:
	uuid
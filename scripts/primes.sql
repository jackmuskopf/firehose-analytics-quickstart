CREATE OR REPLACE STREAM "PRIME_NUMBER_STREAM" (number numeric, 
                                                   isPrime boolean);
-- CREATE OR REPLACE PUMP to insert into output
CREATE OR REPLACE PUMP "STREAM_PUMP" AS 
  INSERT INTO "PRIME_NUMBER_STREAM"
      SELECT "number", "isPrime"
      FROM   "firehose_in_001"
      WHERE  "isPrime";
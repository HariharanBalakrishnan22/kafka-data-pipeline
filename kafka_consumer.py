from confluent_kafka import Consumer, Producer, KafkaError
import json
import time

KAFKA_BROKER = 'localhost:29092'
SOURCE_TOPIC = 'user-login'
TARGET_TOPIC = 'processed-user-login'

def consume_messages():
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'user-login-group',
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe([SOURCE_TOPIC])

    producer = Producer({'bootstrap.servers': KAFKA_BROKER})

    def delivery_report(err, msg):
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            data = json.loads(msg.value().decode('utf-8'))

            # Basic data processing: Filter out certain device types
            if data['device_type'] == 'android':
                processed_data = {
                    'user_id': data['user_id'],
                    'timestamp': data['timestamp'],
                    'app_version': data['app_version'],
                    'device_type': data['device_type'],
                    'ip': data['ip'],
                    'processed_time': int(time.time())
                }

                producer.produce(TARGET_TOPIC, json.dumps(processed_data).encode('utf-8'), callback=delivery_report)
                producer.flush()
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    consume_messages()

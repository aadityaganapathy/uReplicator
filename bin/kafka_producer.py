import threading, logging, time
import multiprocessing
import sys

from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from datetime import datetime


class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        
    def stop(self):
        self.stop_event.set()

    def run(self):
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092'
            )
        
        counter = 1
        while True:
            counter += 1
            for i in range (0,1000):
                producer.send('testTopic', bytes(f"Partition {i} count {counter}", encoding='utf-8'), partition=i)
            time.sleep(1)
        producer.close()

class Consumer0(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()
        
    def stop(self):
        self.stop_event.set()
        
    def run(self):
        print("IN CONSUMER 2 Part 0\n")
        consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=1000)
        

        while True:
            consumer.assign([TopicPartition('testTopic2Large', 5)])
            for message in consumer:
                print("printing")
                print(message)
                print(message.value, end=" ")

        consumer.close()

class Consumer1(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()
        
    def stop(self):
        self.stop_event.set()
        
    def run(self):
        print("IN CONSUMER2 Part 1\n\n\n\n")
        consumer = KafkaConsumer(bootstrap_servers='localhost:9094',
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=1000)
        consumer.assign([TopicPartition('testTopic2_1', 1)])
        # consumer.subscribe('testTopic2_1')
        while True:
            for message in consumer:
                print(message.value)

        consumer.close()        

class Consumer2(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()
        
    def stop(self):
        self.stop_event.set()    
        
    def run(self):
        print("IN CONSUMER2 Part 2\n\n\n\n")
        consumer = KafkaConsumer(bootstrap_servers='localhost:9094',
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=1000)
        consumer.assign([TopicPartition('testTopic2_1', 2)])
        # consumer.subscribe('testTopic2_1')
        while True:
            for message in consumer:
                print(message.value)

        consumer.close()

class ConsumerSource(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()
        
    def stop(self):
        self.stop_event.set()
        
    def run(self):
        print("IN CONSUMER\n\n\n\n")
        consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=1000)
        consumer.subscribe(['testTopic'])
        print("IN CONSUMER2 All\n\n\n\n")
        # while not self.stop_event.is_set():
        while True:
            for message in consumer:
                print(message.value)
        consumer.close()

class ConsumerDest(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()
        
    def stop(self):
        self.stop_event.set()    
        
    def run(self):
        print("IN CONSUMER2 Part 2\n\n\n\n")
        consumer = KafkaConsumer(bootstrap_servers='localhost:9094',
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=1000)
        while True:
            for i in range (0,1000):
                consumer.assign([TopicPartition('testTopic_dest', i)])
                for message in consumer:
                    print(f"This is Received from {i} {message.value}")
        consumer.close()
    
        
def main():
    tasks = []
    if(sys.argv[1] == "ps"):
        print("PRODUCER")
        tasks.append(Producer())
    elif(sys.argv[1] == "cs"):
        print("CONSUMER2 0")
        tasks.append(ConsumerSource())
    elif(sys.argv[1] == "c0"):
        print("CONSUMER2")
        tasks.append(Consumer0())
    elif(sys.argv[1] == "c1"):
        print("CONSUMER2 1")
        tasks.append(Consumer1())
    elif(sys.argv[1] == "c2"):
        print("CONSUMER2 2")
        tasks.append(Consumer2())
    elif(sys.argv[1] == "cd"):
        print("CONSUMER2 Dest")
        tasks.append(ConsumerDest())   
    # tasks = [
    #     # Producer()
    #     Consumer()
    # ]

    for t in tasks:
        t.start()

    time.sleep(10)
    
    for task in tasks:
        task.stop()

    for task in tasks:
        task.join()
        
        
if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO
        )
    main()
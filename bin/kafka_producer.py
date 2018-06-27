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
        partition = 0
        with open('bin/text.txt', 'r') as f:
            for line in f:
                for word in line.split():
                    print(f"PRODUCING word to partition {partition}")
                    producer.send('testTopic2Large', bytes(f"{word} ", encoding='utf-8'), partition=partition)
                    partition += 1
        # while True:
        #     counter += 1
        #     # producer.send('testTopic2', bytes(f"{curr_time}", encoding= 'utf-8'))
        #     producer.send('testTopic2', bytes(f"Partition zero  {counter}", encoding='utf-8'), partition=0)
        #     producer.send('testTopic2', bytes(f"Partition one {counter}", encoding='utf-8'), partition=1)
        #     producer.send('testTopic2', bytes(f"Partition two {counter}", encoding='utf-8'), partition=2)
        #     # producer.send('dummyTopic', bytes(f"{curr_time}", encoding='utf-8'))
        #     time.sleep(3)
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
        consumer.subscribe(['testTopic2'])
        print("IN CONSUMER2 All\n\n\n\n")
        # while not self.stop_event.is_set():
        while True:
            for message in consumer:
                print(message.value)
                # if self.stop_event.is_set():
                #     break
        consumer.close()

class ConsumerDest(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()
        
    def stop(self):
        self.stop_event.set()
        
    def run(self):
        print("IN CONSUMER\n\n\n\n")
        consumer = KafkaConsumer(bootstrap_servers='localhost:9094',
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=1000)
        consumer.subscribe(['testTopic2_1'])
        print("IN CONSUMER2\n\n\n\n")
        # while not self.stop_event.is_set():
        while True:
            for message in consumer:
                print(message.value)
                # if self.stop_event.is_set():
                #     break
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
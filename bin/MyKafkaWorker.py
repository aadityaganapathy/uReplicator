
# coding: utf-8

# In[2]:


import sys
import json
import os
from pprint import pprint
from subprocess import call, Popen, PIPE, check_output, STDOUT, CalledProcessError
import platform
import time
import shutil
from collections import OrderedDict
import datetime
from kafka import KafkaConsumer, KafkaProducer, TopicPartition

# import matplotlib.pyplot as plt
import pandas as pd


class MyKafkaWorker():
    def __init__(self, topic):
        self.topic = topic
    
    def produce(self, port, msg_count=-1):
        producer = KafkaProducer(bootstrap_servers='localhost:{port}')

        counter = 0
        while counter != msg_count:
            counter += 1
            for i in range (0,100):
                producer.send('testTopic', bytes(f"{time.time()}"))
            time.sleep(1)
        print("finished producing")
        producer.close()
    
    def consume(self, port, msg_count=-1):
        producer = KafkaProducer(bootstrap_servers='localhost:{port}')

        counter = 0
        while counter != msg_count:
            counter += 1
            for i in range (0,100):
                producer.send('testTopic', bytes(f"{time.time()}"))
            time.sleep(1)
        print("finished producing")
        producer.close()

    def run_consumer_kill(self, topicName, pid, port, trials):
        consumer = KafkaConsumer(bootstrap_servers=f'localhost:{port}',
                                     auto_offset_reset='earliest',
                                     consumer_timeout_ms=10000000)
        consumer.subscribe([topicName])
        data_frame = pd.DataFrame()

        i = 0
        start = time.time()
        for message in consumer:
            end = time.time()
            data_frame.loc[i,'time_taken'] = end - start
            if i == (trials / 2):
                print("Killing node...")
                call(f"kill -9 {pid}", shell=True)
            elif i == trials:
                break
            i += 1
            start = time.time()

        return data_frame
    
    def test_kill_one(self, trials, fallback=-1, destTopic=''):
        node_to_port = OrderedDict([(0, 9092,), (10, 9095), (11, 9096)])
        # Want to test worst case scenario -> so get node that is assigned the most partitions
        max_leader_node = self.get_node_with_most_partitions(self.topic)

        # Get the PID of the node
        pid = self.get_node_pid(max_leader_node)

        # If the pid is not the correct port, then calling the same function will return a different number
        if pid != self.get_node_pid(max_leader_node):
            print("ERROR: Failed to get PID")
        else:
            if fallback == -1:
                # Get the port of any node other than the one we are killing
                fallback = list(node_to_port.items())[(list(node_to_port.keys()).index(max_leader_node) + 1) % len(list(node_to_port.keys()))][1]

            print(f"killing broker id {max_leader_node} | {pid}")
            print(f"Falling back to port {fallback} after killing node")

            # Spin up the consumer
            if len(destTopic) != 0:
                self.topic = destTopic
            results_kill_one = self.run_consumer_kill(self.topic, pid, fallback, trials)


            return results_kill_one
    
    def get_node_pid(self, node):
        proc1 = Popen(['ps', 'aux'], stdout=PIPE)
        proc2 = Popen(['grep', f'output/2181_cluster/broker_2181_{node}.properties'], stdin=proc1.stdout,
                                 stdout=PIPE, stderr=PIPE)
        proc3 = Popen(['awk', '{print $2}'], stdin=proc2.stdout,
                                 stdout=PIPE, stderr=PIPE)

        proc1.stdout.close()
        proc2.stdout.close()
        out, err = proc3.communicate()
        values = out.decode("utf-8").split(" ")[0]
        return int(values.split('\n')[0])
    
    def get_node_with_most_partitions(self, topic):
        proc1 = Popen(['../deploy/kafka/bin/kafka-topics.sh', '--describe', '--zookeeper', 'localhost:2181', '--topic', topic], stdout=PIPE)
        out, err = proc1.communicate()

        values = out.decode("utf-8").split(" ")

        # Get the number of times each leader appears
        leader_counts = self.get_leader_counts(values)
        
        max_val = max(leader_counts, key=lambda k: leader_counts[k])
        print(f"{leader_counts}" )
        return int(max_val)
    
    def get_leader_counts(self, values):
        leader_counts = dict()
        for i, val in enumerate(values):
            if 'Leader' in val:
                leader_node = values[i+1].split('\t')[0]
                if leader_node not in leader_counts:
                    leader_counts[leader_node] = 0
                leader_counts[leader_node] += 1
        return leader_counts
    


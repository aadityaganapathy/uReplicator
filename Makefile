list:
	deploy/kafka/bin/kafka-topics.sh --list -zookeeper localhost:2182

create:
	deploy/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic test

start_zoo:
	deploy/kafka/bin/zookeeper-server-start.sh config/zookeeper.properties

start_kafka:
	deploy/kafka/bin/kafka-server-start.sh deploy/kafka/config/server.properties

start_consumer:
	./deploy/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --from-beginning --topic testTopic
start_consumertest:
	./deploy/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --from-beginning --topic testTopic
start_consumer2:
	./deploy/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9093 --from-beginning --topic testTopic

	
start_consumer3:
	./deploy/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9094 --from-beginning --topic testTopic

start_producer:
	deploy/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic testTopic


start_producer2:
	deploy/kafka/bin/kafka-console-producer.sh --broker-list localhost:9093 --topic testTopic

start_producer3:
	deploy/kafka/bin/kafka-console-producer.sh --broker-list localhost:9094 --topic testTopic

start_controller1:
	./uReplicator-Distribution/target/uReplicator-Distribution-pkg/bin/start-controller-example1.sh

start_controller2:
	./uReplicator-Distribution/target/uReplicator-Distribution-pkg/bin/start-controller-example2.sh

start_worker1:
	./uReplicator-Distribution/target/uReplicator-Distribution-pkg/bin/start-worker-example1.sh

start_worker2:
	./uReplicator-Distribution/target/uReplicator-Distribution-pkg/bin/start-worker-example2.sh

describe_topic:
	/mnt/c/Users/Nikhilesh-singh/Documents/dev/uReplicator/deploy/kafka/bin/kafka-topics.sh --describe --zookeeper localhost:2181 --topic dummyTopic

list_servers:
	jps | grep Quorum

clean:
	dos2unix bin/stop_clusters.sh
	./bin/stop_clusters.sh && ./bin/pkg/stop-all.sh

status:
	echo dump | nc localhost 2181 | grep brokers
	echo dump | nc localhost 2182 | grep brokers
	echo dump | nc localhost 2183 | grep brokers

create_topics:
	# ./deploy/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --topic testTopic10 --partitions 10 --replication-factor 3
	# ./deploy/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --topic testTopic100 --partitions 100 --replication-factor 3
	# ./deploy/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --topic testTopic1000 --partitions 1000 --replication-factor 3
	./deploy/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2183 --topic testTopic1000_1 --partitions 1000 --replication-factor 1
# ./deploy/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --topic testTopic1000 --partitions 1000 --replication-factor 3
# ./deploy/kafka/bin/kafka-topics.sh --describe --zookeeper localhost:2181 --topic testTopic10

# ./deploy/kafka/bin/kafka-topics.sh --describe --zookeeper localhost:2181 --topic testTopic1000


# .deploy/kafka/bin/kafka-topics.sh --zookeeper localhost:2181 --alter --topic testTopic1000 --replication-factor 3
# deploy/kafka/bin/kafka-topics.sh --zookeeper localhost:2183 --alter --topic testTopic2Large_1 --partitions 1000 
# deploy/kafka/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic testTopic
#./bin/stop_clusters.sh && ./bin/pkg/stop-all.sh
# curl -X POST -d '{"topic":"testTopic2Large", "numPartitions":"1000"}' http://localhost:9000/topics

#curl -X POST -d '{"topic":"testTopic1000", "numPartitions":"1000"}' http://localhost:9000/topics
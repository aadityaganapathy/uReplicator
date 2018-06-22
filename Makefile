list:
	deploy/kafka/bin/kafka-topics.sh --list -zookeeper localhost:2182

create:
	deploy/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic test

start_zoo:
	deploy/kafka/bin/zookeeper-server-start.sh config/zookeeper.properties

start_kafka:
	deploy/kafka/bin/kafka-server-start.sh deploy/kafka/config/server.properties

start_consumer:
	./deploy/kafka/bin/kafka-console-consumer.sh --zookeeper localhost:2181 --from-beginning --topic destTopic

start_producer:
	deploy/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic srcTopic
	# deploy/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic dummyTopic

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

refresh:
	rm -rf /tmp/kafka-logs/
	bin/grid stop all
	bin/grid stop all
	./bin/pkg/stop-all.sh
	./bin/pkg/stop-all.sh
	bin/grid start all
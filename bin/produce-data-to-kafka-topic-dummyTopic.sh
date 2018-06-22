#!/bin/bash -e
echo "test"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "TEST@"
echo $DIR
BASE_DIR=$(dirname $DIR)
echo $BASE_DIR
ZOOKEEPER=localhost:2181
KAFKA_BROKER=localhost:9092

# overwritten options
while getopts "z:b:" option
do
  case ${option} in
    z) ZOOKEEPER="${OPTARG}";;
    b) KAFKA_BROKER="${OPTARG}";;
  esac
done
echo "Using ${ZOOKEEPER} as the zookeeper. You can overwrite it with '-z yourlocation'"
echo "Using ${KAFKA_BROKER} as the kafka broker. You can overwrite it with '-b yourlocation'"

# check if the topic exists. if not, create the topic
echo "IN HERE"
EXIST=$($BASE_DIR/deploy/kafka/bin/kafka-topics.sh --describe --topic dummyTopic --zookeeper $ZOOKEEPER)
if [ -z "$EXIST" ]
  then
    echo "$BASE_DIR/deploy/kafka/bin/kafka-topics.sh --create --zookeeper $ZOOKEEPER --topic dummyTopic --partitions 1 --replication-factor 1"
    $BASE_DIR/deploy/kafka/bin/kafka-topics.sh --create --zookeeper $ZOOKEEPER --topic dummyTopic --partitions 1 --replication-factor 1
fi

# produce raw data
while sleep 1
do
  echo "$BASE_DIR/deploy/kafka/bin/kafka-console-producer.sh < $BASE_DIR/bin/dummyTopicData.log --topic dummyTopic --broker $KAFKA_BROKER"
  $BASE_DIR/deploy/kafka/bin/kafka-console-producer.sh < $BASE_DIR/bin/dummyTopicData.log --topic dummyTopic --broker-list $KAFKA_BROKER
done

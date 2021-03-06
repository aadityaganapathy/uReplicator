 #!/bin/sh
 
echo "Clearing Kafka Logs..."
rm -rf /tmp/kafka-logs/
echo "Finished Clearing Kafka Logs"
value=`jps | grep Quorum`
a=($(echo "$value" | tr ' ' '\n'))

re='^[0-9]+$'

for i in "${a[@]}"; do
  if  [[ $i =~ $re ]] ; then
    echo "Stopping Zookeeper with PID: ${i}"
    kill -9 $i
  fi
done
exit
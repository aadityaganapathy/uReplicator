 #!/bin/sh
 
 echo "Clearing Kafka Logs..."
  rm -rf /tmp/kafka-logs/
#   rm -rf /tmp/zookeeper/
#   rm -rf /tmp/zookeeper-2/
  echo "Finished Clearing Kafka Logs!"
  # $DEPLOY_ROOT_DIR/kafka/bin/kafka-server-stop.sh
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
 #!/bin/sh
 
 echo "Clearing Kafka Logs..."
  rm -rf /tmp/kafka-logs/
  echo "Finished Clearing Kafka Logs!"
  # $DEPLOY_ROOT_DIR/kafka/bin/kafka-server-stop.sh
  value=`jps | grep Quorum`
  a=($(echo "$value" | tr ' ' '\n'))

  re='^[0-9]+$'
  
  for i in "${a[@]}"; do
    if  [[ $i =~ $re ]] ; then
     if ps -p $i > /dev/null
        then
          echo "Stopping Zookeeper with PID: ${i}"
          kill -9 $i
        fi
    fi
  done

value=$(ps -ef | grep 'zookeeper' | awk '{print $2}')
 for i in "${value[@]}"; do
    if  [[ $i =~ $re ]] ; then
      if ps -p $i > /dev/null
        then
          echo "Stopping Zookeeper with PID: ${i}"
          kill -9 $i
        fi
    fi
  done
echo "Stopping kafka"
value2=$(ps -ef | grep 'kafka' | awk '{print $2}')
 for i in "${value2[@]}"; do
    if  [[ $i =~ $re ]] ; then
     if ps -p $i > /dev/null
        then
          echo "Stopping Kafka with PID: ${i}"
          kill -9 $i
        fi
    fi
done
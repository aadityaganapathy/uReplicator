/*
 * Copyright (C) 2015-2017 Uber Technologies, Inc. (streaming-data@uber.com)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.uber.stream.kafka.mirrormaker.controller;

import com.uber.stream.kafka.mirrormaker.controller.core.AutoTopicWhitelistingManager;
import com.uber.stream.kafka.mirrormaker.controller.core.ClusterInfoBackupManager;
import com.uber.stream.kafka.mirrormaker.controller.core.FileBackUpHandler;
import com.uber.stream.kafka.mirrormaker.controller.core.GitBackUpHandler;
import com.uber.stream.kafka.mirrormaker.controller.core.HelixMirrorMakerManager;
import com.uber.stream.kafka.mirrormaker.controller.core.KafkaBrokerTopicObserver;
import com.uber.stream.kafka.mirrormaker.controller.reporter.HelixKafkaMirrorMakerMetricsReporter;
import com.uber.stream.kafka.mirrormaker.controller.rest.ControllerRestApplication;
import com.uber.stream.kafka.mirrormaker.controller.validation.SourceKafkaClusterValidationManager;
import com.uber.stream.kafka.mirrormaker.controller.validation.ValidationManager;
import java.util.HashMap;
import java.util.Map;
import java.util.Iterator;
import java.io.*;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.Option;
import org.restlet.Application;
import org.restlet.Component;
import org.restlet.Context;
import org.restlet.data.Protocol;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

/**
 * The main entry point for everything.
 *
 * @author xiangfu
 */
public class ControllerStarter {

  private static final String DEST_KAFKA_CLUSTER = "destKafkaCluster";
  private static final String SRC_KAFKA_CLUSTER = "srcKafkaCluster";
  private static final Logger LOGGER = LoggerFactory.getLogger(ControllerStarter.class);
  private final ControllerConf _config;

  private final Component _component;
  private final Application _controllerRestApp;
  private final HelixMirrorMakerManager _helixMirrorMakerManager;
  private final ValidationManager _validationManager;
  private final SourceKafkaClusterValidationManager _srcKafkaValidationManager;
  private final AutoTopicWhitelistingManager _autoTopicWhitelistingManager;
  private final ClusterInfoBackupManager _clusterInfoBackupManager;
  private final Map<String, KafkaBrokerTopicObserver> _kafkaBrokerTopicObserverMap =
      new HashMap<String, KafkaBrokerTopicObserver>();

  public ControllerStarter(ControllerConf conf) {
    LOGGER.info("Trying to init ControllerStarter with config: {}", conf);
    _config = conf;
    HelixKafkaMirrorMakerMetricsReporter.init(conf);
    _component = new Component();
    _controllerRestApp = new ControllerRestApplication(null);
    _helixMirrorMakerManager = new HelixMirrorMakerManager(_config);
    _validationManager = new ValidationManager(_helixMirrorMakerManager);
    _srcKafkaValidationManager = getSourceKafkaClusterValidationManager();
    _autoTopicWhitelistingManager = getAutoTopicWhitelistingManager();
    if (_config.getBackUpToGit()) {
      _clusterInfoBackupManager = new ClusterInfoBackupManager(_helixMirrorMakerManager,
          new GitBackUpHandler(conf.getRemoteBackupRepo(), conf.getLocalGitRepoPath()), _config);
    } else {
      _clusterInfoBackupManager = new ClusterInfoBackupManager(_helixMirrorMakerManager,
          new FileBackUpHandler(conf.getLocalBackupFilePath()), _config);
    }
  }

  private SourceKafkaClusterValidationManager getSourceKafkaClusterValidationManager() {
    if (_config.getEnableSrcKafkaValidation()) {
      if (!_kafkaBrokerTopicObserverMap.containsKey(SRC_KAFKA_CLUSTER)) {
        _kafkaBrokerTopicObserverMap.put(SRC_KAFKA_CLUSTER,
            new KafkaBrokerTopicObserver(SRC_KAFKA_CLUSTER, _config.getSrcKafkaZkPath(), _config.getRefreshTimeInSeconds()));
      }
      return new SourceKafkaClusterValidationManager(
          _kafkaBrokerTopicObserverMap.get(SRC_KAFKA_CLUSTER),
          _helixMirrorMakerManager, _config.getEnableAutoTopicExpansion());
    } else {
      LOGGER.info("Not init SourceKafkaClusterValidationManager!");
      return null;
    }
  }

  private AutoTopicWhitelistingManager getAutoTopicWhitelistingManager() {
    if (_config.getEnableAutoWhitelist()) {
      if (!_kafkaBrokerTopicObserverMap.containsKey(SRC_KAFKA_CLUSTER)) {
        _kafkaBrokerTopicObserverMap.put(SRC_KAFKA_CLUSTER,
            new KafkaBrokerTopicObserver(SRC_KAFKA_CLUSTER, _config.getSrcKafkaZkPath(), _config.getRefreshTimeInSeconds()));
      }
      if (!_kafkaBrokerTopicObserverMap.containsKey(DEST_KAFKA_CLUSTER)) {
        _kafkaBrokerTopicObserverMap.put(DEST_KAFKA_CLUSTER,
            new KafkaBrokerTopicObserver(DEST_KAFKA_CLUSTER, _config.getDestKafkaZkPath(), _config.getRefreshTimeInSeconds()));
      }

      String patternToExcludeTopics = _config.getPatternToExcludeTopics();
      if (patternToExcludeTopics != null && patternToExcludeTopics.trim().length() > 0) {
        patternToExcludeTopics = patternToExcludeTopics.trim();
      } else {
        patternToExcludeTopics = "";
      }
      LOGGER.info("Pattern to exclude topics is " + patternToExcludeTopics);

      return new AutoTopicWhitelistingManager(_kafkaBrokerTopicObserverMap.get(SRC_KAFKA_CLUSTER),
          _kafkaBrokerTopicObserverMap.get(DEST_KAFKA_CLUSTER), _helixMirrorMakerManager,
          patternToExcludeTopics, _config.getRefreshTimeInSeconds(), _config.getInitWaitTimeInSeconds());
    } else {
      LOGGER.info("Not init AutoTopicWhitelistingManager!");
      return null;
    }
  }

  public HelixMirrorMakerManager getHelixResourceManager() {
    return _helixMirrorMakerManager;
  }

  public void start() throws Exception {
    _component.getServers().add(Protocol.HTTP, Integer.parseInt(_config.getControllerPort()));
    _component.getClients().add(Protocol.FILE);
    _component.getClients().add(Protocol.JAR);
    _component.getClients().add(Protocol.WAR);

    final Context applicationContext = _component.getContext().createChildContext();

    LOGGER.info("injecting conf and resource manager to the api context");
    applicationContext.getAttributes().put(ControllerConf.class.toString(), _config);
    applicationContext.getAttributes().put(HelixMirrorMakerManager.class.toString(),
        _helixMirrorMakerManager);
    applicationContext.getAttributes().put(ValidationManager.class.toString(), _validationManager);

    if (_srcKafkaValidationManager != null) {
      applicationContext.getAttributes().put(SourceKafkaClusterValidationManager.class.toString(),
          _srcKafkaValidationManager);

      applicationContext.getAttributes().put(KafkaBrokerTopicObserver.class.toString(),
          _kafkaBrokerTopicObserverMap.get(SRC_KAFKA_CLUSTER));
    }
    if (_autoTopicWhitelistingManager != null) {
      applicationContext.getAttributes().put(AutoTopicWhitelistingManager.class.toString(),
          _autoTopicWhitelistingManager);
    }

    _controllerRestApp.setContext(applicationContext);

    _component.getDefaultHost().attach(_controllerRestApp);

    try {
      LOGGER.info("starting helix mirror maker manager");
      _helixMirrorMakerManager.start();
      _validationManager.start();
      if (_autoTopicWhitelistingManager != null) {
        _autoTopicWhitelistingManager.start();
      }
      if (_srcKafkaValidationManager != null) {
        _srcKafkaValidationManager.start();
      }
      if (_clusterInfoBackupManager != null) {
        _clusterInfoBackupManager.start();
      }
      LOGGER.info("starting api component");
      _component.start();
    } catch (final Exception e) {
      LOGGER.error("Caught exception while starting controller", e);
      throw e;
    }
  }

  public void stop() {
    try {
      LOGGER.info("stopping broker topic observers");
      for (String key : _kafkaBrokerTopicObserverMap.keySet()) {
        try {
          KafkaBrokerTopicObserver observer = _kafkaBrokerTopicObserverMap.get(key);
          observer.stop();
        } catch (Exception e) {
          LOGGER.error("Failed to stop KafkaBrokerTopicObserver: {}!", key);
        }
      }
      LOGGER.info("stopping api component");
      _component.stop();

      LOGGER.info("stopping resource manager");
      _helixMirrorMakerManager.stop();

    } catch (final Exception e) {
      LOGGER.error("Caught exception", e);
    }
  }

  public static ControllerConf getDefaultConf() {
    final ControllerConf conf = new ControllerConf();
    conf.setControllerPort("9000");
    conf.setZkStr("localhost:2181");
    conf.setHelixClusterName("testMirrorMaker");
    conf.setBackUpToGit("false");
    conf.setAutoRebalanceDelayInSeconds("120");
    conf.setLocalBackupFilePath("/var/log/kafka-mirror-maker-controller");
    return conf;
  }

  public static ControllerConf getSourceServer1Conf() {
    final ControllerConf conf = new ControllerConf();
    conf.setControllerPort("9000");
    conf.setZkStr("localhost:2181");
    conf.setHelixClusterName("MirrorMakerSource1");
    conf.setBackUpToGit("false");
    conf.setAutoRebalanceDelayInSeconds("120");
    conf.setLocalBackupFilePath("/var/log/kafka-mirror-maker-controller-source1");
    conf.setEnableAutoWhitelist("true");
    conf.setEnableAutoTopicExpansion("true");
    conf.setSrcKafkaZkPath("localhost:2181");
    conf.setDestKafkaZkPath("localhost:2183");
    conf.setInitWaitTimeInSeconds("10");
    conf.setRefreshTimeInSeconds("20");
    return conf;
  }

  public static ControllerConf getSourceServer2Conf() {
    final ControllerConf conf = new ControllerConf();
    conf.setControllerPort("9001");
    conf.setZkStr("localhost:2182");
    conf.setHelixClusterName("MirrorMakerSource2");
    conf.setBackUpToGit("false");
    conf.setAutoRebalanceDelayInSeconds("120");
    conf.setLocalBackupFilePath("/var/log/kafka-mirror-maker-controller-source2");
    conf.setEnableAutoWhitelist("true");
    conf.setEnableAutoTopicExpansion("true");
    conf.setSrcKafkaZkPath("localhost:2182");
    conf.setDestKafkaZkPath("localhost:2183");
    conf.setInitWaitTimeInSeconds("10");
    conf.setRefreshTimeInSeconds("20");
    return conf;
  }

// {
//         controller.port : 9001
//         controller.zk.str : localhost:2182
//         controller.helix.cluster.name : MirrorMakerSource2
//         controller.backup.to.git : false
//         controller.auto.rebalance.delay.in.seconds : 120
//         controller.local.backup.file.path : /var/log/kafka-mirror-maker-controller-source2
//         controller.enable.auto.whitelist : true
//         controller.enable.auto.topic.expansion : true
//         controller.srckafka.zkStr : localhost:2182
//         controller.destkafka.zkStr : localhost:2183
//         controller.init.wait.time.in.seconds : 10
//         controller.refresh.time.in.seconds : 20
// }
  public static ControllerConf getControllerConf(JSONObject config) {
    final ControllerConf conf = new ControllerConf();
    conf.setControllerPort((String) config.get("controllerPort"));
    conf.setZkStr((String) config.get("srcZKPort"));
    conf.setHelixClusterName((String) config.get("controllerName"));
    conf.setBackUpToGit("false");
    conf.setAutoRebalanceDelayInSeconds("120");
    conf.setLocalBackupFilePath("/var/log/" + (String) config.get("controllerName"));
    conf.setEnableAutoWhitelist("true");
    conf.setEnableAutoTopicExpansion("true");
    conf.setSrcKafkaZkPath((String) config.get("srcZKPort"));
    conf.setDestKafkaZkPath((String) config.get("destZKPort"));
    conf.setInitWaitTimeInSeconds("10");
    conf.setRefreshTimeInSeconds("20");
    return conf;
  }
  public static ControllerStarter init(CommandLine cmd) {
    ControllerConf conf = null;
    if (cmd.hasOption("SourceServer1")) {
      conf = getSourceServer1Conf();
    } else if (cmd.hasOption("SourceServer2")) {
      conf = getSourceServer2Conf();
    } else {
      try {
        conf = ControllerConf.getControllerConf(cmd);
      } catch (Exception e) {
        throw new RuntimeException("Not valid controller configurations!", e);
      }
    }
    final ControllerStarter starter = new ControllerStarter(conf);
    return starter;
  }

  public static void main(String[] args) throws Exception {
    Options options = new Options();
    Option configPath = new Option("config", true, "config file path");
    configPath.setRequired(true);
    options.addOption(configPath);

    CommandLineParser parser = new DefaultParser();
    CommandLine cmd = null;
      try {
          cmd = parser.parse(options, args);
        } catch (Exception e) {
            System.out.println(e.getMessage());
            System.exit(1);
        }
    String inputFilePath = cmd.getOptionValue("config");
    System.out.println("INPUT: " + inputFilePath);
    JSONParser jsonParser = new JSONParser();
    Object obj =  jsonParser.parse(new FileReader(inputFilePath));
    JSONObject jsonObject = (JSONObject) obj;

    JSONArray solutions = (JSONArray) jsonObject.get("controllers");


    Iterator iterator = solutions.iterator();
    while (iterator.hasNext()) {
      JSONObject controller = (JSONObject) iterator.next();
      final ControllerStarter controllerStarter = new ControllerStarter(getControllerConf(controller));

      Runtime.getRuntime().addShutdownHook(new Thread() {
        public void run() {
          try {
            controllerStarter.stop();
          } catch (Exception e) {
            LOGGER.error("Caught error during shutdown! ", e);
          }
        }
      });
      try {
        controllerStarter.start();
      } catch (Exception e) {
        LOGGER.error("Cannot start Helix Mirror Maker Controller: ", e);
      }
    }
  }
}

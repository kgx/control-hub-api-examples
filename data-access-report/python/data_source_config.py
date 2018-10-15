#!/usr/bin/env python

################################################################
##
## data_source_config.py 
##
## Specifies labels and properties to retrieve for data sources
## (i.e. SDC Origins)
##
## Key values are SDC Origin Stage Lib and config property names
##
################################################################

data_sources = {}

## HTTP Client 
data_sources['com_streamsets_pipeline_stage_origin_http_HttpClientDSource'] = {
  'label':'HTTP Client',
  'properties':{
    'conf.resourceUrl':'Resource URL',
    'conf.httpMethod':'HTTP Method'
  }
}

## Local Directory 
data_sources['com_streamsets_pipeline_stage_origin_spooldir_SpoolDirDSource'] = {
  'label': 'Local Directory',
  'properties':{
    'conf.spoolDir':'Directory', 
    'conf.filePattern':'File Pattern'
  }
}
  
## JDBC 
data_sources['com_streamsets_pipeline_stage_origin_jdbc_table_TableJdbcDSource'] = {
  'label': 'JDBC',
  'properties':{
    'hikariConfigBean.connectionString':'JDBC URL', 
    'tableJdbcConfigBean.tableConfigs/tablePattern':'Table Pattern'
  }
}

## Oracle CDC
data_sources['com_streamsets_pipeline_stage_origin_jdbc_cdc_oracle_OracleCDCDSource'] = {
  'label': 'Oracle CDC',
  'properties':{
    'hikariConf.connectionString':'JDBC URL',
    'oracleCDCConfigBean.baseConfigBean.schemaTableConfigs/schema':'Schema',
    'oracleCDCConfigBean.baseConfigBean.schemaTableConfigs/table':'Table Pattern'
  }
}

## Kafka Consumer
data_sources['com_streamsets_pipeline_stage_origin_multikafka_MultiKafkaDSource'] = {
  'label': 'Kafka Consumer',
  'properties':{
    'conf.brokerURI':'Broker URI',
    'conf.topicList':'Topic(s)'
  }
}

## Dev Data Generator 
data_sources['com_streamsets_pipeline_stage_devtest_RandomDataGeneratorSource'] = {
  'label': 'Data Generator',
  'properties':{
  }
}







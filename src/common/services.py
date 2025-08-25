"""
IBM Cloud Services Integration

This module provides utilities to integrate with optional IBM Cloud services:
- IBM Cloud Monitoring (Sysdig) for OTEL metrics
- IBM Cloud Logs for centralized logging
- Object Storage for session management and conversation history

Services are configured via environment variables and agent.yaml.
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class MonitoringConfig:
    """Configuration for IBM Cloud Monitoring (Sysdig) service."""
    enabled: bool = False
    instance_name: Optional[str] = None
    service_key_name: Optional[str] = None
    otel_endpoint: Optional[str] = None
    access_key: Optional[str] = None


@dataclass 
class LoggingConfig:
    """Configuration for IBM Cloud Logs service."""
    enabled: bool = False
    instance_name: Optional[str] = None
    service_key_name: Optional[str] = None
    ingestion_endpoint: Optional[str] = None
    ingestion_key: Optional[str] = None


@dataclass
class StorageConfig:
    """Configuration for IBM Cloud Object Storage service."""
    enabled: bool = False
    instance_name: Optional[str] = None
    service_key_name: Optional[str] = None
    bucket_name: Optional[str] = None
    endpoint: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    region: str = "us-south"


@dataclass
class ServicesConfig:
    """Complete services configuration."""
    monitoring: MonitoringConfig
    logging: LoggingConfig
    storage: StorageConfig


def load_services_config() -> ServicesConfig:
    """
    Load services configuration from environment variables.
    
    Returns:
        ServicesConfig: Complete services configuration
    """
    monitoring = MonitoringConfig(
        enabled=os.getenv('IBMCLOUD_MONITORING_ENABLED', 'false').lower() == 'true',
        instance_name=os.getenv('IBMCLOUD_MONITORING_INSTANCE'),
        service_key_name=os.getenv('IBMCLOUD_MONITORING_INSTANCE', '') + '-key' if os.getenv('IBMCLOUD_MONITORING_INSTANCE') else None,
        otel_endpoint=os.getenv('IBMCLOUD_MONITORING_OTEL_ENDPOINT'),
        access_key=os.getenv('IBMCLOUD_MONITORING_ACCESS_KEY')
    )
    
    logging_config = LoggingConfig(
        enabled=os.getenv('IBMCLOUD_LOGS_ENABLED', 'false').lower() == 'true',
        instance_name=os.getenv('IBMCLOUD_LOGS_INSTANCE'),
        service_key_name=os.getenv('IBMCLOUD_LOGS_INSTANCE', '') + '-key' if os.getenv('IBMCLOUD_LOGS_INSTANCE') else None,
        ingestion_endpoint=os.getenv('IBMCLOUD_LOGS_ENDPOINT'),
        ingestion_key=os.getenv('IBMCLOUD_LOGS_INGESTION_KEY')
    )
    
    storage = StorageConfig(
        enabled=os.getenv('IBMCLOUD_COS_ENABLED', 'false').lower() == 'true',
        instance_name=os.getenv('IBMCLOUD_COS_INSTANCE'),
        service_key_name=os.getenv('IBMCLOUD_COS_INSTANCE', '') + '-key' if os.getenv('IBMCLOUD_COS_INSTANCE') else None,
        bucket_name=os.getenv('IBMCLOUD_COS_BUCKET'),
        endpoint=os.getenv('IBMCLOUD_COS_ENDPOINT'),
        access_key_id=os.getenv('IBMCLOUD_COS_ACCESS_KEY_ID'),
        secret_access_key=os.getenv('IBMCLOUD_COS_SECRET_ACCESS_KEY'),
        region=os.getenv('IBMCLOUD_REGION', 'us-south')
    )
    
    return ServicesConfig(
        monitoring=monitoring,
        logging=logging_config,
        storage=storage
    )


def configure_otel_metrics(config: MonitoringConfig) -> bool:
    """
    Configure OpenTelemetry metrics collection to IBM Cloud Monitoring.
    
    Args:
        config: MonitoringConfig instance
        
    Returns:
        bool: True if configuration was successful
    """
    if not config.enabled or not config.otel_endpoint or not config.access_key:
        logging.info("IBM Cloud Monitoring not enabled or missing configuration")
        return False
        
    try:
        # Set OTEL environment variables for metrics export
        os.environ['OTEL_EXPORTER_OTLP_METRICS_ENDPOINT'] = config.otel_endpoint
        os.environ['OTEL_EXPORTER_OTLP_METRICS_HEADERS'] = f'Authorization=Bearer {config.access_key}'
        os.environ['OTEL_METRICS_EXPORTER'] = 'otlp'
        os.environ['OTEL_RESOURCE_ATTRIBUTES'] = f'service.name=ibmcloud-agents,service.instance.id={config.instance_name}'
        
        logging.info(f"✅ IBM Cloud Monitoring configured: {config.instance_name}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Failed to configure IBM Cloud Monitoring: {e}")
        return False


def configure_centralized_logging(config: LoggingConfig) -> bool:
    """
    Configure centralized logging to IBM Cloud Logs.
    
    Args:
        config: LoggingConfig instance
        
    Returns:
        bool: True if configuration was successful
    """
    if not config.enabled or not config.ingestion_endpoint or not config.ingestion_key:
        logging.info("IBM Cloud Logs not enabled or missing configuration")
        return False
        
    try:
        # Configure logging handler for IBM Cloud Logs
        import requests
        
        class IBMCloudLogsHandler(logging.Handler):
            def __init__(self, endpoint: str, ingestion_key: str):
                super().__init__()
                self.endpoint = endpoint
                self.ingestion_key = ingestion_key
                
            def emit(self, record):
                try:
                    log_entry = {
                        'timestamp': record.created * 1000,  # Convert to milliseconds
                        'level': record.levelname,
                        'message': record.getMessage(),
                        'logger': record.name,
                        'service': 'ibmcloud-agents'
                    }
                    
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.ingestion_key}'
                    }
                    
                    # Send log entry (async in production)
                    requests.post(
                        self.endpoint,
                        json=log_entry,
                        headers=headers,
                        timeout=5
                    )
                except Exception:
                    pass  # Don't fail the main application if logging fails
        
        # Add the IBM Cloud Logs handler to the root logger
        handler = IBMCloudLogsHandler(config.ingestion_endpoint, config.ingestion_key)
        handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(handler)
        
        logging.info(f"✅ IBM Cloud Logs configured: {config.instance_name}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Failed to configure IBM Cloud Logs: {e}")
        return False


def configure_session_storage(config: StorageConfig) -> Optional[Dict[str, Any]]:
    """
    Configure Object Storage for session management.
    
    Args:
        config: StorageConfig instance
        
    Returns:
        Optional[Dict[str, Any]]: Storage configuration for session management
    """
    if not config.enabled or not all([config.endpoint, config.access_key_id, config.secret_access_key, config.bucket_name]):
        logging.info("IBM Cloud Object Storage not enabled or missing configuration")
        return None
        
    try:
        storage_config = {
            'type': 'cos',
            'endpoint': config.endpoint,
            'access_key_id': config.access_key_id,
            'secret_access_key': config.secret_access_key,
            'bucket_name': config.bucket_name,
            'region': config.region
        }
        
        # Test the connection
        import boto3
        from botocore.exceptions import ClientError
        
        client = boto3.client(
            's3',
            endpoint_url=config.endpoint,
            aws_access_key_id=config.access_key_id,
            aws_secret_access_key=config.secret_access_key,
            region_name=config.region
        )
        
        # Test bucket access
        client.head_bucket(Bucket=config.bucket_name)
        
        logging.info(f"✅ IBM Cloud Object Storage configured: {config.instance_name}/{config.bucket_name}")
        return storage_config
        
    except ClientError as e:
        logging.error(f"❌ Failed to access COS bucket {config.bucket_name}: {e}")
        return None
    except Exception as e:
        logging.error(f"❌ Failed to configure IBM Cloud Object Storage: {e}")
        return None


def initialize_services() -> ServicesConfig:
    """
    Initialize all IBM Cloud services based on environment configuration.
    
    Returns:
        ServicesConfig: Complete services configuration
    """
    config = load_services_config()
    
    logging.info("🔧 Initializing IBM Cloud services...")
    
    # Configure monitoring
    if config.monitoring.enabled:
        configure_otel_metrics(config.monitoring)
    
    # Configure logging  
    if config.logging.enabled:
        configure_centralized_logging(config.logging)
    
    # Configure storage
    if config.storage.enabled:
        storage_config = configure_session_storage(config.storage)
        if storage_config:
            # Store storage config for session management
            os.environ['SESSION_STORAGE_CONFIG'] = str(storage_config)
    
    # Log enabled services
    enabled_services = []
    if config.monitoring.enabled:
        enabled_services.append("📊 Monitoring")
    if config.logging.enabled:
        enabled_services.append("📝 Logs")
    if config.storage.enabled:
        enabled_services.append("🗂️ Storage")
    
    if enabled_services:
        logging.info(f"✅ IBM Cloud services initialized: {', '.join(enabled_services)}")
    else:
        logging.info("ℹ️ No IBM Cloud services enabled")
    
    return config
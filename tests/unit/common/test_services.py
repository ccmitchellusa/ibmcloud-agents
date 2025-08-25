"""
Unit tests for src.common.services module.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

from src.common.services import (
    MonitoringConfig,
    LoggingConfig,
    StorageConfig,
    ServicesConfig,
    load_services_config,
    configure_otel_metrics,
    configure_centralized_logging,
    configure_session_storage,
    initialize_services,
)


class TestMonitoringConfig:
    """Test MonitoringConfig dataclass."""
    
    def test_monitoring_config_defaults(self):
        """Test MonitoringConfig default values."""
        config = MonitoringConfig()
        assert config.enabled is False
        assert config.instance_name is None
        assert config.service_key_name is None
        assert config.otel_endpoint is None
        assert config.access_key is None
    
    def test_monitoring_config_with_values(self):
        """Test MonitoringConfig with custom values."""
        config = MonitoringConfig(
            enabled=True,
            instance_name="test-monitoring",
            otel_endpoint="https://test.com",
            access_key="test-key"
        )
        assert config.enabled is True
        assert config.instance_name == "test-monitoring"
        assert config.otel_endpoint == "https://test.com"
        assert config.access_key == "test-key"


class TestLoggingConfig:
    """Test LoggingConfig dataclass."""
    
    def test_logging_config_defaults(self):
        """Test LoggingConfig default values."""
        config = LoggingConfig()
        assert config.enabled is False
        assert config.instance_name is None
        assert config.ingestion_endpoint is None
        assert config.ingestion_key is None
    
    def test_logging_config_with_values(self):
        """Test LoggingConfig with custom values."""
        config = LoggingConfig(
            enabled=True,
            instance_name="test-logs",
            ingestion_endpoint="https://logs.test.com",
            ingestion_key="test-ingestion-key"
        )
        assert config.enabled is True
        assert config.instance_name == "test-logs"
        assert config.ingestion_endpoint == "https://logs.test.com"
        assert config.ingestion_key == "test-ingestion-key"


class TestStorageConfig:
    """Test StorageConfig dataclass."""
    
    def test_storage_config_defaults(self):
        """Test StorageConfig default values."""
        config = StorageConfig()
        assert config.enabled is False
        assert config.region == "us-south"
        assert config.bucket_name is None
    
    def test_storage_config_with_values(self):
        """Test StorageConfig with custom values."""
        config = StorageConfig(
            enabled=True,
            instance_name="test-cos",
            bucket_name="test-bucket",
            endpoint="https://s3.test.com",
            access_key_id="test-access-key",
            secret_access_key="test-secret-key",
            region="us-east"
        )
        assert config.enabled is True
        assert config.instance_name == "test-cos"
        assert config.bucket_name == "test-bucket"
        assert config.region == "us-east"


class TestLoadServicesConfig:
    """Test load_services_config function."""
    
    def test_load_services_config_defaults(self, clean_environment):
        """Test loading services config with default values."""
        config = load_services_config()
        
        assert isinstance(config, ServicesConfig)
        assert config.monitoring.enabled is False
        assert config.logging.enabled is False
        assert config.storage.enabled is False
        assert config.storage.region == "us-south"
    
    def test_load_services_config_enabled(self, clean_environment):
        """Test loading services config with enabled services."""
        # Set environment variables
        os.environ.update({
            "IBMCLOUD_MONITORING_ENABLED": "true",
            "IBMCLOUD_MONITORING_INSTANCE": "test-monitoring",
            "IBMCLOUD_MONITORING_OTEL_ENDPOINT": "https://otel.test.com",
            "IBMCLOUD_MONITORING_ACCESS_KEY": "test-access-key",
            
            "IBMCLOUD_LOGS_ENABLED": "true",
            "IBMCLOUD_LOGS_INSTANCE": "test-logs",
            "IBMCLOUD_LOGS_ENDPOINT": "https://logs.test.com",
            "IBMCLOUD_LOGS_INGESTION_KEY": "test-ingestion-key",
            
            "IBMCLOUD_COS_ENABLED": "true",
            "IBMCLOUD_COS_INSTANCE": "test-cos",
            "IBMCLOUD_COS_BUCKET": "test-bucket",
            "IBMCLOUD_COS_ENDPOINT": "https://s3.test.com",
            "IBMCLOUD_COS_ACCESS_KEY_ID": "test-access-key",
            "IBMCLOUD_COS_SECRET_ACCESS_KEY": "test-secret-key",
            "IBMCLOUD_REGION": "us-east"
        })
        
        config = load_services_config()
        
        assert config.monitoring.enabled is True
        assert config.monitoring.instance_name == "test-monitoring"
        assert config.monitoring.otel_endpoint == "https://otel.test.com"
        
        assert config.logging.enabled is True
        assert config.logging.instance_name == "test-logs"
        assert config.logging.ingestion_endpoint == "https://logs.test.com"
        
        assert config.storage.enabled is True
        assert config.storage.instance_name == "test-cos"
        assert config.storage.bucket_name == "test-bucket"
        assert config.storage.region == "us-east"


class TestConfigureOtelMetrics:
    """Test configure_otel_metrics function."""
    
    def test_configure_otel_metrics_disabled(self):
        """Test configuring OTEL metrics when disabled."""
        config = MonitoringConfig(enabled=False)
        result = configure_otel_metrics(config)
        assert result is False
    
    def test_configure_otel_metrics_missing_config(self):
        """Test configuring OTEL metrics with missing configuration."""
        config = MonitoringConfig(enabled=True, otel_endpoint=None)
        result = configure_otel_metrics(config)
        assert result is False
    
    def test_configure_otel_metrics_success(self, clean_environment):
        """Test successful OTEL metrics configuration."""
        config = MonitoringConfig(
            enabled=True,
            instance_name="test-monitoring",
            otel_endpoint="https://otel.test.com",
            access_key="test-access-key"
        )
        
        result = configure_otel_metrics(config)
        
        assert result is True
        assert os.environ["OTEL_EXPORTER_OTLP_METRICS_ENDPOINT"] == "https://otel.test.com"
        assert "Bearer test-access-key" in os.environ["OTEL_EXPORTER_OTLP_METRICS_HEADERS"]
        assert os.environ["OTEL_METRICS_EXPORTER"] == "otlp"
        assert "test-monitoring" in os.environ["OTEL_RESOURCE_ATTRIBUTES"]
    
    def test_configure_otel_metrics_exception(self, clean_environment):
        """Test OTEL metrics configuration with exception."""
        config = MonitoringConfig(
            enabled=True,
            otel_endpoint="https://otel.test.com",
            access_key="test-access-key"
        )
        
        # Mock os.environ to raise an exception during configuration
        with patch('src.common.services.os.environ') as mock_environ:
            mock_environ.__setitem__ = MagicMock(side_effect=Exception("Test error"))
            result = configure_otel_metrics(config)
            assert result is False


class TestConfigureCentralizedLogging:
    """Test configure_centralized_logging function."""
    
    def test_configure_centralized_logging_disabled(self):
        """Test configuring centralized logging when disabled."""
        config = LoggingConfig(enabled=False)
        result = configure_centralized_logging(config)
        assert result is False
    
    def test_configure_centralized_logging_missing_config(self):
        """Test configuring centralized logging with missing configuration."""
        config = LoggingConfig(enabled=True, ingestion_endpoint=None)
        result = configure_centralized_logging(config)
        assert result is False
    
    def test_configure_centralized_logging_success(self, mock_requests):
        """Test successful centralized logging configuration."""
        config = LoggingConfig(
            enabled=True,
            instance_name="test-logs",
            ingestion_endpoint="https://logs.test.com",
            ingestion_key="test-ingestion-key"
        )
        
        result = configure_centralized_logging(config)
        assert result is True
    
    def test_configure_centralized_logging_exception(self):
        """Test centralized logging configuration with exception."""
        config = LoggingConfig(
            enabled=True,
            ingestion_endpoint="https://logs.test.com",
            ingestion_key="test-ingestion-key"
        )
        
        with patch('src.common.services.logging.getLogger') as mock_logger:
            mock_logger.side_effect = Exception("Test error")
            result = configure_centralized_logging(config)
            assert result is False


class TestConfigureSessionStorage:
    """Test configure_session_storage function."""
    
    def test_configure_session_storage_disabled(self):
        """Test configuring session storage when disabled."""
        config = StorageConfig(enabled=False)
        result = configure_session_storage(config)
        assert result is None
    
    def test_configure_session_storage_missing_config(self):
        """Test configuring session storage with missing configuration."""
        config = StorageConfig(enabled=True, endpoint=None)
        result = configure_session_storage(config)
        assert result is None
    
    def test_configure_session_storage_success(self, mock_boto3):
        """Test successful session storage configuration."""
        config = StorageConfig(
            enabled=True,
            instance_name="test-cos",
            bucket_name="test-bucket",
            endpoint="https://s3.test.com",
            access_key_id="test-access-key",
            secret_access_key="test-secret-key",
            region="us-south"
        )
        
        result = configure_session_storage(config)
        
        assert result is not None
        assert result["type"] == "cos"
        assert result["endpoint"] == "https://s3.test.com"
        assert result["bucket_name"] == "test-bucket"
        assert result["region"] == "us-south"
        
        # Verify boto3 client was called
        mock_boto3.head_bucket.assert_called_once_with(Bucket="test-bucket")
    
    def test_configure_session_storage_client_error(self, mock_boto3):
        """Test session storage configuration with client error."""
        mock_boto3.head_bucket.side_effect = ClientError(
            error_response={"Error": {"Code": "NoSuchBucket"}},
            operation_name="head_bucket"
        )
        
        config = StorageConfig(
            enabled=True,
            instance_name="test-cos",
            bucket_name="test-bucket",
            endpoint="https://s3.test.com",
            access_key_id="test-access-key",
            secret_access_key="test-secret-key"
        )
        
        result = configure_session_storage(config)
        assert result is None
    
    def test_configure_session_storage_exception(self):
        """Test session storage configuration with exception."""
        config = StorageConfig(
            enabled=True,
            bucket_name="test-bucket",
            endpoint="https://s3.test.com",
            access_key_id="test-access-key",
            secret_access_key="test-secret-key"
        )
        
        with patch('boto3.client', side_effect=Exception("Test error")):
            result = configure_session_storage(config)
            assert result is None


class TestInitializeServices:
    """Test initialize_services function."""
    
    def test_initialize_services_all_disabled(self, clean_environment):
        """Test initializing services when all are disabled."""
        config = initialize_services()
        
        assert isinstance(config, ServicesConfig)
        assert config.monitoring.enabled is False
        assert config.logging.enabled is False
        assert config.storage.enabled is False
    
    @patch('src.common.services.configure_otel_metrics')
    @patch('src.common.services.configure_centralized_logging')
    @patch('src.common.services.configure_session_storage')
    def test_initialize_services_all_enabled(self, mock_storage, mock_logging, mock_otel, clean_environment):
        """Test initializing services when all are enabled."""
        # Set up environment
        os.environ.update({
            "IBMCLOUD_MONITORING_ENABLED": "true",
            "IBMCLOUD_LOGS_ENABLED": "true",
            "IBMCLOUD_COS_ENABLED": "true",
        })
        
        # Configure mocks
        mock_otel.return_value = True
        mock_logging.return_value = True
        mock_storage.return_value = {"type": "cos", "bucket": "test"}
        
        config = initialize_services()
        
        assert config.monitoring.enabled is True
        assert config.logging.enabled is True
        assert config.storage.enabled is True
        
        # Verify functions were called
        mock_otel.assert_called_once()
        mock_logging.assert_called_once()
        mock_storage.assert_called_once()
        
        # Verify storage config was set in environment
        assert "SESSION_STORAGE_CONFIG" in os.environ
    
    @patch('src.common.services.configure_session_storage')
    def test_initialize_services_storage_config_none(self, mock_storage, clean_environment):
        """Test initializing services when storage config returns None."""
        os.environ["IBMCLOUD_COS_ENABLED"] = "true"
        mock_storage.return_value = None
        
        config = initialize_services()
        
        assert config.storage.enabled is True
        assert "SESSION_STORAGE_CONFIG" not in os.environ
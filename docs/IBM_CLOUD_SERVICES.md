# IBM Cloud Services Integration 📊📝🗂️

This document details the optional IBM Cloud services integration for production deployments of the IBM Cloud Agents.

## Overview

The IBM Cloud Agents project supports optional integration with three key IBM Cloud services for production deployments:

- **📊 IBM Cloud Monitoring (Sysdig)** - OTEL metrics collection and application monitoring
- **📝 IBM Cloud Logs** - Centralized logging and log analysis  
- **🗂️ Object Storage** - Persistent session management and conversation history

These services are **optional** and the agents will work perfectly fine without them for development and testing scenarios.

## Quick Setup

You can create the required IBM Cloud services using either the **Terraform Deployable Architecture** (recommended) or the **Manual Makefile** approach.

### Option 1: Terraform Deployable Architecture (Recommended)

For a production-ready, infrastructure-as-code approach, use the dedicated deployable architecture:

```bash
# Clone the deployable architecture
git clone https://github.com/ccmitchellusa/terraform-ibm-agentic-services.git
cd terraform-ibm-agentic-services

# Configure terraform variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your configuration

# Deploy all services
terraform init
terraform plan
terraform apply

# Get service credentials for your .env.ibmcloud file
terraform output -json environment_variables | jq -r 'to_entries[] | "\(.key)=\(.value)"' >> .env.ibmcloud
```

**Benefits of the Terraform approach:**
- ✅ **Production-ready**: Uses official IBM Terraform modules
- ✅ **Repeatable**: Infrastructure as code with version control
- ✅ **Modular**: Enable/disable services as needed
- ✅ **Integrated**: Services are properly connected (monitoring, activity tracking)
- ✅ **Scalable**: Easy to modify and extend

### Option 2: Manual Makefile Approach

For quick development setups or when Terraform isn't available:

```bash
# Copy the example configuration
cp .env.ibmcloud.example .env.ibmcloud

# Edit with your IBM Cloud settings (region, project name, resource group, etc.)
vim .env.ibmcloud

# Create all supporting services with one command
make ibmcloud-services-setup
```

This command creates:
- IBM Cloud Monitoring (Sysdig) instance  
- IBM Cloud Logs instance
- Object Storage instance and bucket
- Service credentials for all services

### 3. Get Service Credentials

```bash
# Display environment variables for the created services
make ibmcloud-services-env
```

Copy the output and add it to your `.env.ibmcloud` file.

### 4. Enable Services

Edit your `.env.ibmcloud` file and set the desired services to enabled:

```bash
IBMCLOUD_MONITORING_ENABLED=true
IBMCLOUD_LOGS_ENABLED=true  
IBMCLOUD_COS_ENABLED=true
```

### 5. Deploy

```bash
# Deploy to IBM Cloud with all services enabled
make ibmcloud-all
```

## Service Details

### IBM Cloud Monitoring (Sysdig)

**Purpose**: Application monitoring and OTEL metrics collection

**Configuration Variables**:
```bash
IBMCLOUD_MONITORING_ENABLED=true
IBMCLOUD_MONITORING_INSTANCE=my-project-monitoring
IBMCLOUD_MONITORING_ACCESS_KEY=your-access-key
IBMCLOUD_MONITORING_OTEL_ENDPOINT=https://ingest.region.monitoring.cloud.ibm.com/v1/metrics
```

**What it does**:
- Automatically configures OpenTelemetry metrics export
- Collects application metrics, request traces, and performance data
- Provides dashboards for monitoring agent health and usage
- Sets up alerts for agent failures or performance issues

**Manual setup**:
```bash
make ibmcloud-monitoring-create
```

### IBM Cloud Logs

**Purpose**: Centralized logging and log analysis

**Configuration Variables**:
```bash
IBMCLOUD_LOGS_ENABLED=true
IBMCLOUD_LOGS_INSTANCE=my-project-logs
IBMCLOUD_LOGS_INGESTION_KEY=your-ingestion-key
IBMCLOUD_LOGS_ENDPOINT=https://logs.region.logging.cloud.ibm.com/logs/ingest
```

**What it does**:
- Automatically sends application logs to IBM Cloud Logs
- Provides centralized log search and analysis
- Enables structured logging with JSON format
- Supports log aggregation across multiple agent instances

**Manual setup**:
```bash
make ibmcloud-logs-create
```

### Object Storage (COS)

**Purpose**: Session management and conversation history persistence

**Configuration Variables**:
```bash
IBMCLOUD_COS_ENABLED=true
IBMCLOUD_COS_INSTANCE=my-project-cos
IBMCLOUD_COS_BUCKET=my-project-sessions
IBMCLOUD_COS_ENDPOINT=https://s3.region.cloud-object-storage.appdomain.cloud
IBMCLOUD_COS_ACCESS_KEY_ID=your-access-key
IBMCLOUD_COS_SECRET_ACCESS_KEY=your-secret-key
```

**What it does**:
- Stores session data persistently across agent restarts
- Maintains conversation history for improved context
- Enables session sharing across multiple agent instances
- Provides backup and recovery for agent state

**Manual setup**:
```bash
make ibmcloud-cos-create
```

## Technical Architecture

### Service Initialization

Services are initialized in [`src/common/services.py`](../src/common/services.py) during application startup:

1. **Environment Detection**: Checks for enabled services via environment variables
2. **Configuration Loading**: Loads service credentials and endpoints
3. **Service Setup**: Configures OTEL exporters, logging handlers, and storage clients
4. **Health Checks**: Verifies connectivity to each enabled service

### Integration Points

- **Agent Startup**: [`src/ibmcloud_base_agent/main.py`](../src/ibmcloud_base_agent/main.py) initializes services before starting the a2a-server
- **Configuration**: [`agent.yaml`](../agent.yaml) contains service configuration templates with environment variable substitution
- **Monitoring**: OTEL metrics are automatically exported when monitoring is enabled
- **Logging**: Python logging handlers automatically send logs to IBM Cloud Logs
- **Storage**: Session data is automatically persisted to Object Storage

### Deployment Integration

The Makefile includes comprehensive deployment support:

- `make ibmcloud-services-setup` - Creates all services
- `make ibmcloud-services-env` - Extracts credentials 
- `make ibmcloud-all` - Complete deployment pipeline
- `make ibmcloud-deploy` - Deploy with service integration

## Troubleshooting

### Services Not Working

1. **Check service status**:
   ```bash
   ibmcloud resource service-instances
   ```

2. **Verify credentials**:
   ```bash
   make ibmcloud-services-env
   ```

3. **Check application logs**:
   ```bash
   make ibmcloud-ce-logs
   ```

### Common Issues

**Monitoring not receiving metrics**:
- Verify `IBMCLOUD_MONITORING_ACCESS_KEY` is correct
- Check OTEL endpoint configuration
- Confirm network connectivity from Code Engine

**Logs not appearing**:
- Verify `IBMCLOUD_LOGS_INGESTION_KEY` is correct
- Check logs endpoint configuration
- Confirm log level is set appropriately

**Storage not persisting sessions**:
- Verify COS credentials and bucket access
- Check bucket exists and is accessible
- Confirm network connectivity to COS endpoint

### Service Plans

Default service plans are:
- **Monitoring**: `graduated-tier` (free tier available)
- **Logs**: `standard` (pay-as-you-go)
- **Object Storage**: `standard` (free tier available)

You can customize plans by setting:
```bash
IBMCLOUD_MONITORING_PLAN=lite
IBMCLOUD_LOGS_PLAN=standard  
IBMCLOUD_COS_PLAN=lite
```

## Cost Optimization

- **Development**: Disable all services (`*_ENABLED=false`)
- **Testing**: Enable only logs for debugging  
- **Production**: Enable all services for full observability

Free tiers are available for monitoring and storage services, making it cost-effective to use these services even for smaller deployments.

## Security Considerations

- Service credentials are stored as environment variables
- All communications use TLS/HTTPS
- IBM Cloud IAM controls access to services
- Object Storage uses HMAC keys for secure access
- Consider using IBM Cloud Secrets Manager for credential management in production

## Migrating from Makefile to Terraform Deployable Architecture

If you're currently using the Makefile approach and want to migrate to the Terraform deployable architecture:

### 1. Export Current Configuration

```bash
# Get your current service configuration
make ibmcloud-services-env > current-services.env
```

### 2. Set Up Terraform Deployable Architecture

```bash
# Clone the deployable architecture
git clone https://github.com/ccmitchellusa/terraform-ibm-agentic-services.git
cd terraform-ibm-agentic-services

# Create terraform variables file matching your current setup
cat > terraform.tfvars << EOF
prefix              = "your-project-name"
region             = "us-south"  # or your current region
resource_group_name = "default"   # or your current resource group

# Enable services you currently use
enable_monitoring = true
enable_logs      = true
enable_cos       = true
EOF
```

### 3. Import Existing Resources (Optional)

If you want to manage existing resources with Terraform:

```bash
# Import existing resources (requires service IDs from IBM Cloud)
terraform import 'module.observability[0].ibm_resource_instance.sysdig_instance' <monitoring-service-id>
terraform import 'module.cos[0].ibm_resource_instance.cos_instance' <cos-service-id>
```

### 4. Replace Makefile Commands

| Old Makefile Command | New Terraform Command |
|---------------------|----------------------|
| `make ibmcloud-services-setup` | `terraform apply` |
| `make ibmcloud-services-env` | `terraform output environment_variables` |
| Service updates | `terraform plan && terraform apply` |

### 5. Benefits After Migration

- **Version Control**: Infrastructure changes are tracked in Git
- **Team Collaboration**: Multiple developers can work with the same infrastructure definition  
- **Automated Testing**: CI/CD pipelines can validate infrastructure changes
- **Disaster Recovery**: Complete infrastructure can be recreated from code
- **Cost Management**: Better resource lifecycle management

## Next Steps

1. **For Terraform users**: Review the [terraform-ibm-agentic-services repository](https://github.com/ccmitchellusa/terraform-ibm-agentic-services) documentation
2. **For Makefile users**: Review the [Makefile](../Makefile) for all available service commands
3. Examine [`src/common/services.py`](../src/common/services.py) for implementation details
4. Customize service configuration in [`agent.yaml`](../agent.yaml) as needed
5. Set up monitoring dashboards in IBM Cloud Monitoring console
6. Configure log analysis and alerting in IBM Cloud Logs console

For questions or issues, refer to the main [README](../README.md) or open an issue on GitHub.

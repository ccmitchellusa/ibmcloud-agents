import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from a2a_server.run import run_server
from src.common.services import initialize_services

def main():
    """
    Main entry point for IBM Cloud Agents.
    
    This initializes optional IBM Cloud services (monitoring, logs, storage)
    and then starts the a2a-server.
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting IBM Cloud Agents...")
    
    # Initialize optional IBM Cloud services
    try:
        services_config = initialize_services()
        logger.info("📦 IBM Cloud services initialization completed")
    except Exception as e:
        logger.warning(f"⚠️ IBM Cloud services initialization failed: {e}")
        logger.info("📦 Continuing without optional services...")
    
    # Start the a2a-server
    logger.info("🌟 Starting a2a-server...")
    run_server()

if __name__ == "__main__":
    main()
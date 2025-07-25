from dotenv import load_dotenv

load_dotenv()

from a2a_server.run import run_server
from ibmcloud_serverless_agent import agent

def main():
    run_server()

if __name__ == "__main__":
    main()
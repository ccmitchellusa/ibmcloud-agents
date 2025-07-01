from dotenv import load_dotenv

load_dotenv()

from a2a_server.run import run_server

def main():
    run_server()

if __name__ == "__main__":
    main()
    
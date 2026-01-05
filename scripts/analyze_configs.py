
import json
import os
import sys

def analyze():
    with open('temp_configs_list.txt', 'r') as f:
        paths = [line.strip() for line in f if line.strip()]

    print(f"Found {len(paths)} config files.")
    
    results = []
    
    for path in paths:
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Assuming structure: mcpServers -> <server_name> -> args
            # server_name usually 'ibmcloud' or 'ibmcloud-something'
            # We want the args list
            
            mcp_servers = data.get('mcpServers', {})
            tools = "UNKNOWN"
            server_name = "UNKNOWN"
            
            for s_name, s_config in mcp_servers.items():
                server_name = s_name
                args = s_config.get('args', [])
                if '--mcp-tools' in args:
                    idx = args.index('--mcp-tools')
                    if idx + 1 < len(args):
                        tools = args[idx+1]
                elif 'args' in s_config and isinstance(s_config['args'], list):
                     pass 

            # Extract domain from path: .../src/<domain>/configs/...
            parts = path.split('/')
            try:
                src_index = parts.index('src')
                domain = parts[src_index + 1]
            except ValueError:
                domain = "unknown"
                
            filename = os.path.basename(path)
            
            results.append(f"{domain}|{filename}|{server_name}|{tools}")
            
        except Exception as e:
            print(f"Error reading {path}: {e}")

    results.sort()
    for r in results:
        print(r)

if __name__ == "__main__":
    analyze()

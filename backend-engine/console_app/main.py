import sys
import os
import logging

# Add parent directory to path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.core.runner import run_automation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_multiline_input(prompt):
    print(prompt)
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return lines

def main():
    while True:
        clear_screen()
        print("=== AutoISP Console App ===")
        print("1. Run Automation")
        print("2. Exit")
        
        choice = input("\nSelect an option: ")
        
        if choice == "2":
            break
        
        if choice == "1":
            # 1. Select Provider
            print("\nAvailable Providers:")
            print("1. gmx")
            print("2. webde")
            
            provider_choice = input("\nSelect Provider (1-2): ")
            provider = "gmx" if provider_choice == "1" else "webde" if provider_choice == "2" else None
            
            if not provider:
                print("Invalid provider selected.")
                input("Press Enter to continue...")
                continue
                
            # 2. Select Automation
            print(f"\nAvailable Automations for {provider}:")
            # Hardcoded for now based on research, could be dynamic
            automations = ["authenticate", "report_not_spam"]
            for idx, auto in enumerate(automations, 1):
                print(f"{idx}. {auto}")
                
            auto_choice = input(f"\nSelect Automation (1-{len(automations)}): ")
            try:
                automation_name = automations[int(auto_choice) - 1]
            except (ValueError, IndexError):
                print("Invalid automation selected.")
                input("Press Enter to continue...")
                continue

            # Handle specific parameters
            automation_params = {}
            if automation_name == "report_not_spam":
                search_text = input("\nEnter text to search for (for report not spam): ")
                automation_params["text"] = search_text
                
            # 3. Select Device Type
            print("\nSelect Device Type:")
            print("1. Desktop")
            print("2. Mobile")
            
            device_choice = input("\nSelect Device Type (1-2): ")
            device_type = "desktop" if device_choice == "1" else "mobile" if device_choice == "2" else None
            
            if not device_type:
                print("Invalid device type selected. Defaulting to 'desktop'.")
                device_type = "desktop"

            # 4. Input Accounts
            print("\nEnter Accounts (email:password[:proxy[:port[:username[:password]]]]), one per line.")
            print("Proxy format examples:")
            print("  - email:password")
            print("  - email:password:proxy.server.com:8080")
            print("  - email:password:proxy.server.com:8080:proxyuser:proxypass")
            print("Press Enter twice to finish.")
            account_lines = get_multiline_input("Paste accounts here:")
            
            if not account_lines:
                print("No accounts provided.")
                input("Press Enter to continue...")
                continue
                
            print(f"\nStarting {automation_name} for {len(account_lines)} accounts on {provider} ({device_type})...")
            
            for line in account_lines:
                if ":" not in line:
                    print(f"Skipping invalid format: {line}")
                    continue
                
                parts = line.strip().split(":")
                if len(parts) < 2:
                    print(f"Skipping invalid format (need at least email:password): {line}")
                    continue
                
                email = parts[0]
                password = parts[1]
                proxy_config = None
                
                # Parse proxy configuration if provided
                if len(parts) >= 3:
                    proxy_server = parts[2]
                    proxy_port = parts[3] if len(parts) >= 4 else "8080"
                    proxy_username = parts[4] if len(parts) >= 5 else None
                    proxy_password = parts[5] if len(parts) >= 6 else None
                    
                    proxy_config = {
                        "host": proxy_server,
                        "port": proxy_port,
                        "username": proxy_username,
                        "password": proxy_password,
                        "type": "http"
                    }
                    print(f"Running {email} with proxy {proxy_server}:{proxy_port}")
                else:
                    print(f"Running {email} without proxy")
                
                try:
                    run_automation(
                        email=email, 
                        password=password, 
                        isp=provider, 
                        automation_name=automation_name,
                        device_type=device_type,
                        proxy_config=proxy_config,
                        **automation_params
                    )
                except Exception as e:
                    print(f"Error running for {email}: {e}")
            
            print("\nBatch execution completed.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()

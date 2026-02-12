import os
import sys
import logging
import argparse
import importlib
import concurrent.futures
import multiprocessing
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Ensure the light-engine directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
# Add modules directory to path to support 'from automations...' imports
modules_path = os.path.join(current_dir, "modules")
if modules_path not in sys.path:
    sys.path.insert(0, modules_path)

from modules.core.models import Account
from modules.core.automation_metadata import AutomationMetadata
from modules.core.flow_state import FlowResult

# Static Paths
DATA_DIR = os.path.join(current_dir, "data")
OUTPUT_DIR = os.path.join(current_dir, "output")
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.txt")
PROXIES_FILE = os.path.join(DATA_DIR, "proxies.txt")

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("light_engine")

# Module-level worker state (shared across processes via initializer)
_worker_lock = None
_worker_status_counts = None
_worker_run_output_dir = None

def init_worker(lock, status_counts, run_output_dir):
    """Initialize worker process with shared state."""
    global _worker_lock, _worker_status_counts, _worker_run_output_dir
    _worker_lock = lock
    _worker_status_counts = status_counts
    _worker_run_output_dir = run_output_dir

def read_accounts() -> List[Dict[str, str]]:
    accounts = []
    if not os.path.exists(ACCOUNTS_FILE):
        logger.error(f"Accounts file not found: {ACCOUNTS_FILE}")
        return accounts

    with open(ACCOUNTS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(":")
            if len(parts) >= 2:
                accounts.append({
                    "email": parts[0],
                    "password": parts[1]
                })
            else:
                logger.warning(f"Invalid account line: {line}")
    return accounts

def read_proxies() -> List[str]:
    proxies = []
    if not os.path.exists(PROXIES_FILE):
        logger.warning(f"Proxies file not found: {PROXIES_FILE}")
        return proxies

    with open(PROXIES_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                proxies.append(line)
    return proxies

def process_account_worker(account_data: Dict[str, str], proxy: str, provider: str, automation_name: str, account_type: str, index: int, **kwargs) -> str:
    """
    Worker function to process a single account.
    This runs in a separate process.
    """
    global _worker_lock, _worker_status_counts, _worker_run_output_dir
    
    print(f"[{index}] Starting account: {account_data['email']}")
    
    # Create account-specific log directory
    email = account_data['email']
    email_folder_name = email.replace("@", "_").replace(".", "_")
    account_log_dir = os.path.join(_worker_run_output_dir, "accounts", email_folder_name)
    os.makedirs(account_log_dir, exist_ok=True)
    
    # Setup file handler for this account - add to 'autoisp' logger used by automations
    autoisp_logger = logging.getLogger("autoisp")
    autoisp_logger.setLevel(logging.INFO)
    log_file_path = os.path.join(account_log_dir, "log.txt")
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    autoisp_logger.addHandler(file_handler)
    
    status = "FAILED"
    try:
        result = run_automation(
            account_data=account_data,
            proxy=proxy,
            provider=provider,
            automation_name=automation_name,
            account_type=account_type,
            log_dir=account_log_dir,
            **kwargs
        )
        
        # Determine status from result
        if isinstance(result, dict):
            status = result.get("status", "FAILED").upper()
        elif isinstance(result, FlowResult):
            status = result.name
        elif isinstance(result, str):
            status = result.upper()
            
        # Handle specific statuses by saving to files
        if status in ("COMPLETED", "SUCCESS", "FAILED", "ABORT", "SUSPENDED", "WRONG_EMAIL", "WRONG_PASSWORD", "PHONE_VERIFICATION", "CAPTCHA", "LOCKED", "ADD_PROTECTION"):
            filename = f"{status.lower()}_accounts.txt"
            filepath = os.path.join(_worker_run_output_dir, filename)
            
            if _worker_lock:
                with _worker_lock:
                    with open(filepath, "a") as f:
                        f.write(f"{account_data['email']}:{account_data['password']}\n")
            else:
                 with open(filepath, "a") as f:
                        f.write(f"{account_data['email']}:{account_data['password']}\n")
            
            autoisp_logger.info(f"Account marked as {status}")

    except Exception as e:
        autoisp_logger.error(f"Worker error: {e}")
        status = "ERROR"
    finally:
        # Clean up file handler
        file_handler.close()
        autoisp_logger.removeHandler(file_handler)
        
    # Update shared status counts
    if _worker_status_counts is not None and _worker_lock is not None:
        with _worker_lock:
            current = _worker_status_counts.get(status, 0)
            _worker_status_counts[status] = current + 1
            
    return status

def run_automation(account_data: Dict[str, str], proxy: str, provider: str, automation_name: str, account_type: str, **kwargs):
    account_id = account_data["email"].replace("@", "_").replace(".", "_")
    
    proxy_settings = None
    if proxy:
        # Support format: username:password@ip:port
        try:
            if "@" in proxy:
                creds, server = proxy.split("@")
                username, password = creds.split(":")
                host, port = server.split(":")
                proxy_settings = {
                    "protocol": "http",
                    "host": host,
                    "port": int(port),
                    "username": username,
                    "password": password
                }
            else:
                # Fallback to simple host:port or URL
                from urllib.parse import urlparse
                if "://" not in proxy:
                    proxy = "http://" + proxy
                parsed = urlparse(proxy)
                proxy_settings = {
                    "protocol": parsed.scheme or "http",
                    "host": parsed.hostname,
                    "port": parsed.port or 80,
                }
                if parsed.username:
                    proxy_settings["username"] = parsed.username
                if parsed.password:
                    proxy_settings["password"] = parsed.password
        except Exception as e:
            logger.error(f"Failed to parse proxy {proxy}: {e}")
            proxy_settings = {"server": proxy} # Fallback

    account = Account(
        id=account_id,
        email=account_data["email"],
        password=account_data["password"],
        provider=provider,
        proxy_settings=proxy_settings,
        type=account_type,
        credentials={"password": account_data["password"]}
    )

    logger.info(f"Starting {automation_name} for {account.email} using proxy: {proxy or 'None'}")

    try:
        # Import the automation's loader.py
        loader_module_path = f"modules.automations.{provider}.{automation_name}.loader"
        loader = importlib.import_module(loader_module_path)

        if not hasattr(loader, "run"):
            raise AttributeError(f"{loader_module_path} missing 'run(account, job_id, **kwargs)' function")

        result = loader.run(account=account, **kwargs)
        logger.info(f"Finished {automation_name} for {account.email}. Result: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to run automation {automation_name} for {account.email}: {e}")
        return {"status": "failed", "message": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Light Automation Engine")
    parser.add_argument("--provider", help="ISP provider (e.g., webde, gmx)")
    parser.add_argument("--automation", help="Automation name (e.g., authenticate)")
    parser.add_argument("--type", default="desktop", choices=["desktop", "mobile"], help="Account type")
    parser.add_argument("--workers", type=int, default=10, help="Number of concurrent workers")
    
    args = parser.parse_args()

    # Interactive prompts if arguments are missing
    provider = args.provider
    if not provider:
        # Try to list available providers
        automations_dir = os.path.join(current_dir, "modules", "automations")
        available_providers = []
        if os.path.exists(automations_dir):
            available_providers = [d for d in os.listdir(automations_dir) 
                                 if os.path.isdir(os.path.join(automations_dir, d)) and not d.startswith("__")]
        
        if available_providers:
            print("\nAvailable providers:")
            for i, p in enumerate(available_providers, 1):
                print(f"  {i}. {p}")
            
            choice = input(f"\nSelect provider (1-{len(available_providers)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_providers):
                    provider = available_providers[idx]
                else:
                    provider = choice # Fallback to literal if number is out of range
            except ValueError:
                provider = choice # Fallback to literal if not a number
        else:
            provider = input("Enter ISP provider (e.g., webde, gmx): ").strip()

    automation = args.automation
    if not automation:
        # Try to list available automations for the selected provider
        provider_dir = os.path.join(current_dir, "modules", "automations", provider)
        available_automations = []
        if os.path.exists(provider_dir):
            available_automations = [d for d in os.listdir(provider_dir) 
                                   if os.path.isdir(os.path.join(provider_dir, d)) and not d.startswith("__")]
        
        if available_automations:
            print(f"\nAvailable automations for {provider}:")
            for i, a in enumerate(available_automations, 1):
                print(f"  {i}. {a}")
            
            choice = input(f"\nSelect automation (1-{len(available_automations)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_automations):
                    automation = available_automations[idx]
                else:
                    automation = choice # Fallback to literal if number is out of range
            except ValueError:
                automation = choice # Fallback to literal if not a number
        else:
            automation = input("Enter automation name (e.g., authenticate): ").strip()

    if not provider or not automation:
        logger.error("Provider and automation name are required.")
        return

    # Ensure data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Created data directory: {DATA_DIR}")

    if not os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "w") as f:
            f.write("# email:password\n")
        logger.info(f"Created empty accounts file: {ACCOUNTS_FILE}")

    if not os.path.exists(PROXIES_FILE):
        with open(PROXIES_FILE, "w") as f:
            f.write("# http://user:pass@host:port\n")
        logger.info(f"Created empty proxies file: {PROXIES_FILE}")

    accounts = read_accounts()
    proxies = read_proxies()

    if not accounts:
        logger.error("No accounts found to process. Please add them to data/accounts.txt")
        return

    logger.info(f"Found {len(accounts)} accounts and {len(proxies)} proxies.")

    automation_kwargs = {}
    if automation == "report_not_spam":
        search_text = input("Enter search keyword (optional, press Enter to skip): ").strip()
        days_str = input("Enter how many days back to search (default 7): ").strip()
        
        try:
            days_back = int(days_str) if days_str else 7
        except ValueError:
            logger.warning(f"Invalid days value '{days_str}', defaulting to 7")
            days_back = 7
            
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        automation_kwargs = {
            "keyword": search_text if search_text else None,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        msg = f"ReportNotSpam config: keyword='{search_text}', days={days_back} ({start_date} to {end_date})"
        logger.info(msg)
    
    elif automation == "import_contacts":
        vcf_path = os.path.join(DATA_DIR, "export.vcf")
        if not os.path.exists(vcf_path):
            logger.error(f"VCF file not found at: {vcf_path}")
            print(f"\nError: VCF file not found at: {vcf_path}")
            return

        automation_kwargs = {"vcf_file": vcf_path}
        logger.info(f"ImportContacts config: vcf_file='{vcf_path}'")

    elif automation == "open_profile":
        duration_str = input("Enter duration in minutes (default 10): ").strip()
        try:
            duration = int(duration_str) if duration_str else 10
        except ValueError:
            logger.warning(f"Invalid duration '{duration_str}', defaulting to 10")
            duration = 10
        automation_kwargs = {"duration": duration}
        logger.info(f"OpenProfile config: duration={duration} minutes")

    # Prompt for desktop/mobile percentage
    desktop_pct_str = input("Enter desktop percentage (0-100, default 100): ").strip()
    try:
        desktop_pct = int(desktop_pct_str) if desktop_pct_str else 100
        desktop_pct = max(0, min(100, desktop_pct))  # Clamp to 0-100
    except ValueError:
        logger.warning(f"Invalid percentage '{desktop_pct_str}', defaulting to 100")
        desktop_pct = 100
    logger.info(f"Desktop/Mobile split: {desktop_pct}% desktop, {100-desktop_pct}% mobile")

    # Create run output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_output_dir = os.path.join(OUTPUT_DIR, f"automation_run_{timestamp}")
    accounts_dir = os.path.join(run_output_dir, "accounts")
    os.makedirs(accounts_dir, exist_ok=True)
    logger.info(f"Run output directory: {run_output_dir}")

    # Multiprocessing Setup
    manager = multiprocessing.Manager()
    lock = manager.Lock()
    status_counts, _ = AutomationMetadata.create_shared_state(manager)
    
    metadata = AutomationMetadata(
        automation_name=f"{provider}_{automation}",
        total_accounts=len(accounts),
        status_counts=status_counts,
        lock=lock,
        output_dir=run_output_dir
    )
    
    print(f"Starting execution (multithreaded - {args.workers} workers)...")
    
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=args.workers,
        initializer=init_worker,
        initargs=(lock, status_counts, run_output_dir)
    ) as executor:
        futures = []
        for i, account_data in enumerate(accounts):
            # Round-robin proxy distribution
            proxy = proxies[i % len(proxies)] if proxies else None
            
            # Randomly assign desktop or mobile based on percentage
            account_type = "desktop" if random.randint(1, 100) <= desktop_pct else "mobile"
            
            futures.append(executor.submit(
                process_account_worker,
                account_data=account_data,
                proxy=proxy,
                provider=provider,
                automation_name=automation,
                account_type=account_type,
                index=i+1,
                **automation_kwargs
            ))
        
        # Wait for all futures to complete
        concurrent.futures.wait(futures)
        
    # Finalize metadata and write report
    metadata_file = metadata.finalize()
    print(f"\nAll accounts processed. Report saved to: {metadata_file}")

if __name__ == "__main__":
    multiprocessing.freeze_support() # For Windows support
    python_path = r"C:\Python314\python.exe"
    if os.path.exists(python_path):
        multiprocessing.set_executable(python_path)
    main()

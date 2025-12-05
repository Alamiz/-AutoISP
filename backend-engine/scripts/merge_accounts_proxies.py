"""
Account & Proxy Merger Script
Merges accounts (email:password) with proxies (ip:port:username:password)
Distributes proxies equally across all accounts.
"""
import argparse
from pathlib import Path


def load_lines(file_path: str) -> list[str]:
    """Load non-empty lines from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def merge_accounts_with_proxies(accounts: list[str], proxies: list[str]) -> list[str]:
    """
    Merge accounts with proxies, distributing proxies equally.
    Each account gets one proxy, cycling through proxies if more accounts than proxies.
    """
    if not proxies:
        raise ValueError("No proxies provided")
    
    merged = []
    for i, account in enumerate(accounts):
        # Cycle through proxies
        proxy = proxies[i % len(proxies)]
        merged.append(f"{account}:{proxy}")
    
    return merged


def main():
    parser = argparse.ArgumentParser(description='Merge accounts with proxies')
    parser.add_argument('--accounts', '-a', required=True, help='Path to accounts file (email:password)')
    parser.add_argument('--proxies', '-p', required=True, help='Path to proxies file (ip:port:user:pass)')
    parser.add_argument('--output', '-o', default='merged_accounts.txt', help='Output file path')
    
    args = parser.parse_args()
    
    # Load data
    print(f"Loading accounts from: {args.accounts}")
    accounts = load_lines(args.accounts)
    print(f"  Found {len(accounts)} accounts")
    
    print(f"Loading proxies from: {args.proxies}")
    proxies = load_lines(args.proxies)
    print(f"  Found {len(proxies)} proxies")
    
    # Calculate distribution
    if len(proxies) > 0:
        accounts_per_proxy = len(accounts) / len(proxies)
        print(f"\nDistribution: ~{accounts_per_proxy:.1f} accounts per proxy")
    
    # Merge
    merged = merge_accounts_with_proxies(accounts, proxies)
    
    # Write output
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in merged:
            f.write(line + '\n')
    
    print(f"\n✓ Merged {len(merged)} accounts with proxies")
    print(f"✓ Output saved to: {output_path.absolute()}")


if __name__ == '__main__':
    main()

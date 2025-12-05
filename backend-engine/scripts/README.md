# Scripts

Utility scripts for AutoISP automation.

---

## merge_accounts_proxies.py

Merges account credentials with proxy configurations, distributing proxies equally across all accounts.

### Input Formats

**accounts.txt** - One account per line:
```
email:password
```

**proxies.txt** - One proxy per line:
```
ip:port:username:password
```

### Output Format

```
email:password:ip:port:username:password
```

### Usage

```bash
python scripts/merge_accounts_proxies.py -a <accounts_file> -p <proxies_file> -o <output_file>
```

### Arguments

| Argument | Short | Required | Description |
|----------|-------|----------|-------------|
| `--accounts` | `-a` | Yes | Path to accounts file |
| `--proxies` | `-p` | Yes | Path to proxies file |
| `--output` | `-o` | No | Output file (default: `merged_accounts.txt`) |

### Example

```bash
python scripts/merge_accounts_proxies.py -a scripts/accounts.txt -p scripts/proxies.txt -o output.txt
```

**accounts.txt:**
```
user1@gmx.de:pass123
user2@gmx.de:pass456
user3@gmx.de:pass789
```

**proxies.txt:**
```
192.168.1.1:8080:proxyuser:proxypass
192.168.1.2:8080:proxyuser:proxypass
```

**output.txt:**
```
user1@gmx.de:pass123:192.168.1.1:8080:proxyuser:proxypass
user2@gmx.de:pass456:192.168.1.2:8080:proxyuser:proxypass
user3@gmx.de:pass789:192.168.1.1:8080:proxyuser:proxypass
```

> **Note:** If there are more accounts than proxies, proxies are cycled/reused.

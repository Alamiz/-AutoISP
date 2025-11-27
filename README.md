# -AutoISP

## **1. Overview**

This repository contains the first functional prototype of a **multi-ISP browser automation engine** designed to run on a dedicated client machine. The system executes deterministic authentication flows for different email providers (currently GMX) using Playwright, with support for:

* Desktop vs Mobile automation separation
* Device-specific flows and selector signatures
* A loader mechanism to dynamically select the correct automation path
* Dynamic selector parsing (stored locally for now; API-managed in future phases)
* A standardized runner capable of invoking ISP automations through a unified interface
* A humanized action layer: delays, retries, required action semantics
* A state-based flow engine capable of identifying pages and executing handlers in sequence

This prototype is the foundation for a future **fully dynamic, remotely configurable automation platform**.

---

## **2. Repository Structure**

```
automations/
  ├── gmx/
  │   ├── loader.py                # Selects desktop/mobile automation class
  │   ├── desktop/
  │   │   ├── run.py               # Desktop runner + state machine
  │   │   ├── flows.py             # Desktop flow handlers
  │   │   ├── pages.py             # Desktop page signatures
  │   │   └── signatures.py        # Desktop selectors
  │   └── mobile/
  │       ├── run.py               # Mobile runner + state machine
  │       ├── flows.py             # Mobile flows
  │       ├── pages.py             # Mobile page signatures
  │       └── signatures.py        # Mobile selectors
core/
  ├── browser/                     # Playwright factory + user-agent system
  ├── humanization/                # Human behavior decorator
  ├── utils/                       # Retry, identification, helpers
runner.py                           # Global automation runner (before loader)
```

---

## **3. Core Concepts Implemented**

### **3.1 State Machine Architecture**

Each device type (desktop/mobile) has its own:

* Flow handler class
* Page signature map
* Selector signature file
* `FLOW_MAP` describing which handler corresponds to which page state

The automation runs as:

1. Load browser environment
2. Detect page (`identify_page`)
3. Lookup handler method for that page
4. Execute actions the handler produces
5. Repeat until reaching a goal state

---

## **4. Loader Mechanism**

Each ISP now includes a `loader.py` that:

* Receives `(email, password, proxy_config, device_type)`
* Chooses the correct automation class (`DesktopGMXAuthentication` or `MobileGMXAuthentication`)
* Returns a unified class instance for execution

This eliminates device branching inside `runner.py` and keeps the runner simple.

---

## **5. Runner for Executing Automations**

The global runner (`runner.py`) dynamically loads:

```
automations/{isp}/{automation_name}/loader.py
```

It then calls:

```
automation = Loader.load(email, password, proxy_config, device_type)
result = automation.execute()
```

This ensures:

* Consistent entrypoint for all ISPs
* Clean extensibility
* Prepared for API-based automation loading

---

## **6. Humanization & Error Handling Already Implemented**

* Retry decorator with required/optional failure semantics
* Human behavior delays between actions
* Detailed structured logging
* Browser profile isolation per account
* Proxy support and masked logging

---

## **7. What This MVP Can Do Today**

* Log into GMX using desktop and mobile flows
* Handle multiple popup states
* Execute flows via a deterministic state machine
* Switch device type dynamically
* Extend easily to new ISPs
* Support flexible selector overrides
* Provide stable backbone for loading flows from an external API later

---

## **1. Objective**

The final goal is to build a **cloud-managed, no-code browser automation framework** where:

* Administrators define automations through a web UI
* Selectors, flows, and cases are stored in a central API
* The client machine only executes commands
* Users can create new automations (e.g., “Change GMX Password”)
* Custom logic and advanced branches are supported
* Even non-technical users can update selectors or steps

---

## **2. High-Level Roadmap**

### **PHASE 1 — MVP (Completed)**

* Desktop/mobile structured automations
* Loader system
* Local flows, selectors, pages
* Basic state machine
* Retry and humanization layers
* Working runner and entrypoint patterns

### **PHASE 2 — API-Driven Automations (Next Stage)**

Target: client executes flows **loaded dynamically from Master API**.

Features:

* Automations stored in Postgres as JSONB
* Selectors stored in DB with versions and history
* Client pulls latest automation definition
* Client resolves selectors before execution
* Basic JSON DSL to define cases, actions, transitions
* Execution logs streamed back to API

Deliverables:

* Automation registry in Master API
* Selector registry (by ISP, device, page, element)
* Versioning: published, draft, archived
* Client executor for remote flows

### **PHASE 3 — No-Code Automation Builder UI**

Users will be able to:

* Create new automations from scratch
* Add cases (page states)
* Add actions: click, fill, wait, assert, iframe, evaluate, conditional
* Drag-drop sequencing
* Link automations (e.g.: authenticate → change_password)
* Retry rules and required rules via UI
* Page matching logic (selector-based signatures)

### **PHASE 4 — High Flexibility Engine**

Introduce a **rule engine** and **conditional branching**:

* if element exists → go to case X
* if inbox page AND popup exists → close popup
* loop actions (e.g. process emails until empty list)
* dynamic data: lists, iteration, counters

### **PHASE 5 — Custom Code Blocks (Controlled)**

Support embedded Python/JS snippets (sandboxed):

* Custom email processing logic
* Conditional rules
* Loops and advanced control structures
* Data extraction and transformation

This expands the system to allow operations like:

“From the inbox, read all unread senders and send 50% to spam.”

### **PHASE 6 — Marketplace & Shared Automations**

* Users share automations with each other
* Extend to multiple ISPs, social platforms, websites
* Template-based automations

---

## **3. Target JSON DSL (Final Form)**

The final automation format will support:

* Cases (states)
* Match rules
* Actions with parameters
* Branching
* Loops
* Calling other automations
* Dynamic data

Example:

```json
{
  "id": "change_password",
  "requires": ["gmx_authenticate"],
  "cases": {
    "inbox": {
      "match": { "selector": "inbox_marker" },
      "actions": [
        { "type": "click", "target": "settings_button" },
        { "type": "wait_for", "target": "settings_page", "timeout": 5000 }
      ],
      "next": "settings"
    },
    "settings": {
      "actions": [
        { "type": "click", "target": "password_tab" },
        { "type": "fill", "target": "current_password", "value": "{{account.password}}" },
        { "type": "fill", "target": "new_password", "value": "{{data.new_password}}" },
        { "type": "click", "target": "save_button" }
      ],
      "goal": true
    }
  }
}
```

---

## **4. Master API Responsibilities (Future)**

* Manage accounts
* Manage automations & versions
* Manage selectors with history
* Permissions & user roles
* Execution history
* Logs & observability
* Deployment of updates to clients

---

## **5. Client Responsibilities (Future)**

* Poll for tasks
* Load automation JSON
* Load selectors
* Execute via interpreter
* Emit logs, screenshots, step results
* Maintain local profiles, browser instances, and proxy handling
* Support sandboxed custom code

---

## **6. UX Philosophy**

Even non-technical users must be able to:

* Fix broken selectors
* Add/modify steps
* Reorder flows
* Create new automations
* Reuse authentication flows
* Combine flows into end-to-end processes

Advanced users should optionally:

* Write custom logic
* Add mini-scripts
* Build conditional workflows

Everything should be deeply versioned and reproducible.

---
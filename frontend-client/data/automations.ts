import { Automation } from "@/lib/types";

export const automations: Automation[] = [
    // GMX Automations
    {
        id: "authenticate",
        name: "Authenticate",
        description: "Login to GMX account and verify session.",
        category: "Auth",
        provider: "gmx",
        estimatedDuration: "30s",
    },
    {
        id: "report_not_spam",
        name: "Report Not Spam",
        description: "Find emails by keyword in Spam folder and move them to Inbox.",
        category: "Email",
        provider: "gmx",
        estimatedDuration: "2m",
        params: [
            {
                name: "keyword",
                label: "Search Keyword",
                type: "text",
                placeholder: "e.g. 'Welcome'",
                required: true,
            },
            {
                name: "start_date",
                label: "Start Date",
                type: "date",
                required: true,
            },
            {
                name: "end_date",
                label: "End Date",
                type: "date",
                required: true,
            },
        ],
    },
    {
        id: "import_contacts",
        name: "Import Contacts",
        description: "Import contacts from a .vcf file into the address book.",
        category: "Maintenance",
        provider: "gmx",
        estimatedDuration: "1m",
        params: [
            {
                name: "vcf_file",
                label: "Contacts File (.vcf)",
                type: "file",
                accept: ".vcf",
                required: true,
            },
        ],
    },
    {
        id: "open_profile",
        name: "Open Profile",
        description: "Open the browser with the user profile for manual interaction.",
        category: "Test",
        provider: "gmx",
        estimatedDuration: "10m",
        params: [
            {
                name: "duration",
                label: "Duration (in minutes)",
                type: "number",
                placeholder: "e.g. '10'",
                required: true,
            },
        ],
    },

    // Web.de Automations
    {
        id: "authenticate",
        name: "Authenticate",
        description: "Login to Web.de account and verify session.",
        category: "Auth",
        provider: "webde",
        estimatedDuration: "30s",
    },
    {
        id: "report_not_spam",
        name: "Report Not Spam",
        description: "Find emails by keyword in Spam folder and move them to Inbox.",
        category: "Email",
        provider: "webde",
        estimatedDuration: "2m",
        params: [
            {
                name: "keyword",
                label: "Search Keyword",
                type: "text",
                placeholder: "e.g. 'Welcome'",
                required: true,
            },
            {
                name: "start_date",
                label: "Start Date",
                type: "date",
                required: true,
            },
            {
                name: "end_date",
                label: "End Date",
                type: "date",
                required: true,
            },
        ],
    },
    {
        id: "import_contacts",
        name: "Import Contacts",
        description: "Import contacts from a .vcf file into the address book.",
        category: "Maintenance",
        provider: "webde",
        estimatedDuration: "1m",
        params: [
            {
                name: "vcf_file",
                label: "Contacts File (.vcf)",
                type: "file",
                accept: ".vcf",
                required: true,
            },
        ],
    },
    {
        id: "open_profile",
        name: "Open Profile",
        description: "Open the browser with the user profile for manual interaction.",
        category: "Test",
        provider: "webde",
        estimatedDuration: "10m",
        params: [
            {
                name: "duration",
                label: "Duration (in minutes)",
                type: "number",
                placeholder: "e.g. '10'",
                required: true,
            },
        ],
    },
];
import { Automation } from "@/lib/types";

export const gmxAutomations: Automation[] = [
    {
        id: "authenticate",
        name: "Authenticate",
        description: "Authenticate to GMX",
        category: "browsing",
        estimatedDuration: "1-2 minutes",
    },
    {
        id: "open_profile",
        name: "Open profile",
        description: "Open profile for a specefic duration for test purposes.",
        category: "test",
        estimatedDuration: "unkown",
        parameters: {
            duration: { type: "number", label: "Duration (seconds)", required: true },
        },
    }
]

export const webdeAutomations: Automation[] = [
    {
        id: "authenticate",
        name: "Authenticate",
        description: "Authenticate to web.de",
        category: "browsing",
        estimatedDuration: "1-2 minutes",
    },
    {
        id: "open_profile",
        name: "Open profile",
        description: "Open profile for a specefic duration for test purposes.",
        category: "test",
        estimatedDuration: "unkown",
        parameters: {
            duration: { type: "number", label: "Duration (seconds)", required: true },
        },
    }
]
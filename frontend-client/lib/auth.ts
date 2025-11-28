import { apiPost, apiGet } from "./api";

const TOKEN_KEY = "auth_tokens";

interface AuthTokens {
    access: string;
    refresh: string;
}

export const auth = {
    async login(username: string, password: string): Promise<void> {
        const tokens = await apiPost<AuthTokens, { username: string; password: string }>(
            "/api/token/",
            { username, password },
            "master"
        );
        localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
        // Also set cookie for middleware
        document.cookie = `auth_tokens=${JSON.stringify(tokens)}; path=/; max-age=${60 * 60 * 24 * 7}`;
    },

    logout() {
        localStorage.removeItem(TOKEN_KEY);
        // Clear cookie
        document.cookie = 'auth_tokens=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
        window.location.href = "/login";
    },

    getAccessToken(): string | null {
        const tokensStr = localStorage.getItem(TOKEN_KEY);
        if (!tokensStr) return null;
        try {
            const tokens = JSON.parse(tokensStr) as AuthTokens;
            return tokens.access;
        } catch {
            return null;
        }
    },

    isAuthenticated(): boolean {
        return !!this.getAccessToken();
    }
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface OrganizationSummary {
    ein: string;
    name: string;
    city: string | null;
    state: string | null;
    ntee_category: string | null;
}

export interface SearchResponse {
    query: string;
    total_results: number;
    results: OrganizationSummary[];
}

export interface FilingYear {
    tax_year: number;
    total_revenue: number | null;
    total_expenses: number | null;
    total_assets: number | null;
    total_liabilities: number | null;
    contributions: number | null;
    program_revenue: number | null;
}

export interface OrganizationProfile {
    ein: string;
    name: string;
    city: string | null;
    state: string | null;
    ntee_category: string | null;
    filings: FilingYear[];
}

async function get<T>(path: string): Promise<T> {
    const resp = await fetch(`${API_URL}${path}`);
    if (!resp.ok) throw new Error(`API error ${resp.status} on ${path}`);
    return resp.json();
}

export function searchOrganizations(q: string) {
    return get<SearchResponse>(`/search?q=${encodeURIComponent(q)}`);
}

export function getOrganization(ein: string) {
    return get<OrganizationProfile>(`/organizations/${ein}`);
}
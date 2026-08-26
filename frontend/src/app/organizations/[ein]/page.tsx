"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import {
    CartesianGrid,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import { getOrganization } from "@/lib/api";

const fmtMoney = (n: number | null | undefined) =>
    n == null
        ? "—"
        : new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            notation: "compact",
            maximumFractionDigits: 1,
        }).format(n);

function Organization() {
    const { ein } = useParams<{ ein: string }>();
    const q = useSearchParams().get("q");

    const { data: org, isPending, error } = useQuery({
        queryKey: ["organization", ein],
        queryFn: () => getOrganization(ein),
    });

    if (isPending) return <p className="p-12 text-gray-500">Loading…</p>;
    if (error || !org)
        return <p className="p-12 text-red-600">Organization not found.</p>;

    const latest = org.filings.at(-1);
    const prior = org.filings.at(-2);
    const yoy =
        latest?.total_revenue && prior?.total_revenue
            ? ((latest.total_revenue - prior.total_revenue) /
                prior.total_revenue) *
            100
            : null;

    return (
        <main className="mx-auto max-w-4xl px-4 py-12">
            <Link
                href={q ? `/?q=${encodeURIComponent(q)}` : "/"}
                className="text-sm text-gray-500 hover:underline"
            >
                ← Search
            </Link>
            <h1 className="mt-2 text-3xl font-bold">{org.name}</h1>
            <p className="text-gray-500">
                {[org.city, org.state].filter(Boolean).join(", ")}
                {org.ntee_category ? ` • ${org.ntee_category}` : ""} • EIN {org.ein}
            </p>

            <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
                <Stat label="Latest revenue" value={fmtMoney(latest?.total_revenue)} />
                <Stat label="Latest expenses" value={fmtMoney(latest?.total_expenses)} />
                <Stat label="Total assets" value={fmtMoney(latest?.total_assets)} />
                <Stat
                    label="Revenue YoY"
                    value={yoy == null ? "—" : `${yoy > 0 ? "+" : ""}${yoy.toFixed(1)}%`}
                />
            </div>

            {org.filings.length > 1 ? (
                <section className="mt-10">
                    <h2 className="text-xl font-semibold">Revenue & Expenses</h2>
                    <div className="mt-4 h-80">
                        <ResponsiveContainer>
                            <LineChart data={org.filings}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="tax_year" />
                                <YAxis tickFormatter={(v) => fmtMoney(v)} width={80} />
                                <Tooltip
                                    formatter={(v) => fmtMoney(Number(v))}
                                    contentStyle={{
                                        backgroundColor: "#ffffff",
                                        border: "1px solid #e5e7eb",
                                        borderRadius: "8px",
                                    }}
                                    labelStyle={{ color: "#111827", fontWeight: 600 }}
                                />
                                <Line
                                    dataKey="total_revenue"
                                    name="Revenue"
                                    stroke="#2563eb"
                                    strokeWidth={2}
                                    dot
                                />
                                <Line
                                    dataKey="total_expenses"
                                    name="Expenses"
                                    stroke="#dc2626"
                                    strokeWidth={2}
                                    dot
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </section>
            ) : (
                <p className="mt-10 text-gray-500">
                    Not enough digitized filings to chart history for this organization.
                </p>
            )}
        </main>
    );
}

function Stat({ label, value }: { label: string; value: string }) {
    return (
        <div className="rounded-lg border border-gray-200 p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">{label}</p>
            <p className="mt-1 text-lg font-semibold">{value}</p>
        </div>
    );
}

export default function OrganizationPage() {
    return (
        <Suspense>
            <Organization />
        </Suspense>
    );
}
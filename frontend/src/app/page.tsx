"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { searchOrganizations } from "@/lib/api";

function Search() {
  const router = useRouter();
  const query = useSearchParams().get("q") ?? "";
  const [input, setInput] = useState(query);

  const submit = () => {
    const q = input.trim();
    router.replace(q ? `/?q=${encodeURIComponent(q)}` : "/");
  };

  const { data, isFetching, error } = useQuery({
    queryKey: ["search", query],
    queryFn: () => searchOrganizations(query),
    enabled: query.length >= 2,
  });

  return (
    <main className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="text-3xl font-bold">Nonprofit Intelligence</h1>
      <p className="mt-1 text-gray-500">
        Search U.S. nonprofits and explore their financial history.
      </p>

      <div className="mt-6 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="Try “Sierra Club” or “food bank”"
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2"
        />
        <button
          onClick={submit}
          className="rounded-lg bg-gray-900 px-5 py-2 font-medium text-white"
        >
          Search
        </button>
      </div>

      {isFetching && <p className="mt-6 text-gray-500">Searching…</p>}
      {error && (
        <p className="mt-6 text-red-600">
          Search failed — is the backend running?
        </p>
      )}

      {data && (
        <div className="mt-6">
          <p className="text-sm text-gray-500">
            {data.total_results} results for “{data.query}”
          </p>
          <ul className="mt-2 divide-y divide-gray-200">
            {data.results.map((org) => (
              <li key={org.ein}>
                <Link
                  href={`/organizations/${org.ein}?q=${encodeURIComponent(query)}`}
                  className="block py-3 hover:bg-gray-50"
                >
                  <span className="font-medium">{org.name}</span>
                  <span className="ml-2 text-sm text-gray-500">
                    {[org.city, org.state].filter(Boolean).join(", ")}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </main>
  );
}

export default function SearchPage() {
  return (
    <Suspense>
      <Search />
    </Suspense>
  );
}
'use client';

import { FormEvent, useState } from "react";

type Lead = {
  id: string;
  name: string;
  category: string;
  country: string;
  headquarters_city: string;
  fit_score: string;
  justification: string;
  rank: number;
};

type JobStatus = {
  job_id: string;
  status: string;
  created_at: string;
  finished_at: string | null;
};

export default function Home() {
  const [businessDescription, setBusinessDescription] = useState<string>('');
  const [targetMarket, setTargetMarket] = useState<string>('ZM');
  const [buyerTypes, setBuyerTypes] = useState<string[]>(['distributor', 'supermarket', 'horeca']);
  const [maxResults, setMaxResults] = useState<number>(10);

  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const API_URL = 'http://localhost:8000/api';

  const pollJobStatus = async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_URL}/discovery/${id}`);
        const data: JobStatus = await res.json();

        setStatus(data);

        if (data.status === 'done') {
          clearInterval(interval);

          const leadsRes = await fetch(`${API_URL}/discovery/${id}/leads`);
          const leadsData = await leadsRes.json();

          setLeads(leadsData.leads);
          setLoading(false);
        }
      } catch (error) {
        console.error(error);
      }
    }, 1500);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setLeads([]);

    try {
      const res = await fetch(`${API_URL}/discovery`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          business_description: businessDescription,
          target_market: targetMarket,
          buyer_types: buyerTypes,
          max_results: maxResults,
        }),
      });

      if (!res.ok) throw new Error('Failed to start discovery: ' + res.statusText);

      const data: JobStatus = await res.json();
      setJobId(data.job_id);
      setStatus(data);

      pollJobStatus(data.job_id);
    } catch (err: any) {
      setError(err.message || 'Something went wrong');
      setLoading(false);
      setJobId(null);
      setStatus(null);
    }
  };

  const buyerOptions = [
    'distributor', 'supermarket', 'horeca', 'wholesaler',
    'online_retailer', 'food_processor', 'convenience_chain', 'logistics'
  ];

  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-3xl mx-auto space-y-8">

        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Luso8 Lead Discovery</h1>
          <p className="text-slate-500">Identify and qualify buyers across target African markets.</p>
        </div>

        {error && (
          <div className="rounded-md border border-red-200 bg-red-50 p-4">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
          </div>
        )}

        {!loading && leads.length === 0 && (
          <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <form onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-8">
              <div className="space-y-2">
                <label htmlFor="business-description" className="text-sm font-medium leading-none text-slate-900">
                  Business Description
                </label>
                <textarea
                  id="business-description"
                  value={businessDescription}
                  onChange={(e) => setBusinessDescription(e.target.value)}
                  placeholder="e.g., We produce packaged groundnut snacks for retail..."
                  className="flex min-h-[120px] w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  required
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label htmlFor="target-market" className="text-sm font-medium leading-none text-slate-900">Target Market</label>
                  <select
                    id="target-market"
                    value={targetMarket}
                    onChange={(e) => setTargetMarket(e.target.value)}
                    className="flex h-10 w-full items-center justify-between rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="ZM">Zambia (ZM)</option>
                    <option value="KE">Kenya (KE)</option>
                    <option value="TZ">Tanzania (TZ)</option>
                    <option value="NG">Nigeria (NG)</option>
                    <option value="ZA">South South Africa (ZA)</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label htmlFor="max-results" className="text-sm font-medium leading-none text-slate-900">Max Results</label>
                  <input
                    id="max-results"
                    type="number"
                    value={maxResults}
                    onChange={(e) => setMaxResults(Number(e.target.value))}
                    min="1"
                    max="50"
                    className="flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  />
                </div>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-medium leading-none text-slate-900">Buyer Types</label>
                <div className="flex flex-wrap gap-2">
                  {buyerOptions.map((type) => {
                    const isSelected = buyerTypes.includes(type);
                    return (
                      <button
                        key={type}
                        type="button"
                        onClick={() => {
                          setBuyerTypes((prev) =>
                            isSelected ? prev.filter((t) => t !== type) : [...prev, type]
                          );
                        }}
                        className={`inline-flex items-center rounded-md border px-3 py-1.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-slate-900 focus:ring-offset-2 ${
                          isSelected
                            ? 'border-transparent bg-slate-900 text-slate-50 hover:bg-slate-900/90 shadow-sm'
                            : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'
                        }`}
                      >
                        {type.replace('_', ' ')}
                      </button>
                    );
                  })}
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="inline-flex w-full items-center justify-center rounded-md bg-slate-900 px-8 py-3 text-sm font-medium text-slate-50 shadow transition-colors hover:bg-slate-900/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
              >
                Discover Leads
              </button>
            </form>
          </div>
        )}

        {loading && leads.length === 0 && (
          <div className="rounded-xl border border-slate-200 bg-white p-12 shadow-sm text-center">
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900 mb-6" />
            <h2 className="text-lg font-semibold tracking-tight text-slate-900">Mining Data</h2>
            <div className="mt-2 flex items-center justify-center gap-2 text-sm text-slate-500">
              <span>Status:</span>
              <span className="inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-900 capitalize">
                {status?.status || 'connecting...'}
              </span>
            </div>
            {jobId && <p className="mt-6 text-xs text-slate-400 font-mono">ID: {jobId}</p>}
          </div>
        )}

        {leads.length > 0 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold tracking-tight text-slate-900">
                Qualified Leads ({leads.length})
              </h2>
              <button
                onClick={() => {
                  setJobId(null);
                  setLeads([]);
                  setStatus(null);
                  setLoading(false);
                }}
                className="text-sm font-medium text-slate-600 hover:text-slate-900 underline underline-offset-4"
              >
                Start New Search
              </button>
            </div>

            <div className="grid gap-4">
              {leads.map((lead) => {
                const score = Number(lead.fit_score) * 100;
                return (
                  <div
                    key={lead.id}
                    className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition-all hover:shadow-md"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-900">
                            {lead.rank}
                          </span>
                          <h3 className="font-semibold text-slate-900 text-lg leading-none">
                            {lead.name}
                          </h3>
                        </div>
                        <p className="text-sm text-slate-500 pl-8">
                          {lead.category} • {lead.headquarters_city}, {lead.country}
                        </p>
                      </div>

                      <div className="flex flex-col sm:items-end pl-8 sm:pl-0">
                        <div className="flex items-baseline gap-1">
                          <span className={`text-2xl font-bold tracking-tight ${score >= 80 ? 'text-slate-900' : 'text-slate-700'}`}>
                            {score.toFixed(0)}%
                          </span>
                        </div>
                        <span className="text-[10px] font-medium uppercase tracking-wider text-slate-500">
                          Fit Score
                        </span>
                      </div>
                    </div>

                    <div className="mt-4 ml-0 sm:ml-8 rounded-md bg-slate-50 p-4 border border-slate-100">
                      <p className="text-sm leading-relaxed text-slate-700">
                        {lead.justification}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
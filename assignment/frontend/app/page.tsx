'use client';

import {FormEvent, useState} from "react";


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
}

export default function Home(){
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

  const pollJobStatus = async (id: string)=> {
    const interval = setInterval(async () => {
      try{
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
      }catch(error){
        console.error(error);
      }
    }, 1500); // poll every 1.5 seconds
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setLeads([])

    try{
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

      if(!res.ok) throw new Error('Failed to start discovery' + res.statusText);

      const data: JobStatus = await res.json();
      setJobId(data.job_id);
      setStatus(data);

      // start polling
      pollJobStatus(data.job_id);
    }
    catch(error: any){
      setError(error.message || 'Something went wrong');
      setLoading(false);
    }
  }

  const buyerOptions = [
    'distributor', 'supermarket', 'horeca', 'wholesaler',
    'online_retailer', 'food_processor', 'convenience_chain', 'logistics'
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-900">Luso8 Lead Discovery</h1>
          <p className="text-gray-600 mt-2">Find qualified buyers across Africa</p>
        </div>

        {/* Form State */}
        {!jobId && (
          <form onSubmit={handleSubmit} className="bg-white shadow-xl rounded-2xl p-8">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business Description
                </label>
                <textarea
                  value={businessDescription}
                  onChange={(e) => setBusinessDescription(e.target.value)}
                  placeholder="We produce packaged groundnut snacks for retail."
                  className="w-full h-32 px-4 py-3 border border-gray-400 text-gray-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Target Market</label>
                  <select
                    value={targetMarket}
                    onChange={(e) => setTargetMarket(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 text-gray-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="ZM">Zambia (ZM)</option>
                    <option value="KE">Kenya (KE)</option>
                    <option value="TZ">Tanzania (TZ)</option>
                    <option value="NG">Nigeria (NG)</option>
                    <option value="ZA">South Africa (ZA)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Results</label>
                  <input
                    type="number"
                    value={maxResults}
                    onChange={(e) => setMaxResults(Number(e.target.value))}
                    min="1"
                    max="50"
                    className="w-full px-4 py-3 border border-gray-300 text-gray-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Buyer Types</label>
                <div className="flex flex-wrap gap-2">
                  {buyerOptions.map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => {
                        setBuyerTypes((prev) =>
                          prev.includes(type)
                            ? prev.filter((t) => t !== type)
                            : [...prev, type]
                        );
                      }}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                        buyerTypes.includes(type)
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-4 rounded-2xl transition-colors text-lg"
              >
                {loading ? 'Starting Discovery...' : 'Find Leads'}
              </button>
            </div>
          </form>
        )}

        {/* Pending State */}
        {jobId && status?.status !== 'done' && (
          <div className="bg-white shadow-xl rounded-2xl p-12 text-center">
            <div className="animate-spin w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-6"></div>
            <h2 className="text-2xl font-semibold text-gray-800">Finding qualified leads...</h2>
            <p className="text-gray-500 mt-3">This usually takes 20–40 seconds</p>
            <p className="text-xs text-gray-400 mt-8">Job ID: {jobId}</p>
          </div>
        )}

        {/* Results State */}
        {leads.length > 0 && (
          <div className="bg-white shadow-xl rounded-2xl p-8">
            <h2 className="text-2xl text-gray-600 font-bold mb-6 flex items-center gap-3">
              <span>Your Qualified Leads ({leads.length})</span>
            </h2>

            <div className="space-y-6">
              {leads.map((lead) => (
                <div
                  key={lead.id}
                  className="border border-gray-200 rounded-2xl p-6 hover:border-blue-200 transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-xl text-gray-900">{lead.name}</h3>
                      <p className="text-gray-600">
                        {lead.category} • {lead.country} • {lead.headquarters_city}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-bold text-emerald-600">
                        {(Number(lead.fit_score) * 100).toFixed(0)}%
                      </div>
                      <div className="text-xs text-gray-500">FIT SCORE</div>
                    </div>
                  </div>

                  <div className="mt-5 bg-orange-600 border border-amber-100 rounded-xl p-5 text-sm leading-relaxed">
                    {lead.justification}
                  </div>

                  <div className="text-xs text-gray-400 mt-4">Rank #{lead.rank}</div>
                </div>
              ))}
            </div>

            <button
              onClick={() => {
                setJobId(null);
                setLeads([]);
                setStatus(null);
                setBusinessDescription('');
              }}
              className="mt-10 w-full py-4 border text-gray-500 border-gray-50 rounded-2xl hover:bg-blue-500 font-medium"
            >
              Start New Search
            </button>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-6 rounded-2xl text-center">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}



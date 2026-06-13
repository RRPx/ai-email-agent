import { useState, useEffect } from "react";
import { API_URL } from "./utils/helper/api";
import axios from "axios";
import EmailCard from "./components/EmailCard";
import StatCard from "./components/StatCard";
import PulseDot from "./components/PulseDot";

export default function App() {
  const [emails, setEmails] = useState([]);
  const [newIds, setNewIds] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [running, setRunning] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [filter, setFilter] = useState("ALL");

  const fetchEmails = async (isManual = false) => {
    try {
      const res = await axios.get(
        `https://backend-email-agent-production.up.railway.app/emails`,
      );
      const fetched = res.data.emails;

      if (isManual) {
        setEmails((prev) => {
          const prevIds = new Set(prev.map((e) => e.email_id));
          const fresh = fetched.filter((e) => !prevIds.has(e.email_id));
          if (fresh.length > 0) {
            const freshIds = new Set(fresh.map((e) => e.email_id));
            setNewIds(freshIds);
            setTimeout(() => setNewIds(new Set()), 5000);
          }
          return fetched;
        });
      } else {
        setEmails(fetched);
      }

      setLastUpdated(new Date().toLocaleTimeString());
      setError(null);
    } catch {
      setError("Failed to connect to the backend.");
    } finally {
      setLoading(false);
    }
  };

  const runAgent = async () => {
    setRunning(true);
    try {
      await axios.post(`${API_URL}/run`);
      await fetchEmails(true);
    } catch {
      setError("Failed to run agent.");
    } finally {
      setRunning(false);
    }
  };

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      if (mounted) await fetchEmails();
    };
    load();
    const interval = setInterval(() => {
      if (mounted) fetchEmails(true);
    }, 30000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const filteredEmails =
    filter === "ALL" ? emails : emails.filter((e) => e.priority === filter);

  const high = emails.filter((e) => e.priority === "HIGH").length;
  const medium = emails.filter((e) => e.priority === "MEDIUM").length;
  const low = emails.filter((e) => e.priority === "LOW").length;

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-slate-200">
      {/* background glows */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-20 -right-20 w-80 h-80 bg-teal-600/8 rounded-full blur-3xl" />
      </div>

      {/* header */}
      <div className="relative z-10 border-b border-white/6 backdrop-blur-xl bg-white/3">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <div className="flex items-center">
              <PulseDot />
              <h1 className="text-lg font-semibold text-slate-100">
                AI Email Agent
              </h1>
            </div>
            <p className="text-xs text-slate-500 mt-0.5 ml-4">
              {lastUpdated ? `Last updated: ${lastUpdated}` : "Connecting..."}
            </p>
          </div>
          <button
            onClick={runAgent}
            disabled={running}
            className="flex items-center gap-2 bg-indigo-500/10 hover:bg-indigo-500/20 disabled:opacity-40 border border-indigo-500/20 hover:border-indigo-500/40 text-indigo-300 text-sm font-medium px-4 py-2 rounded-lg transition-all"
          >
            <span className={running ? "animate-spin" : ""}>⟳</span>
            {running ? "Running..." : "Run Agent"}
          </button>
        </div>
      </div>

      {/* main */}
      <div className="relative z-10 max-w-5xl mx-auto px-6 py-8">
        {loading ? (
          <div className="text-center py-32 text-slate-600">
            Loading emails...
          </div>
        ) : error ? (
          <div className="text-center py-32 text-red-400">{error}</div>
        ) : (
          <>
            {/* stats */}
            <div className="grid grid-cols-3 gap-4 mb-8">
              <StatCard
                label="High Priority"
                value={high}
                color="text-red-400"
              />
              <StatCard
                label="Medium Priority"
                value={medium}
                color="text-yellow-400"
              />
              <StatCard
                label="Low Priority"
                value={low}
                color="text-emerald-400"
              />
            </div>

            {/* filters */}
            <div className="flex items-center gap-2 mb-6">
              {["ALL", "HIGH", "MEDIUM", "LOW"].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`hover:cursor-pointer text-xs px-4 py-1.5 rounded-full font-medium transition-all ${
                    filter === f
                      ? "bg-indigo-500/20 border border-indigo-500/40 text-indigo-300"
                      : "bg-white/3 border border-white/6 text-slate-400 hover:bg-white/6"
                  }`}
                >
                  {f}
                </button>
              ))}
              <span className="ml-auto text-xs text-slate-600">
                {filteredEmails.length} notification
                {filteredEmails.length !== 1 ? "s" : ""}
              </span>
            </div>

            {/* cards */}
            {filteredEmails.length === 0 ? (
              <div className="text-center py-32 text-slate-600 text-sm">
                No important emails found.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredEmails.map((email) => (
                  <EmailCard
                    key={email.email_id}
                    email={email}
                    isNew={newIds.has(email.email_id)}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

import { useEffect, useState } from "react";
import {
  loadSession,
  searchHotels,
  type HotelResult,
  type ParsedQuery,
  type SearchFilters,
  type TourResult,
} from "./api/client";
import { Loading } from "./pages/Loading";
import { Results } from "./pages/Results";
import { Welcome } from "./pages/Welcome";
import { Detail } from "./pages/Detail";

type Screen = "welcome" | "loading" | "results" | "detail";

function getSessionFromUrl(): string | null {
  const params = new URLSearchParams(window.location.search);
  return params.get("session");
}

export default function App() {
  const [screen, setScreen] = useState<Screen>("welcome");
  const [query, setQuery] = useState(
    "Махачкала, 3 дня в ноябре, до 15 тысяч, у моря или тур по Дагестану",
  );
  const [hotels, setHotels] = useState<HotelResult[]>([]);
  const [tours, setTours] = useState<TourResult[]>([]);
  const [parsed, setParsed] = useState<ParsedQuery | null>(null);
  const [filters, setFilters] = useState<SearchFilters | null>(null);
  const [webInsight, setWebInsight] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function applySearchData(data: {
    parsed: ParsedQuery;
    filters: SearchFilters;
    hotels: HotelResult[];
    tours: TourResult[];
    web_insight: string | null;
  }) {
    setParsed(data.parsed);
    setFilters(data.filters);
    setHotels(data.hotels);
    setTours(data.tours);
    setWebInsight(data.web_insight);
  }

  useEffect(() => {
    const sessionId = getSessionFromUrl();
    if (!sessionId) return;
    setScreen("loading");
    loadSession(sessionId)
      .then((data) => {
        setQuery(data.query);
        applySearchData(data);
        setScreen("results");
      })
      .catch((e) => {
        setError(String(e.message || e));
        setScreen("welcome");
      });
  }, []);

  async function handleSearch() {
    setError(null);
    setScreen("loading");
    try {
      const data = await searchHotels(query.trim());
      applySearchData(data);
      setScreen("results");
    } catch (e) {
      setError(String((e as Error).message || e));
      setScreen("welcome");
    }
  }

  return (
    <div className="app-shell">
      {error && <div className="error">{error}</div>}
      {screen === "welcome" && (
        <Welcome query={query} onQueryChange={setQuery} onSubmit={handleSearch} />
      )}
      {screen === "loading" && <Loading />}
      {screen === "results" && parsed && filters && (
        <Results
          query={query}
          parsed={parsed}
          filters={filters}
          hotels={hotels}
          tours={tours}
          webInsight={webInsight}
          onSelect={(id) => {
            setSelectedId(id);
            setScreen("detail");
          }}
          onBack={() => setScreen("welcome")}
        />
      )}
      {screen === "detail" && selectedId && (
        <Detail hotelId={selectedId} onBack={() => setScreen("results")} />
      )}
    </div>
  );
}

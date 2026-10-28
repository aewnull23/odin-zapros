import { useEffect, useMemo, useState } from "react";
import type { HotelResult, ParsedQuery, SearchFilters, TourResult } from "../api/client";
import { Filters } from "../components/Filters";
import { HotelCard } from "../components/HotelCard";
import { TourCard } from "../components/TourCard";

interface Props {
  query: string;
  parsed: ParsedQuery;
  filters: SearchFilters;
  hotels: HotelResult[];
  tours: TourResult[];
  webInsight: string | null;
  onSelect: (id: string) => void;
  onBack: () => void;
}

export function Results({
  query,
  parsed,
  filters,
  hotels,
  tours,
  webInsight,
  onSelect,
  onBack,
}: Props) {
  const maxPrice = useMemo(() => Math.max(...hotels.map((h) => h.price_per_night), 5000), [hotels]);
  const [priceLimit, setPriceLimit] = useState(filters.max_price_per_night ?? maxPrice);
  const [minStars, setMinStars] = useState(filters.min_stars);
  const [maxDistance, setMaxDistance] = useState(filters.max_distance_km);
  const [tab, setTab] = useState<"hotels" | "tours">(
    filters.product_type === "tour" ? "tours" : "hotels",
  );

  useEffect(() => {
    setPriceLimit(filters.max_price_per_night ?? maxPrice);
    setMinStars(filters.min_stars);
    setMaxDistance(filters.max_distance_km);
  }, [filters, maxPrice]);

  const filteredHotels = hotels.filter(
    (h) =>
      h.price_per_night <= priceLimit &&
      h.stars >= minStars &&
      h.distance_to_center_km <= maxDistance,
  );

  const filteredTours = tours.filter((t) => {
    if (filters.max_total_price && t.price_total > filters.max_total_price) return false;
    return true;
  });

  return (
    <section>
      <button className="btn secondary" onClick={onBack} style={{ marginBottom: 12 }}>
        ← Новый запрос
      </button>
      <h1 className="hero-title">Подбор AI</h1>
      <p className="parsed-summary">
        «{query}»
        {parsed.location ? ` · ${parsed.location}` : ""}
        {parsed.budget_max ? ` · до ${parsed.budget_max.toLocaleString("ru-RU")} ₽` : ""}
      </p>
      <p className="parsed-summary">
        Фильтры от AI: тип {filters.product_type}, звёзды от {filters.min_stars}, сортировка{" "}
        {filters.sort_by}
        {filters.required_tags.length ? `, теги: ${filters.required_tags.join(", ")}` : ""}
      </p>
      {webInsight && <p className="ai-reason">{webInsight}</p>}

      <div className="filters-row" style={{ marginBottom: 12 }}>
        {(filters.product_type === "hotel" || filters.product_type === "both") && (
          <button className={`btn ${tab === "hotels" ? "" : "secondary"}`} onClick={() => setTab("hotels")}>
            Отели ({filteredHotels.length})
          </button>
        )}
        {(filters.product_type === "tour" || filters.product_type === "both") && (
          <button className={`btn ${tab === "tours" ? "" : "secondary"}`} onClick={() => setTab("tours")}>
            Туры ({filteredTours.length})
          </button>
        )}
      </div>

      {tab === "hotels" && (
        <>
          <Filters
            maxPrice={maxPrice}
            priceLimit={priceLimit}
            onPriceLimit={setPriceLimit}
            minStars={minStars}
            onMinStars={setMinStars}
            maxDistance={maxDistance}
            onMaxDistance={setMaxDistance}
          />
          <div className="hotel-list">
            {filteredHotels.length === 0 ? (
              <p>Нет отелей по фильтрам AI. Ослабьте условия ниже.</p>
            ) : (
              filteredHotels.map((h) => (
                <HotelCard key={h.id} hotel={h} onClick={() => onSelect(h.id)} />
              ))
            )}
          </div>
        </>
      )}

      {tab === "tours" && (
        <div className="hotel-list">
          {filteredTours.length === 0 ? (
            <p>Нет туров по заданным фильтрам.</p>
          ) : (
            filteredTours.map((t) => <TourCard key={t.id} tour={t} />)
          )}
        </div>
      )}
    </section>
  );
}

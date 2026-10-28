import type { TourResult } from "../api/client";

interface Props {
  tour: TourResult;
}

export function TourCard({ tour }: Props) {
  return (
    <article className="hotel-card">
      <img src={tour.photo_url} alt={tour.name} loading="lazy" />
      <div className="hotel-card-body">
        <h3>{tour.name}</h3>
        <div className="meta">
          <span className="chip">Тур</span>
          <span>{tour.duration_days} дн.</span>
          <span>{tour.rating} рейтинг</span>
          <span>{tour.price_total.toLocaleString("ru-RU")} ₽</span>
        </div>
        <p className="ai-reason">{tour.ai_reason}</p>
      </div>
    </article>
  );
}

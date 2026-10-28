import type { HotelResult } from "../api/client";

interface Props {
  hotel: HotelResult;
  onClick: () => void;
}

export function HotelCard({ hotel, onClick }: Props) {
  return (
    <article className="hotel-card" onClick={onClick}>
      <img src={hotel.photo_url} alt={hotel.name} loading="lazy" />
      <div className="hotel-card-body">
        <h3>{hotel.name}</h3>
        <div className="meta">
          <span>{"★".repeat(hotel.stars)}</span>
          <span>{hotel.rating} рейтинг</span>
          <span>{hotel.price_per_night.toLocaleString("ru-RU")} ₽/ночь</span>
        </div>
        <p className="ai-reason">{hotel.ai_reason}</p>
      </div>
    </article>
  );
}

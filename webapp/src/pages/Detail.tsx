import { useEffect, useState } from "react";
import { bookHotel, getHotel, type HotelDetail as HotelDetailType } from "../api/client";
import { openBookingLink, showBookSuccess } from "../tg";

interface Props {
  hotelId: string;
  onBack: () => void;
}

export function Detail({ hotelId, onBack }: Props) {
  const [hotel, setHotel] = useState<HotelDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getHotel(hotelId)
      .then(setHotel)
      .catch((e) => setError(String(e.message || e)))
      .finally(() => setLoading(false));
  }, [hotelId]);

  async function handleBook() {
    setBooking(true);
    try {
      const res = await bookHotel(hotelId);
      showBookSuccess(res.message || "Успешно забронировано!");
      if (res.booking_url) {
        openBookingLink(res.booking_url);
      }
    } catch (e) {
      setError(String((e as Error).message || e));
    } finally {
      setBooking(false);
    }
  }

  if (loading) return <p>Загрузка...</p>;
  if (error) return <div className="error">{error}</div>;
  if (!hotel) return <p>Отель не найден</p>;

  return (
    <section>
      <button className="btn secondary" onClick={onBack} style={{ marginBottom: 12 }}>
        ← К списку
      </button>
      <div className="detail-hero">
        <img src={hotel.photo_url} alt={hotel.name} />
      </div>
      <h1 className="hero-title">{hotel.name}</h1>
      <p className="hero-sub">
        {hotel.city} · {"★".repeat(hotel.stars)} · {hotel.rating} · {hotel.price_per_night.toLocaleString("ru-RU")}{" "}
        ₽/ночь · {hotel.distance_to_center_km} км до центра
      </p>
      <div className="detail-section">
        <p>{hotel.description}</p>
      </div>
      <div className="detail-section">
        <strong>Удобства</strong>
        <div className="amenities" style={{ marginTop: 8 }}>
          {hotel.amenities.map((a) => (
            <span className="chip" key={a}>
              {a}
            </span>
          ))}
        </div>
      </div>
      <div className="detail-section">
        <button className="btn block" disabled={booking} onClick={handleBook}>
          {booking ? "Бронирование..." : "Забронировать"}
        </button>
      </div>
    </section>
  );
}

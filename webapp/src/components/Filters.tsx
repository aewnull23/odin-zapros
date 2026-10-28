interface Props {
  maxPrice: number;
  priceLimit: number;
  onPriceLimit: (v: number) => void;
  minStars: number;
  onMinStars: (v: number) => void;
  maxDistance: number;
  onMaxDistance: (v: number) => void;
}

export function Filters({
  maxPrice,
  priceLimit,
  onPriceLimit,
  minStars,
  onMinStars,
  maxDistance,
  onMaxDistance,
}: Props) {
  return (
    <section className="filters">
      <strong>Фильтры</strong>
      <label>
        Цена до {priceLimit.toLocaleString("ru-RU")} ₽/ночь
        <input
          type="range"
          min={2000}
          max={Math.max(maxPrice, 3000)}
          step={500}
          value={priceLimit}
          onChange={(e) => onPriceLimit(Number(e.target.value))}
        />
      </label>
      <div className="filters-row">
        <label>
          Звёзды от
          <select value={minStars} onChange={(e) => onMinStars(Number(e.target.value))}>
            {[0, 2, 3, 4, 5].map((s) => (
              <option key={s} value={s}>
                {s === 0 ? "Любые" : s}
              </option>
            ))}
          </select>
        </label>
        <label>
          До центра, км
          <input
            type="number"
            min={0.5}
            max={15}
            step={0.5}
            value={maxDistance}
            onChange={(e) => onMaxDistance(Number(e.target.value))}
          />
        </label>
      </div>
    </section>
  );
}

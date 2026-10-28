interface Props {
  query: string;
  onQueryChange: (v: string) => void;
  onSubmit: () => void;
  loading?: boolean;
}

export function Welcome({ query, onQueryChange, onSubmit, loading }: Props) {
  return (
    <section>
      <h1 className="hero-title">О!дин запрос</h1>
      <p className="hero-sub">Куда и когда хотите поехать? Опишите поездку одним сообщением — AI подберёт отели.</p>
      <textarea
        placeholder="Куда и когда хотите поехать?"
        value={query}
        onChange={(e) => onQueryChange(e.target.value)}
      />
      <div style={{ marginTop: 12 }}>
        <button className="btn block" disabled={loading || query.trim().length < 5} onClick={onSubmit}>
          {loading ? "Отправка..." : "Найти отели"}
        </button>
      </div>
    </section>
  );
}

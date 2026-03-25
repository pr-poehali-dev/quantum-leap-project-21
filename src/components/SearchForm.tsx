import { useState } from "react";
import Icon from "@/components/ui/icon";

const SEARCH_URL = "https://functions.poehali.dev/f283c1d3-3bfb-455b-b885-ff94d711687c";

interface SearchResult {
  marketplace: string;
  name: string;
  brand: string;
  seller: string;
  price: number;
  url: string;
  match_type: string;
  risk: "high" | "medium";
}

export default function SearchForm() {
  const [brand, setBrand] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!brand.trim()) return;
    setLoading(true);
    setResults(null);
    setError("");
    setQuery(brand.trim());

    try {
      const resp = await fetch(SEARCH_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: brand.trim() }),
      });
      const data = await resp.json();
      const parsed = typeof data === "string" ? JSON.parse(data) : data;
      setResults(parsed.results || []);
    } catch {
      setError("Не удалось выполнить поиск. Попробуйте ещё раз.");
    } finally {
      setLoading(false);
    }
  };

  const wbResults = results?.filter((r) => r.marketplace === "Wildberries") ?? [];
  const ozonResults = results?.filter((r) => r.marketplace === "Ozon") ?? [];

  return (
    <div id="contact" className="bg-neutral-50 py-20 px-6">
      <div className="max-w-3xl mx-auto">
        <p className="uppercase text-sm tracking-wide text-neutral-500 mb-4 text-center">
          Бесплатная проверка
        </p>
        <h2 className="text-3xl md:text-5xl font-bold text-neutral-900 text-center mb-4 leading-tight">
          Проверьте свой бренд прямо сейчас
        </h2>
        <p className="text-neutral-500 text-center mb-10 text-base md:text-lg">
          Введите название товарного знака — мы найдём все упоминания на Wildberries и Ozon
        </p>

        <form onSubmit={handleSubmit} className="flex gap-0 mb-10">
          <input
            type="text"
            value={brand}
            onChange={(e) => setBrand(e.target.value)}
            placeholder="Например: ЕМКОЛБАСКИ"
            required
            className="flex-1 border border-neutral-300 border-r-0 bg-white px-5 py-4 text-neutral-900 text-base placeholder:text-neutral-400 focus:outline-none focus:border-neutral-900 transition-colors uppercase tracking-wide"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-neutral-900 text-white px-8 py-4 uppercase tracking-widest text-sm font-semibold hover:bg-neutral-700 transition-colors duration-300 disabled:opacity-60 disabled:cursor-not-allowed whitespace-nowrap flex items-center gap-2"
          >
            {loading ? (
              <>
                <Icon name="Loader2" size={16} className="animate-spin" />
                Ищем...
              </>
            ) : (
              <>
                <Icon name="Search" size={16} />
                Найти
              </>
            )}
          </button>
        </form>

        {error && (
          <div className="text-red-500 text-center mb-6">{error}</div>
        )}

        {results !== null && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-neutral-900">
                Результаты по запросу «{query}»
              </h3>
              <span className="text-sm text-neutral-500">
                Найдено: {results.length} товаров
              </span>
            </div>

            {results.length === 0 ? (
              <div className="text-center py-12 border border-neutral-200 bg-white">
                <div className="text-4xl mb-3">✅</div>
                <p className="text-neutral-700 font-semibold text-lg mb-1">Нарушений не обнаружено</p>
                <p className="text-neutral-400 text-sm">Товарный знак «{query}» не найден у сторонних продавцов</p>
              </div>
            ) : (
              <div className="space-y-8">
                {wbResults.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <span className="bg-[#CB11AB] text-white text-xs font-bold px-2 py-1 uppercase tracking-wide">Wildberries</span>
                      <span className="text-neutral-400 text-sm">{wbResults.length} товаров</span>
                    </div>
                    <div className="flex flex-col gap-3">
                      {wbResults.map((item, i) => (
                        <ResultCard key={i} item={item} />
                      ))}
                    </div>
                  </div>
                )}
                {ozonResults.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <span className="bg-[#005BFF] text-white text-xs font-bold px-2 py-1 uppercase tracking-wide">Ozon</span>
                      <span className="text-neutral-400 text-sm">{ozonResults.length} товаров</span>
                    </div>
                    <div className="flex flex-col gap-3">
                      {ozonResults.map((item, i) => (
                        <ResultCard key={i} item={item} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function ResultCard({ item }: { item: SearchResult }) {
  return (
    <a
      href={item.url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-start justify-between gap-4 bg-white border border-neutral-200 px-5 py-4 hover:border-neutral-400 transition-colors group"
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          {item.risk === "high" && (
            <span className="bg-red-100 text-red-600 text-xs font-semibold px-2 py-0.5 uppercase tracking-wide">
              Высокий риск
            </span>
          )}
          {item.risk === "medium" && (
            <span className="bg-yellow-100 text-yellow-700 text-xs font-semibold px-2 py-0.5 uppercase tracking-wide">
              Средний риск
            </span>
          )}
        </div>
        <p className="text-neutral-900 font-medium text-sm leading-snug truncate">{item.name}</p>
        <p className="text-neutral-400 text-xs mt-1">
          Бренд: <span className="text-neutral-600">{item.brand}</span>
          {" · "}
          Продавец: <span className="text-neutral-600">{item.seller}</span>
        </p>
      </div>
      <div className="flex flex-col items-end gap-1 shrink-0">
        {item.price > 0 && (
          <span className="text-neutral-900 font-semibold text-sm">{item.price.toLocaleString("ru-RU")} ₽</span>
        )}
        <Icon name="ExternalLink" size={14} className="text-neutral-300 group-hover:text-neutral-600 transition-colors" />
      </div>
    </a>
  );
}

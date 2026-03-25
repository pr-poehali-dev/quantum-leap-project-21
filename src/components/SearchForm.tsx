import { useState } from "react";

export default function SearchForm() {
  const [brand, setBrand] = useState("");
  const [contact, setContact] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!brand.trim()) return;
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setSubmitted(true);
    }, 1200);
  };

  return (
    <div id="contact" className="bg-neutral-50 py-20 px-6">
      <div className="max-w-2xl mx-auto">
        <p className="uppercase text-sm tracking-wide text-neutral-500 mb-4 text-center">
          Бесплатная проверка
        </p>
        <h2 className="text-3xl md:text-5xl font-bold text-neutral-900 text-center mb-4 leading-tight">
          Проверьте свой бренд прямо сейчас
        </h2>
        <p className="text-neutral-500 text-center mb-12 text-base md:text-lg">
          Введите название товарного знака — мы проверим маркетплейсы и свяжемся с вами с результатами
        </p>

        {submitted ? (
          <div className="text-center py-12 border border-neutral-200 bg-white">
            <div className="text-4xl mb-4">✅</div>
            <h3 className="text-xl font-bold text-neutral-900 mb-2">Заявка принята!</h3>
            <p className="text-neutral-500">
              Мы проверим <strong className="text-neutral-800">«{brand}»</strong> на всех маркетплейсах
              и свяжемся с вами в течение 24 часов.
            </p>
            <button
              onClick={() => { setSubmitted(false); setBrand(""); setContact(""); }}
              className="mt-6 text-sm underline text-neutral-500 hover:text-neutral-800 transition-colors"
            >
              Проверить ещё один бренд
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <label className="uppercase text-xs tracking-widest text-neutral-500">
                Название товарного знака *
              </label>
              <input
                type="text"
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
                placeholder="Например: ЕМКОЛБАСКИ"
                required
                className="w-full border border-neutral-300 bg-white px-5 py-4 text-neutral-900 text-base placeholder:text-neutral-400 focus:outline-none focus:border-neutral-900 transition-colors uppercase tracking-wide"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="uppercase text-xs tracking-widest text-neutral-500">
                Ваш телефон или email *
              </label>
              <input
                type="text"
                value={contact}
                onChange={(e) => setContact(e.target.value)}
                placeholder="+7 999 000 00 00 или email@mail.ru"
                required
                className="w-full border border-neutral-300 bg-white px-5 py-4 text-neutral-900 text-base placeholder:text-neutral-400 focus:outline-none focus:border-neutral-900 transition-colors"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-neutral-900 text-white px-6 py-4 uppercase tracking-widest text-sm font-semibold hover:bg-neutral-700 transition-colors duration-300 disabled:opacity-60 disabled:cursor-not-allowed mt-2"
            >
              {loading ? "Проверяем..." : "Проверить бесплатно"}
            </button>
            <p className="text-xs text-neutral-400 text-center">
              Нажимая кнопку, вы соглашаетесь на обработку персональных данных
            </p>
          </form>
        )}
      </div>
    </div>
  );
}

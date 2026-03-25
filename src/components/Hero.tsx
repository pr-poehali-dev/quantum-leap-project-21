import { useScroll, useTransform, motion } from "framer-motion";
import { useRef } from "react";

export default function Hero() {
  const container = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: container,
    offset: ["start start", "end start"],
  });
  const y = useTransform(scrollYProgress, [0, 1], ["0vh", "50vh"]);

  return (
    <div
      ref={container}
      className="relative flex items-center justify-center h-screen overflow-hidden"
    >
      <motion.div
        style={{ y }}
        className="absolute inset-0 w-full h-full"
      >
        <img
          src="/images/mountain-landscape.jpg"
          alt="Mountain landscape"
          className="w-full h-full object-cover"
        />
      </motion.div>

      <div className="relative z-10 text-center text-white">
        <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight mb-6">
          ЗАЩИТИ
        </h1>
        <p className="text-lg md:text-xl max-w-2xl mx-auto px-6 opacity-90">
          Находим нарушителей вашего товарного знака на маркетплейсах и помогаем остановить незаконное использование бренда
        </p>
        <div className="mt-10">
          <a
            href="#contact"
            className="bg-white text-black px-8 py-3 text-sm uppercase tracking-widest font-semibold hover:bg-transparent hover:text-white border border-white transition-all duration-300"
          >
            Проверить бренд бесплатно
          </a>
        </div>
      </div>
    </div>
  );
}
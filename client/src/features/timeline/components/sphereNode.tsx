export function SphereNode() {
  return (
    <div
      className="
            relative z-10
            w-full h-full  /* CHANGED: Was h-[130px] w-[130px] */
            rounded-full
            overflow-hidden
            shadow-[0_10px_25px_-5px_rgba(0,0,0,0.4)]
            bg-gradient-to-br from-[#9a7bff] via-[#7f5fff] to-[#5e21d6]
        "
    >
      {/* Top Shine */}
      <div
        className="
                absolute top-0 left-0 right-0 h-1/2
                rounded-t-full bg-gradient-to-b
                from-white/40 to-transparent mix-blend-screen
                "
      />

      {/* Noise Texture */}
      <div
        className="
                absolute inset-0 opacity-[0.16]
                bg-[url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/w8AAusB9YpU8F0AAAAASUVORK5CYII=')]
                bg-repeat
                "
      />
    </div>
  );
}

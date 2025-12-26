export function ChildNodeLabel({ text }: { text: string }) {
  return (
    <div
      className="
        /* POSITIONING */
        absolute 
        left-1/2 -translate-x-1/2  /* Center horizontally relative to sphere */
        top-full.               /* Push below the sphere */
        z-20                       /* Ensure it sits on top of other lines */

        /* TYPOGRAPHY */
        font-medium
        whitespace-nowrap          /* prevent text from wrapping vertically */
        text-white/90              /* High contrast text */

        /* BOX STYLING */
        px-2 py-0.5 
        bg-black/60                /* Semi-transparent background for readability */
        backdrop-blur-sm           /* Cool glass effect */
        border border-white/20 
        rounded-full               /* Pill shape looks better on timelines */
      "
      style={{
        fontSize: "calc(var(--lane-height) * 0.10)",
      }}
    >
      {text}
    </div>
  );
}

import { Easing, interpolate, useCurrentFrame } from "remotion";

// A word that pops in at `delay` frames (relative to its scene).
export const Word: React.FC<{
  readonly children: React.ReactNode;
  readonly delay: number;
  readonly style?: React.CSSProperties;
}> = ({ children, delay, style }) => {
  const frame = useCurrentFrame();

  return (
    <span
      style={{
        display: "inline-block",
        marginRight: "0.25em",
        opacity: interpolate(frame, [delay, delay + 8], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        }),
        translate: interpolate(frame, [delay, delay + 14], ["0px 60px", "0px 0px"], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.16, 1, 0.3, 1),
        }),
        scale: interpolate(frame, [delay, delay + 14], [0.7, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.spring({ damping: 12 }),
          output: "perceptual-scale",
        }),
        ...style,
      }}
    >
      {children}
    </span>
  );
};

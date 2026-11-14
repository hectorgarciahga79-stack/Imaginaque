import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { colors } from "./theme";

// Generated as one template: decorative orbs drifting slowly.
const ORBS = [
  { x: 180, y: 320, r: 420, color: colors.accent2, speed: 0.9 },
  { x: 900, y: 760, r: 520, color: colors.accent1, speed: 0.6 },
  { x: 260, y: 1500, r: 480, color: colors.accent3, speed: 0.75 },
  { x: 880, y: 1700, r: 360, color: colors.accent2, speed: 1.1 },
];

export const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  return (
    <AbsoluteFill
      style={{
        backgroundImage: `linear-gradient(180deg, ${colors.bgTop} 0%, ${colors.bgBottom} 100%)`,
        overflow: "hidden",
      }}
    >
      {ORBS.map((o, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: o.x - o.r / 2,
            top: o.y - o.r / 2,
            width: o.r,
            height: o.r,
            borderRadius: "50%",
            background: o.color,
            opacity: 0.28,
            filter: "blur(110px)",
            translate: `${Math.sin(t * o.speed + i) * 90}px ${Math.cos(t * o.speed * 0.8 + i) * 120}px`,
          }}
        />
      ))}
      {/* subtle vignette */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)",
          opacity: interpolate(frame, [0, fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      />
    </AbsoluteFill>
  );
};

import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { colors } from "./theme";

export const ProgressBar: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  return (
    <div
      style={{
        position: "absolute",
        top: 70,
        left: 80,
        right: 80,
        height: 8,
        borderRadius: 4,
        background: "rgba(255,255,255,0.15)",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          height: "100%",
          width: `${interpolate(frame, [0, durationInFrames - 1], [0, 100], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })}%`,
          backgroundImage: `linear-gradient(90deg, ${colors.accent3}, ${colors.accent1})`,
        }}
      />
    </div>
  );
};

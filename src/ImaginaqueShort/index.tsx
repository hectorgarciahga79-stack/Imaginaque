import { Track, useVideoConfig } from "remotion";
import { Background } from "./Background";
import { ProgressBar } from "./ProgressBar";
import { Claim, Hook, Outro, Pipeline } from "./scenes";

// Vertical 1080x1920 test short for TikTok / YouTube Shorts.
export const ImaginaqueShort: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <>
      <Background />
      <Track name="Escenas">
        <Hook
          name="Gancho"
          durationInFrames={3 * fps}
          style={{ justifyContent: "center", alignItems: "center" }}
        />
        <Pipeline
          name="Proceso"
          from={3 * fps}
          durationInFrames={4.5 * fps}
          style={{ justifyContent: "center", alignItems: "center" }}
        />
        <Claim
          name="Mensaje"
          from={7.5 * fps}
          durationInFrames={2.5 * fps}
          style={{ justifyContent: "center", alignItems: "center" }}
        />
        <Outro
          name="Cierre"
          from={10 * fps}
          durationInFrames={3 * fps}
          style={{ justifyContent: "center", alignItems: "center" }}
        />
      </Track>
      <ProgressBar />
    </>
  );
};

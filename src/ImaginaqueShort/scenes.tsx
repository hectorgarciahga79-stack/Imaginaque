import { Easing, interpolate, Interactive, useCurrentFrame, useVideoConfig } from "remotion";
import { Word } from "./Word";
import { colors, fontFamily, gradientText } from "./theme";

const sceneText: React.CSSProperties = {
  fontFamily,
  color: colors.text,
  textAlign: "center",
  padding: "0 90px",
  margin: 0,
};

// Fades the whole scene out during its last frames.
const useExit = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return interpolate(frame, [durationInFrames - 8, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

/* ---------- 1. Hook ---------- */
const HookInner: React.FC = () => {
  const opacity = useExit();
  return (
    <>
      <h1 style={{ ...sceneText, fontSize: 116, fontWeight: 800, lineHeight: 1.15, opacity }}>
        <Word delay={0}>¿Y</Word>
        <Word delay={4}>si</Word>
        <Word delay={8}>una</Word>
        <Word delay={12}>IA</Word>
        <br />
        <Word delay={20} style={gradientText}>
          imaginara
        </Word>
        <br />
        <Word delay={30}>tu</Word>
        <Word delay={34}>próxima</Word>
        <Word delay={38}>historia?</Word>
      </h1>
    </>
  );
};

export const Hook = Interactive.create({
  Component: HookInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});

/* ---------- 2. Pipeline ---------- */
const STEPS = [
  { n: "1", title: "Idea", desc: "Una historia original" },
  { n: "2", title: "Guion", desc: "Escrito para enganchar" },
  { n: "3", title: "Voz", desc: "Narración natural" },
  { n: "4", title: "Vídeo", desc: "Escenas cinematográficas" },
];

const StepCard: React.FC<{ readonly index: number; readonly step: (typeof STEPS)[number] }> = ({
  index,
  step,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const start = 0.6 * fps + index * 0.45 * fps;
  const progress = interpolate(frame, [start, start + 0.5 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const accent = [colors.accent3, colors.accent2, colors.accent1, colors.accent3][index];

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 40,
        width: 860,
        padding: "34px 44px",
        borderRadius: 36,
        background: "rgba(255,255,255,0.07)",
        border: "2px solid rgba(255,255,255,0.14)",
        opacity: progress,
        translate: `${(1 - progress) * (index % 2 === 0 ? -200 : 200)}px 0px`,
      }}
    >
      <div
        style={{
          width: 110,
          height: 110,
          flexShrink: 0,
          borderRadius: "50%",
          background: accent,
          color: colors.bgTop,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 60,
          fontWeight: 800,
        }}
      >
        {step.n}
      </div>
      <div style={{ textAlign: "left" }}>
        <div style={{ fontSize: 72, fontWeight: 800, lineHeight: 1.05 }}>{step.title}</div>
        <div style={{ fontSize: 44, color: colors.muted, fontWeight: 400 }}>{step.desc}</div>
      </div>
    </div>
  );
};

const PipelineInner: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = useExit();
  return (
    <div
      style={{
        ...sceneText,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 34,
        opacity,
      }}
    >
      <h2
        style={{
          fontSize: 96,
          fontWeight: 800,
          margin: "0 0 30px 0",
          opacity: interpolate(frame, [0, 0.4 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        De la idea <span style={gradientText}>al vídeo</span>
      </h2>
      {STEPS.map((s, i) => (
        <StepCard key={s.n} index={i} step={s} />
      ))}
    </div>
  );
};

export const Pipeline = Interactive.create({
  Component: PipelineInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});

/* ---------- 3. Claim ---------- */
const ClaimInner: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = useExit();
  return (
    <div style={{ ...sceneText, opacity }}>
      <div style={{ fontSize: 110, fontWeight: 800, lineHeight: 1.1 }}>
        <Word delay={0}>Todo</Word>
        <Word delay={5}>automático.</Word>
      </div>
      <div
        style={{
          ...gradientText,
          fontSize: 190,
          fontWeight: 800,
          lineHeight: 1.1,
          marginTop: 30,
          scale: interpolate(frame, [0.4 * fps, 1.1 * fps], [0.5, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.spring({ damping: 10 }),
            output: "perceptual-scale",
          }),
          opacity: interpolate(frame, [0.4 * fps, 0.7 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        TikTok
        <br />& Shorts
      </div>
    </div>
  );
};

export const Claim = Interactive.create({
  Component: ClaimInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});

/* ---------- 4. Outro / CTA ---------- */
const OutroInner: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ ...sceneText, display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div
        style={{
          fontSize: 128,
          fontWeight: 800,
          letterSpacing: -3,
          scale: interpolate(frame, [0, 0.8 * fps], [0.3, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.spring({ damping: 11 }),
            output: "perceptual-scale",
          }),
          opacity: interpolate(frame, [0, 0.3 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Imagina<span style={gradientText}>Que</span>
      </div>
      <div
        style={{
          marginTop: 60,
          fontSize: 50,
          fontWeight: 600,
          whiteSpace: "nowrap",
          padding: "26px 60px",
          borderRadius: 999,
          backgroundImage: `linear-gradient(90deg, ${colors.accent2}, ${colors.accent1})`,
          opacity: interpolate(frame, [0.8 * fps, 1.1 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          translate: interpolate(frame, [0.8 * fps, 1.2 * fps], ["0px 40px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
          scale: interpolate(
            frame,
            [1.5 * fps, 1.8 * fps, 2.1 * fps],
            [1, 1.06, 1],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
          ),
        }}
      >
        Síguenos para más
      </div>
    </div>
  );
};

export const Outro = Interactive.create({
  Component: OutroInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});

import { loadFont } from "@remotion/google-fonts/Poppins";

export const { fontFamily } = loadFont("normal", {
  weights: ["400", "600", "800"],
  subsets: ["latin", "latin-ext"],
});

export const colors = {
  bgTop: "#0b0620",
  bgBottom: "#2a0f5c",
  accent1: "#ff4ecd",
  accent2: "#7c5cff",
  accent3: "#2de2e6",
  text: "#ffffff",
  muted: "rgba(255,255,255,0.72)",
};

export const gradientText: React.CSSProperties = {
  backgroundImage: `linear-gradient(90deg, ${colors.accent3}, ${colors.accent2}, ${colors.accent1})`,
  WebkitBackgroundClip: "text",
  backgroundClip: "text",
  color: "transparent",
};

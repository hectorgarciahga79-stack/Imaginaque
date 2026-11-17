"""Perfiles de calidad. El render se hace a 'resolution' y FFmpeg escala a
1080x1920 (lanczos + enfoque) cuando hace falta: así un equipo sin GPU
mantiene tiempos razonables y una GPU potente renderiza a resolución nativa."""

PROFILES = {
    # vista previa ultrarrápida para ajustar cámaras y tiempos
    "preview": {"resolution": (360, 640), "samples": 6, "adaptive_threshold": 0.1, "motion_blur": False,
                "volumetrics": False, "rain_density": 0.5, "smoke": True, "step": 4},
    # CPU sin GPU (este equipo): 720x1280 + reescalado, ~10-20 s/fotograma
    "cpu_draft": {"resolution": (540, 960), "samples": 10, "adaptive_threshold": 0.05, "motion_blur": True,
                  "volumetrics": False, "rain_density": 0.8, "smoke": True},
    # (la caja de niebla volumetrica duplica el coste en CPU: se usa niebla por pase Mist)
    "cpu_balanced": {"resolution": (720, 1280), "samples": 14, "adaptive_threshold": 0.04, "motion_blur": True,
                     "volumetrics": False, "volume_step_rate": 4.0, "rain_density": 1.0, "smoke": True},
    # GPU dedicada
    "gpu_mid": {"resolution": (1080, 1920), "samples": 64, "adaptive_threshold": 0.02, "motion_blur": True,
                "volumetrics": True, "volume_step_rate": 1.5, "rain_density": 1.0, "smoke": True,
                "diffuse_bounces": 3, "glossy_bounces": 4},
    "gpu_high": {"resolution": (1080, 1920), "samples": 192, "adaptive_threshold": 0.01, "motion_blur": True,
                 "volumetrics": True, "volume_step_rate": 1.0, "rain_density": 1.2, "smoke": True,
                 "diffuse_bounces": 4, "glossy_bounces": 6, "png16": True, "volumetric_fx": True},
}


def get(name, overrides=None):
    p = dict(PROFILES[name])
    p.update(overrides or {})
    p["name"] = name
    return p

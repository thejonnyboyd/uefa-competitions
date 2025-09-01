from pathlib import Path
import yaml
from engine.schemas import Config, Team, Pot

def _normalise(cfg: dict) -> dict:
    def make_id(name): return "".join(c.lower() for c in name if c.isalnum())[:12]
    for p_idx, p in enumerate(cfg["pots"], start=1):
        for t in p.get("teams", []):
            t.setdefault("id", make_id(t["name"]))
            t["pot"] = p_idx
    return cfg

def load_config(competition: str) -> Config:
    file = Path(__file__).with_suffix("").parent / f"{competition.lower()}.yaml"
    if not file.exists():
        file = Path(__file__).with_suffix("").parent / "ucl_2025_26.yaml"
    cfg = yaml.safe_load(file.read_text())
    cfg = _normalise(cfg)
    return Config.model_validate(cfg)
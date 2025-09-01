import hashlib, json
from engine.schemas import DrawRequest, DrawResult
from engine.config.reader import load_config
from engine.solver.cp_sat import solve

def compute_draw_id(cfg_dict: dict, seed: int | None) -> str:
    key = json.dumps({"cfg": cfg_dict, "seed": seed}, sort_keys=True).encode()
    return hashlib.sha256(key).hexdigest()[:12]

def run_draw(req: DrawRequest) -> DrawResult:
    cfg = load_config(req.competition)
    cfg_dict = cfg.model_dump()
    fixtures, meta = solve(cfg, req.seed)
    draw_id = compute_draw_id(cfg_dict, req.seed)
    return DrawResult(draw_id=draw_id, fixtures=fixtures, solver_meta=meta)
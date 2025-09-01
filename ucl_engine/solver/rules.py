from collections import defaultdict
from typing import Dict, List, Set, Tuple
from ucl_engine.schemas import Config

def pot_index(cfg: Config) -> Dict[str, int]:
    return {team.id: pot_idx for pot_idx, pot in enumerate(cfg.pots, start=1) for team in pot.teams}

def teams_by_pot(cfg: Config) -> Dict[int, List[str]]:
    return {pot_idx: [team.id for team in pot.teams] for pot_idx, pot in enumerate(cfg.pots, start=1)}

def forbidden_pairs(cfg: Config) -> Set[Tuple[str, str]]:
    block: Set[Tuple[str, str]] = set()
    if cfg.rules.block_same_federation:
        teams = [t for p in cfg.pots for t in p.teams]
        by_federation: Dict[str, List[str]] = defaultdict(list)
        for t in teams:
            by_federation[t.federation].append(t.id)
        for ids in by_federation.values():
            for i in ids:
                for j in ids:
                    if i != j:
                        block.add((i, j))
                        block.add((j, i))
    return block

def opponents_by_federation(cfg: Config) -> Dict[str, Dict[str, List[str]]]:
    teams = [t for p in cfg.pots for t in p.teams]
    by_federation: Dict[str, List[str]] = defaultdict(list)
    for t in teams:
        by_federation[t.federation].append(t.id)
    out: Dict[str, Dict[str, List[str]]] = {}
    for t in teams:
        inner: Dict[str, List[str]] = {}
        for fed, ids in by_federation.items():
            inner[fed] = [u for u in ids if u != t.id]
        out[t.id] = inner
    return out

def quotas(cfg: Config) -> tuple[int, int]:
    return cfg.rules.home_away_balance["home"], cfg.rules.home_away_balance["away"]

from ortools.sat.python import cp_model
from engine.schemas import Config, Fixture, SolverMeta
from engine.solver.rules import (
    forbidden_pairs, quotas, opponents_by_federation, pot_index, teams_by_pot
)
import time

def solve(cfg: Config, seed: int | None):
    teams = [t for p in cfg.pots for t in p.teams]
    idx = {t.id: i for i, t in enumerate(teams)}
    n = len(teams)
    home_q, away_q = quotas(cfg)
    forb = forbidden_pairs(cfg)

    matches_needed = home_q + away_q
    if matches_needed > n - 1:
        raise RuntimeError(f"Infeasible: each team needs {matches_needed} opponents but only {n-1} exist.")

    enforce_pot_split = (len(cfg.pots) == 4 and home_q == 4 and away_q == 4)
    tbp = teams_by_pot(cfg)     
    fed_of = {t.id: t.federation for t in teams}

    if enforce_pot_split:
        for t in teams:
            for p_idx, ids in tbp.items():
                cands = [u for u in ids if u != t.id and fed_of[u] != t.federation]
                if len(cands) < 2:
                    raise RuntimeError(
                        f"Infeasible for {t.name}: needs 2 opponents in Pot {p_idx} not in same federation; only {len(cands)} available."
                    )

    m = cp_model.CpModel()
    x = {}
    for i in range(n):
        for j in range(n):
            if i == j: 
                continue
            tid_i, tid_j = teams[i].id, teams[j].id
            if (tid_i, tid_j) in forb or (tid_j, tid_i) in forb:
                x[i, j] = m.NewConstant(0)
            else:
                x[i, j] = m.NewBoolVar(f"x_{i}_{j}")

    for i in range(n):
        for j in range(i + 1, n):
            m.Add(x[i, j] + x[j, i] <= 1)

    for i in range(n):
        m.Add(sum(x[i, j] for j in range(n) if j != i) == home_q)  # home
        m.Add(sum(x[j, i] for j in range(n) if j != i) == away_q)  # away

    if enforce_pot_split:
        for i in range(n):
            my_id = teams[i].id
            for p_idx, ids in tbp.items():
                j_idxs = [idx[tid] for tid in ids if tid != my_id]
                m.Add(sum(x[i, j] for j in j_idxs) == 1)
                m.Add(sum(x[j, i] for j in j_idxs) == 1)

    cap = cfg.rules.max_per_foreign_federation
    if cap is not None:
        opp_by_fed = opponents_by_federation(cfg)
        for i in range(n):
            tid_i = teams[i].id
            my_fed = teams[i].federation
            for fed, ids in opp_by_fed[tid_i].items():
                if fed == my_fed:
                    continue
                j_idxs = [idx[tid] for tid in ids]
                m.Add(sum(x[i, j] for j in j_idxs) + sum(x[j, i] for j in j_idxs) <= cap)

    solver = cp_model.CpSolver()
    if seed is not None:
        solver.parameters.random_seed = seed
    solver.parameters.max_time_in_seconds = 5.0
    solver.parameters.num_search_workers = 8

    t0 = time.time()
    status = solver.Solve(m)
    elapsed = int((time.time() - t0) * 1000)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("No feasible draw for this config/constraints.")

    fixtures = []
    for i in range(n):
        for j in range(n):
            if i != j and solver.Value(x[i, j]) == 1:
                fixtures.append(Fixture(home_team_id=teams[i].id, away_team_id=teams[j].id))

    meta = SolverMeta(solver="cp-sat", time_ms=elapsed, random_seed=seed)
    return fixtures, meta

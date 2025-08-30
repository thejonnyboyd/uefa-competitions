from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class Team(BaseModel):
    id: str
    name: str
    federation: str
    pot: int

class Pot(BaseModel):
    name: str
    teams: List[Team]

class RuleSet(BaseModel):
    matches_per_team: int = 8
    home_away_balance: Dict[str, int] = {"home": 4, "away": 4}
    block_same_federation: bool = True
    max_per_foreign_federation: Optional[int] = 2

class Config(BaseModel):
    competition: str
    season: str
    pots: List[Pot]
    rules: RuleSet

class Fixture(BaseModel):
    home_team_id: str
    away_team_id: str

class DrawRequest(BaseModel):
    competition: str
    seed: Optional[int] = None

class SolverMeta(BaseModel):
    solver: str
    time_ms: int
    random_seed: Optional[int] = None

class DrawResult(BaseModel):
    draw_id: str
    fixtures: List[Fixture]
    stats: Dict[str, int] = Field(default_factory=dict)
    solver_meta: SolverMeta
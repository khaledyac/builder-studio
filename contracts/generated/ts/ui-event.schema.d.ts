/* Builder Studio contracts 1.0.0. Generated from the JSON Schemas: edit the Pydantic models, then run task contracts-gen. */

export type UiEvent = Message | QuestionCard | SummaryCard | PlanCard | Status | PreviewRefresh | Cost;
export type Line = string;
export type RiskTier = 1 | 2 | 3;
export type SessionState = "starting" | "ready" | "building" | "idle" | "rebuilding" | "deleted";

export interface Message {
  id: string;
  type: "message";
  role: "builder" | "agent";
  text: string;
}
export interface QuestionCard {
  id: string;
  type: "question-card";
  question: Line;
  /**
   * @minItems 1
   * @maxItems 5
   */
  suggested_answers:
    [Line] | [Line, Line] | [Line, Line, Line] | [Line, Line, Line, Line] | [Line, Line, Line, Line, Line];
}
export interface SummaryCard {
  id: string;
  type: "summary-card";
  /**
   * @minItems 1
   * @maxItems 12
   */
  summary:
    | [Line]
    | [Line, Line]
    | [Line, Line, Line]
    | [Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line];
  tier: RiskTier;
  tier_reasons: Line[];
}
export interface PlanCard {
  id: string;
  type: "plan-card";
  summary: Line;
  /**
   * @minItems 1
   * @maxItems 20
   */
  steps:
    | [Line]
    | [Line, Line]
    | [Line, Line, Line]
    | [Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line, Line]
    | [
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line,
        Line
      ];
}
export interface Status {
  id: string;
  type: "status";
  state: SessionState;
  detail?: Line | null;
}
export interface PreviewRefresh {
  id: string;
  type: "preview-refresh";
  url: string;
}
export interface Cost {
  id: string;
  type: "cost";
  tokens: number;
  cost_usd: number;
}

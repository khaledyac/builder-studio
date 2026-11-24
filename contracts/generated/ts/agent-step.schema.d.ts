/* Builder Studio contracts 1.0.0. Generated from the JSON Schemas: edit the Pydantic models, then run task contracts-gen. */

export type UserId = string;
export type AppId = string;
export type SessionId = string;
export type AgentStepKind = "intake" | "router" | "fast" | "lead" | "worker";
export type IdempotencyKey = string;

export interface AgentStep {
  contract_version: string;
  context: CallContext;
  kind: AgentStepKind;
  input: string;
  idempotency_key: IdempotencyKey;
}
/**
 * The IDs that travel together: every model call, log line and agent step carries them.
 */
export interface CallContext {
  user_id: UserId;
  app_id: AppId;
  session_id: SessionId;
}

/* Builder Studio contracts 1.0.0. Generated from the JSON Schemas: edit the Pydantic models, then run task contracts-gen. */

export type Event =
  | SessionStarted
  | SessionReady
  | SessionIdle
  | SessionDeleted
  | IntakeConfirmed
  | PlanApproved
  | TicketUpdated
  | MergeDone
  | PreviewRefreshed
  | PublishRequested
  | CheckCompleted
  | DeployCompleted
  | ReviewRequested
  | ReviewCompleted
  | BudgetExceeded;
export type UserId = string;
export type AppId = string;
export type SessionId = string;
export type BranchName = string;
export type CommitSha = string;
export type Environment = "lab" | "staging" | "production";
export type ReviewKind = "domain-owner" | "engineer" | "security" | "dpo" | "legal";

export interface SessionStarted {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "session.started";
  data: SessionData;
}
export interface SessionData {
  context: CallContext;
}
/**
 * The IDs that travel together: every model call, log line and agent step carries them.
 */
export interface CallContext {
  user_id: UserId;
  app_id: AppId;
  session_id: SessionId;
}
export interface SessionReady {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "session.ready";
  data: SessionData;
}
export interface SessionIdle {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "session.idle";
  data: SessionData;
}
export interface SessionDeleted {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "session.deleted";
  data: SessionData;
}
export interface IntakeConfirmed {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "intake.confirmed";
  data: SessionData;
}
export interface PlanApproved {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "plan.approved";
  data: SessionData;
}
export interface TicketUpdated {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "ticket.updated";
  data: TicketData;
}
export interface TicketData {
  context: CallContext;
  ticket: number;
  state: "open" | "in-progress" | "done";
}
export interface MergeDone {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "merge.done";
  data: MergeData;
}
export interface MergeData {
  context: CallContext;
  branch: BranchName;
  sha: CommitSha;
}
export interface PreviewRefreshed {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "preview.refreshed";
  data: PreviewData;
}
export interface PreviewData {
  context: CallContext;
  sha: CommitSha;
}
export interface PublishRequested {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "publish.requested";
  data: SessionData;
}
export interface CheckCompleted {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "check.completed";
  data: CheckData;
}
export interface CheckData {
  app_id: AppId;
  name: string;
  conclusion: "success" | "failure" | "neutral" | "cancelled" | "skipped" | "timed_out" | "action_required";
}
export interface DeployCompleted {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "deploy.completed";
  data: DeployData;
}
export interface DeployData {
  app_id: AppId;
  environment: Environment;
  version: string;
  outcome: "success" | "failure";
}
export interface ReviewRequested {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "review.requested";
  data: ReviewRequestData;
}
export interface ReviewRequestData {
  app_id: AppId;
  review: ReviewKind;
}
export interface ReviewCompleted {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "review.completed";
  data: ReviewResultData;
}
export interface ReviewResultData {
  app_id: AppId;
  review: ReviewKind;
  outcome: "approved" | "changes-requested";
}
export interface BudgetExceeded {
  specversion?: "1.0";
  id: string;
  source: string;
  time: string;
  datacontenttype?: "application/json";
  contractversion: string;
  type: "budget.exceeded";
  data: BudgetData;
}
export interface BudgetData {
  context: CallContext;
  scope: "session" | "user-day";
}

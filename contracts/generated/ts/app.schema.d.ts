/* Builder Studio contracts 1.0.0. Generated from studio.contracts: edit the Pydantic models, then run task contracts-gen. */

export type AppId = string;
export type UserId = string;
export type DomainId = string;
export type ProjectType = "form-workflow" | "dashboard" | "chat-assistant" | "records" | "adk-agent";
export type AccessMode = "read" | "write";
export type ApprovedModule = "firestore" | "cloud-sql" | "cloud-storage" | "pubsub" | "cloud-scheduler";
export type Audience = "personal" | "team" | "domain";
export type RiskTier = 1 | 2 | 3;

export interface AppManifest {
  /**
   * The contracts version it was written with. Readers accept 1.x.
   */
  contract_version: string;
  name: AppId;
  owner: UserId;
  domain: DomainId;
  project_type: ProjectType;
  connectors?: {
    [k: string]: AccessMode;
  };
  resources?: Resource[];
  audience: Audience;
  risk_tier?: RiskTier | null;
  expires_on: string;
}
export interface Resource {
  module: ApprovedModule;
  name: string;
}

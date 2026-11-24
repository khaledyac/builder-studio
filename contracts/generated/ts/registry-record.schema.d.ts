/* Builder Studio contracts 1.0.0. Generated from the JSON Schemas: edit the Pydantic models, then run task contracts-gen. */

export type AppId = string;
export type UserId = string;
export type DomainId = string;
export type RiskTier = 1 | 2 | 3;
export type RepoName = string;
export type Environment = "lab" | "staging" | "production";
export type Environments = Environment[];
export type RegistryStatus = "draft" | "live-lab" | "live-prod" | "expired" | "archived";

export interface RegistryRecord {
  contract_version: string;
  app_id: AppId;
  owner: UserId;
  domain: DomainId;
  tier: RiskTier;
  expires_on: string;
  repo: RepoName;
  environments?: Environments;
  status: RegistryStatus;
}

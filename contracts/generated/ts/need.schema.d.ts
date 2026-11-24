/* Builder Studio contracts 1.0.0. Generated from studio.contracts: edit the Pydantic models, then run task contracts-gen. */

export type Line = string;
export type ConnectorId = string;
export type ConnectorIds = ConnectorId[];
export type AccessMode = "read" | "write";
export type Audience = "personal" | "team" | "domain";
export type DomainId = string;
export type ProjectType = "form-workflow" | "dashboard" | "chat-assistant" | "records" | "adk-agent";

export interface Need {
  /**
   * The contracts version it was written with. Readers accept 1.x.
   */
  contract_version: string;
  problem: string;
  users: Line;
  /**
   * @minItems 2
   * @maxItems 3
   */
  examples: [Line, Line] | [Line, Line, Line];
  data?: ConnectorIds;
  access: AccessMode;
  audience: Audience;
  out_of_scope?: Line[];
  domain: DomainId;
  project_type: ProjectType;
}

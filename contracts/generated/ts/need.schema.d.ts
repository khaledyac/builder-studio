/* Builder Studio contracts 1.0.0. Generated from the JSON Schemas: edit the Pydantic models, then run task contracts-gen. */

export type Sentence = string;
export type ConnectorId = string;
export type ConnectorIds = ConnectorId[];
export type AccessMode = "read" | "write";
export type Audience = "personal" | "team" | "domain";
export type DomainId = string;
export type ProjectType = "form-workflow" | "dashboard" | "chat-assistant" | "records" | "adk-agent";

export interface Need {
  contract_version: string;
  problem: string;
  users: Sentence;
  /**
   * @minItems 2
   * @maxItems 3
   */
  examples: [Sentence, Sentence] | [Sentence, Sentence, Sentence];
  data?: ConnectorIds;
  access: AccessMode;
  audience: Audience;
  out_of_scope?: Sentence[];
  domain: DomainId;
  project_type: ProjectType;
}

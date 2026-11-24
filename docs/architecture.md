# Vibe coding platform · target architecture

**One shared hub, one sandbox per session, one governed path to production.**

Business people ("AI builders") describe an app in plain language. Agents build it in an isolated workspace while the builder watches a live preview. Publish opens a pull request, and the GitHub pipeline deploys the app to its domain's spoke, following the app's risk tier.

- **Scope:** one company, on Google Cloud, using generally available services only.
- **Status:** target design for v1. Open points are listed at the end.

**Colours used in the diagrams**

| Colour | Meaning |
|---|---|
| Yellow | People |
| Purple | Outside GCP: Okta, GitHub, Trust Layer |
| Peach | Created for each session |
| Grey | GCP service |

## Contents

1. [Overview](#1-overview)
2. [Full architecture](#2-full-architecture)
3. [Builder journey](#3-builder-journey)
4. [How a message is handled](#4-how-a-message-is-handled)
5. [Workspace lifecycle](#5-workspace-lifecycle)
6. [Branches](#6-branches)
7. [Project template](#7-project-template)
8. [Publish and risk tiers](#8-publish-and-risk-tiers)
9. [Identity and model calls](#9-identity-and-model-calls)
10. [Day two](#10-day-two)
11. [Components](#11-components)
12. [Guardrails](#12-guardrails)
13. [Cost](#13-cost)
14. [Decisions and open points](#14-decisions-and-open-points)

---

## 1. Overview

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#EEF0F2", "primaryBorderColor": "#8A949C", "primaryTextColor": "#211C19", "lineColor": "#5F6B73", "clusterBkg": "#FAF8F4", "clusterBorder": "#CFC5B4", "edgeLabelBackground": "#FFFFFF"}}}%%
flowchart LR
    builders["AI builders"]
    subgraph HUB["Hub · shared by everyone"]
        studio["Builder Studio<br/>Web UI · Platform API · agent service"]
    end
    subgraph PERSESSION["Created for each session"]
        ws["Session workspace<br/>one Cloud Run service per session"]
    end
    gh["GitHub<br/>app repo · pull requests · Actions"]
    subgraph SPOKES["Spoke · one per domain"]
        spokes["Lab · Staging · Production"]
    end
    tl["Trust Layer"]
    vx["Vertex AI · Claude"]
    data[("Domain data<br/>read-only connectors")]
    cross["Security · governance · observability · FinOps<br/>across hub and spokes"]

    builders -->|"chat + live preview"| studio
    studio -->|"tool calls"| ws
    ws -->|"git push"| gh
    gh -->|"Terraform, keyless"| spokes
    studio -->|"every model call"| tl
    spokes -->|"app model calls"| tl
    tl --> vx
    spokes --> data

    classDef default fill:#EEF0F2,stroke:#8A949C,color:#211C19
    classDef people fill:#FBE9A6,stroke:#B8962E,color:#211C19
    classDef ext fill:#E7DDF6,stroke:#7B5FB0,color:#211C19
    classDef session fill:#FBD9C3,stroke:#C9773F,color:#211C19
    class builders people
    class gh,tl ext
    class ws session
```

- **Hub:** everything shared. The UI, the APIs, the agents and their state live in one hub project owned by the Platform Owner.
- **Workspace:** the only place agent-written code runs. It has synthetic data only, no route to the spokes, and its only way out is a pull request.
- **Spokes:** one per domain, owned by the Domain Owner. Each has a non-production project (Lab, Staging) and a production project.

## 2. Full architecture

Every GCP component, with the main flows. Section 11 describes each one.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#EEF0F2", "primaryBorderColor": "#8A949C", "primaryTextColor": "#211C19", "lineColor": "#5F6B73", "clusterBkg": "#FAF8F4", "clusterBorder": "#CFC5B4", "edgeLabelBackground": "#FFFFFF"}}}%%
flowchart TB
    subgraph PEOPLE["People"]
        builder["AI builders<br/>no code, no infrastructure"]
        downer["Domain Owner<br/>owns a spoke, approves Tier 2"]
        reviewers["Reviewers<br/>DPO · legal · security"]
        powner["Platform Owner<br/>hub, templates, skills, pipelines"]
    end

    subgraph EDGE["Edge and identity"]
        okta["Okta<br/>SSO · groups to roles"]
        dns["Cloud DNS<br/>+ Certificate Manager"]
        lb["External Application Load Balancer<br/>Cloud Armor WAF · IAP<br/>Okta via Workforce Identity Federation"]
    end

    subgraph HUB["Hub project · Platform Owner"]
        subgraph HUBX["Experience and APIs"]
            webui["Web UI · Cloud Run<br/>gallery · chat · preview"]
            api["Platform API · Cloud Run<br/>sessions, intake, Publish, status"]
            pxy["Preview proxy · Cloud Run<br/>author only"]
            regapi["Registry API · Cloud Run<br/>owner · tier · expiry"]
            whk["Webhook receiver · Cloud Run<br/>GitHub events"]
        end
        subgraph HUBA["Agents and state"]
            tasks[["Cloud Tasks<br/>agent steps, retries, rate limits"]]
            agent["Agent service · Cloud Run<br/>intake · router · lead · workers"]
            smgr["Session manager · Cloud Run<br/>creates and deletes workspaces"]
            sched["Cloud Scheduler<br/>idle reaper · expiry checks"]
            secrets["Secret Manager<br/>GitHub App key, Okta client"]
            valkey[("Memorystore for Valkey<br/>live state, plan, merge lock")]
            fs[("Firestore<br/>sessions, conversations, registry")]
            ps[["Pub/Sub<br/>GitHub, deploy, review events"]]
            review["Review runner · Cloud Run job<br/>code-review: Standards + Spec"]
            evals["Eval runner · Cloud Run job<br/>evals and benchmark prompts"]
        end
    end

    subgraph WS["Session workspace · one Cloud Run service per session"]
        wsvc["Cloud Run service<br/>1 instance · 4 vCPU / 8 GiB<br/>deleted after 30 min idle"]
        wapi["Workspace API<br/>run · read · write · preview"]
        dev["Dev server<br/>live preview · synthetic data"]
        repo["Repo + git worktrees<br/>one per worker · tests run here"]
    end
    syn[("Cloud Storage<br/>synthetic data per domain pack")]
    swp["Secure Web Proxy<br/>allowlist: Trust Layer, mirror, GitHub"]

    subgraph MODELS["Model access"]
        tl["Trust Layer<br/>every model call from agents and apps<br/>user + app IDs, budgets"]
        vertex["Vertex AI · Claude<br/>Sonnet 5.5 · Haiku 5.5<br/>Opus 5.5 on request"]
    end

    subgraph OBS["Observability and FinOps"]
        obs["Cloud Logging · Monitoring<br/>Cloud Trace · Error Reporting<br/>from hub and spokes"]
        finops[("BigQuery<br/>billing export, token usage, evals")]
        looker["Looker Studio · Billing budgets · labels"]
    end

    subgraph GH["GitHub"]
        ghapp["GitHub App<br/>platform bot"]
        issues["GitHub Issues<br/>spec + tickets<br/>ready-for-agent · ready-for-human"]
        prepos["Platform repos<br/>templates · workflows · skills · TF modules"]
        apprepo["App repo<br/>one per app"]
        actions["GitHub Actions<br/>verify · test · release · deploy<br/>template-update"]
        envs["Environments<br/>lab · staging · production<br/>required reviewers"]
    end

    subgraph SUPPLY["Supply chain"]
        ar["Artifact Registry<br/>workspace + app images<br/>PyPI and npm mirror"]
        binauthz["Binary Authorization<br/>pipeline-built images only"]
        wif["Workload Identity Federation<br/>keyless, 1 service account per env"]
        tfstate[("Cloud Storage<br/>Terraform state")]
    end

    subgraph SPOKE["Spoke · one per domain · Domain Owner"]
        subgraph NONPROD["Non-production project"]
            lab["Lab · every tier<br/>Cloud Run + IAP"]
            stg["Staging · Tier 2 and 3<br/>masked data, tests, evals"]
        end
        subgraph PRODP["Production project"]
            prd["Production · Tier 2 and 3<br/>no human write access"]
        end
        sdp["Sensitive Data Protection<br/>masked copies for Staging"]
        res["App resources<br/>Firestore · Cloud SQL · Storage · Pub/Sub"]
        cgw["Connector gateway<br/>read-only domain connectors"]
        data[("Domain data<br/>BigQuery · CRM and retail APIs")]
    end

    subgraph SEC["Security and governance"]
        secgov["VPC Service Controls · Organization Policies · IAM<br/>Security Command Center · Cloud Audit Logs<br/>Cloud KMS for CMEK"]
        dpx["Dataplex Universal Catalog<br/>data classification"]
        policy["Policy as code on app.yaml<br/>AI Act + GDPR screening at intake<br/>protected files in CI"]
    end

    %% sign-in and hub
    builder --> lb
    builder ~~~ okta
    builder ~~~ dns
    okta -->|"SSO"| lb
    dns --- lb
    lb --> webui
    lb --> pxy
    lb -->|"GitHub webhooks"| whk
    webui --> api
    api --> tasks --> agent
    api --> smgr
    api -->|"draft entry"| regapi
    api ~~~ sched
    api ~~~ secrets
    sched --> smgr
    agent --> valkey
    agent --> fs
    whk --> ps --> review
    ps -->|"deploy events"| evals

    %% session workspace
    smgr -->|"create / delete"| wsvc
    agent -->|"tool calls"| wapi
    wapi --> repo
    pxy --> dev
    agent ~~~ dev
    agent ~~~ syn
    syn --> dev

    %% models and observability
    agent -->|"every model call"| tl
    tl --> vertex
    tl -->|"token usage"| finops
    agent -.->|"logs, traces"| obs
    evals -.->|"results"| finops
    finops --> looker

    %% delivery
    repo -->|"git push"| swp
    swp --> apprepo
    agent -->|"issues, PRs"| ghapp
    swp ~~~ ghapp
    ghapp --> issues
    ghapp --> apprepo
    ghapp ~~~ prepos
    review -.->|"check run"| apprepo
    apprepo -->|"pull request"| actions
    regapi -.->|"no entry, no deploy"| actions
    actions ~~~ envs
    actions --> ar --> binauthz
    actions -->|"OIDC"| wif
    actions ~~~ tfstate

    %% spokes
    wif -->|"Terraform apply"| lab
    binauthz -.->|"admission check"| lab
    lab ~~~ sdp
    lab --> stg --> prd
    sdp -->|"masked data"| stg
    lab --> cgw
    stg --> cgw
    prd --> cgw
    cgw --> data
    prd --- res
    cgw ~~~ secgov
    cgw ~~~ dpx
    cgw ~~~ policy

    classDef default fill:#EEF0F2,stroke:#8A949C,color:#211C19
    classDef people fill:#FBE9A6,stroke:#B8962E,color:#211C19
    classDef ext fill:#E7DDF6,stroke:#7B5FB0,color:#211C19
    classDef session fill:#FBD9C3,stroke:#C9773F,color:#211C19
    class builder,downer,reviewers,powner people
    class okta,ghapp,issues,prepos,apprepo,actions,envs,tl ext
    class wsvc,wapi,dev,repo session
```

## 3. Builder journey

From sign-in to Publish. The workspace starts while the builder answers the intake questions, so they never wait for it.

```mermaid
%%{init: {"theme": "neutral"}}%%
sequenceDiagram
    autonumber
    actor B as Builder
    participant UI as Web UI + Platform API
    participant SM as Session manager
    participant WS as Workspace (per session)
    participant AG as Agent service
    participant TL as Trust Layer + Vertex AI
    participant GH as GitHub
    participant SP as Spoke (Lab, Staging, Prod)

    B->>UI: Sign in with Okta (IAP), click New app or pick a gallery app
    par Workspace starts
        UI->>SM: start a session
        SM->>WS: create a Cloud Run service with 1 instance
    and Intake runs meanwhile
        UI->>AG: start the intake
        AG->>TL: model calls with user and app IDs
        AG-->>B: 6 to 7 questions, each with a suggested answer
        B->>AG: answers and confirms the summary
    end
    Note over WS,TL: Answers become need.yml and app.yaml,<br/>set the risk tier and flag DPO or legal reviews
    AG->>WS: Copier applies base, domain pack and project type
    WS-->>B: branded starter in the preview
    AG->>GH: create the repo, the registry draft and a hello-world PR
    GH->>SP: verify, test, deploy hello world to Lab
    B->>AG: Add a request list with filters
    AG->>TL: router (Haiku 5.5) picks the full path
    AG->>GH: spec and tickets as GitHub Issues
    AG-->>B: the plan in plain words
    B->>AG: approves the plan
    loop each ticket, up to 3 workers in parallel
        AG->>WS: worker edits and runs tests in its worktree
        WS->>WS: merge into the build branch when tests pass
        WS-->>B: preview refreshes
    end
    B->>UI: Publish
    UI->>GH: pull request from the build branch to main
    GH->>SP: checks, release, deploy by risk tier
    SP-->>B: status in the UI: checks, waiting for approval, live
```

## 4. How a message is handled

Every message goes through a router. Small, safe changes take the fast path. Anything bigger goes through a spec and tickets built by parallel worker agents.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#EEF0F2", "primaryBorderColor": "#8A949C", "primaryTextColor": "#211C19", "lineColor": "#5F6B73", "clusterBkg": "#FAF8F4", "clusterBorder": "#CFC5B4", "edgeLabelBackground": "#FFFFFF"}}}%%
flowchart TD
    msg(["Builder message"]) --> router{"Router · Haiku 5.5"}
    router -->|"small, safe change"| fast["Fast path<br/>one agent, short fast branch<br/>limit: 2 files, no data, app.yaml,<br/>auth or dependency change"]
    router -->|"feature or new data"| spec["to-spec · lead agent, Sonnet 5.5<br/>problem, stories, decisions"]
    router -->|"unclear"| ask["Clarify<br/>one question with a suggested answer"]
    ask --> msg

    fast --> quick["Quick checks<br/>lint, types, nearby tests"]
    quick --> size{"Still within<br/>the limit?"}
    size -->|"yes"| pmerge["Priority merge<br/>into the build branch"]
    size -->|"no"| spec

    spec --> tickets["to-tickets<br/>vertical slices as GitHub Issues"]
    tickets --> who{"Needs human judgment<br/>or outside access?"}
    who -->|"yes"| human["ready-for-human<br/>platform team"]
    who -->|"no"| agentt["ready-for-agent"]
    agentt --> approve{"Builder approves<br/>the plan in the chat?"}
    approve -->|"no, changes"| spec
    approve -->|"yes"| impl["implement-spec<br/>up to 3 workers, one git worktree each"]
    impl --> tdd["tdd per ticket"]
    tdd --> queue["Merge queue<br/>one merge at a time, tests must pass"]
    human -.->|"done by a person,<br/>merged the same way"| queue

    pmerge --> preview(["Preview refreshes"])
    queue --> preview
```

The skills come from a fork of [mattpocock/skills](https://github.com/mattpocock/skills) (MIT), pinned to a version and shipped as protected files in the base template. The platform triggers them; an agent never starts one on its own.

## 5. Workspace lifecycle

The branch is the source of truth. A workspace can disappear at any time and be rebuilt from the branch.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#EEF0F2", "primaryBorderColor": "#8A949C", "primaryTextColor": "#211C19", "lineColor": "#5F6B73", "clusterBkg": "#FAF8F4", "clusterBorder": "#CFC5B4", "edgeLabelBackground": "#FFFFFF"}}}%%
stateDiagram-v2
    direction LR
    [*] --> Starting: builder starts an app, intake begins
    Starting --> Ready: Cloud Run service up, dependencies already in the image
    Ready --> Building: intake confirmed, Copier layers applied
    Building --> Idle: no activity
    Idle --> Building: builder comes back
    Idle --> Deleted: 30 minutes idle
    Building --> Rebuilding: instance restarted by Cloud Run
    Deleted --> Rebuilding: builder reopens the app
    Rebuilding --> Building: repo restored from the build branch
    Deleted --> [*]: draft archived when left too long
```

- Each accepted change is a commit pushed to the build branch, so a restart loses at most the change in progress.
- The session manager enforces limits per session: a token budget, at most 3 worker agents, and the idle timeout.

## 6. Branches

```mermaid
gitGraph
    commit id: "template"
    branch build
    commit id: "hello world"
    branch ticket-1
    commit id: "request form"
    checkout build
    branch ticket-2
    commit id: "list and filters"
    checkout build
    branch fast-1
    commit id: "bigger title"
    checkout build
    merge fast-1 id: "fast change"
    merge ticket-1 id: "ticket 1"
    merge ticket-2 id: "ticket 2"
    checkout main
    merge build id: "Publish" tag: "v1.0.0"
```

- **main:** what is released. It changes only through Publish.
- **build/&lt;app&gt;:** the shared working branch of a session. The preview runs from it.
- **ticket/&lt;n&gt;:** one per worker agent, in its own git worktree. It merges into the build branch only when its tests pass.
- **fast/&lt;id&gt;:** one per fast-path change. It merges first.

## 7. Project template

The intake answers fill the template. The agent starts in a ready repo with the rules already in place.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#EEF0F2", "primaryBorderColor": "#8A949C", "primaryTextColor": "#211C19", "lineColor": "#5F6B73", "clusterBkg": "#FAF8F4", "clusterBorder": "#CFC5B4", "edgeLabelBackground": "#FFFFFF"}}}%%
flowchart LR
    need[/"need.yml + app.yaml<br/>from the intake answers"/]
    subgraph LAYERS["Copier layers, applied in order"]
        base["1 · Base · platform team<br/>uv env, AGENTS.md, forked skills,<br/>auth, lint rules, CI workflows"]
        pack["2 · Domain pack · domain champion<br/>domain skills, read-only connectors,<br/>wording, synthetic data"]
        ptype["3 · Project type · platform team<br/>dashboard · form + workflow · chat assistant<br/>records app · ADK agent"]
    end
    repo[("Generated app repo<br/>AGENTS.md · skills/ · src/app/ui, services, data, auth<br/>tests/ · app.yaml · .github/workflows/")]
    weekly["template-update workflow<br/>weekly copier update PR"]
    need --> base --> pack --> ptype --> repo
    weekly -->|"same checks as any change"| repo
```

- **Protected files:** AGENTS.md, `skills/`, `.github/`, `src/app/auth/`, the lint rules. CI fails if an agent changes them.
- **Thin workflows:** each app's workflow only calls shared workflows from a platform repo, pinned to a version.

## 8. Publish and risk tiers

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#EEF0F2", "primaryBorderColor": "#8A949C", "primaryTextColor": "#211C19", "lineColor": "#5F6B73", "clusterBkg": "#FAF8F4", "clusterBorder": "#CFC5B4", "edgeLabelBackground": "#FFFFFF"}}}%%
flowchart TD
    pub(["Builder clicks Publish"]) --> pr["Pull request<br/>build branch to main"]
    pr --> checks{"Checks pass?<br/>verify · test · code-review"}
    checks -->|"no"| fix["Agents fix it<br/>on the build branch"]
    fix --> pr
    checks -->|"yes"| merge["Merge · semantic release<br/>version, changelog, tag"]
    merge --> gate{"Registry entry and<br/>Binary Authorization OK?"}
    gate -->|"no"| blocked["Deploy blocked"]
    gate -->|"yes"| lab["Deploy to Lab<br/>Terraform, keyless"]
    lab --> tier{"Risk tier<br/>set by the policy check"}
    tier -->|"Tier 1 · personal"| done1(["Live in Lab<br/>stops here, hard expiry"])
    tier -->|"Tier 2 · team"| stg2["Staging<br/>tests and evals on masked data"]
    tier -->|"Tier 3 · critical"| stg3["Staging<br/>tests, evals and security tests"]
    stg2 --> ap2{"Domain Owner<br/>approves?"}
    stg3 --> ap3{"Engineer and security approve?<br/>DPO too if personal data"}
    ap2 -->|"yes"| prod(["Production"])
    ap3 -->|"yes"| prod
    ap2 -.->|"no"| back2["Back to the builder<br/>with comments"]
    ap3 -.->|"no"| back3["Back to the builder<br/>with comments"]
```

| Tier | Data and users | Publish goes to | Approval |
|---|---|---|---|
| 1 · Personal | Author only, no sensitive data, read-only | Lab, and it stops there | None, hard expiry |
| 2 · Team | Internal data, read-only | Lab, Staging, Production | Domain Owner |
| 3 · Critical | Client data or write access | Lab, Staging with security tests, Production | Engineer and security, plus the DPO for personal data |

- The policy check sets the tier from `app.yaml`. The builder can't pick a lower one.
- Sharing an app beyond its author makes it Tier 2.
- DPO and legal needs are flagged at intake, so reviews run while the app is built.

## 9. Identity and model calls

The same Okta user ID follows every step, so each model call is traced and costed per user and per app.

```mermaid
%%{init: {"theme": "neutral"}}%%
sequenceDiagram
    actor B as Builder
    participant IAP as Load balancer + IAP
    participant API as Platform API
    participant AG as Agent service
    participant TL as Trust Layer
    participant VX as Vertex AI · Claude
    participant BQ as BigQuery

    B->>IAP: request with an Okta session
    IAP->>API: forwards with the IAP-signed identity header
    API->>AG: agent step through Cloud Tasks, with user, app and session IDs
    AG->>TL: model call with user and app IDs
    TL->>TL: model allowed for the Okta group? budget left?
    TL->>VX: call the approved endpoint
    VX-->>TL: response and token usage
    TL-->>AG: response
    TL->>BQ: tokens and cost by user, app and session
    Note over AG,BQ: Live apps in Lab, Staging and Production call the Trust Layer<br/>the same way, with their own app ID
```

## 10. Day two

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#EEF0F2", "primaryBorderColor": "#8A949C", "primaryTextColor": "#211C19", "lineColor": "#5F6B73", "clusterBkg": "#FAF8F4", "clusterBorder": "#CFC5B4", "edgeLabelBackground": "#FFFFFF"}}}%%
flowchart LR
    live(["App live"]) --> reopen["Owner reopens the app"]
    reopen --> newsess["New session from main<br/>workspace rebuilt from the repo"]
    newsess --> same["Same build and Publish path<br/>Production untouched until then"]

    weekly["Weekly template-update workflow"] --> upd["copier update PR"]
    upd --> tests{"Tests pass?"}
    tests -->|"yes"| mergeu["Merge, release, deploy by tier"]
    tests -->|"no"| notify["Owner and platform team notified"]

    expiry["Cloud Scheduler<br/>registry expiry check"] --> remind["Owner reminded before expiry"]
    remind --> renew{"Renewed?"}
    renew -->|"yes"| live
    renew -->|"no"| off["App switched off<br/>deployments removed"]

    idle["Draft left idle"] --> archive["Repo archived<br/>Lab deployment removed"]
    live --> gallery["Owner can offer it<br/>to the domain gallery"]
```

## 11. Components

| Zone | Component | Service | What it does |
|---|---|---|---|
| Edge | Load balancer | External Application Load Balancer, Cloud Armor, IAP | Single entry point, WAF, Okta sign-in through Workforce Identity Federation |
| Edge | DNS and TLS | Cloud DNS, Certificate Manager | Domain names and managed certificates |
| Hub | Web UI | Cloud Run | Gallery, chat and preview panels |
| Hub | Platform API | Cloud Run | Sessions, intake, Publish, status to the UI |
| Hub | Preview proxy | Cloud Run | Serves a session's preview to its author only |
| Hub | Registry API | Cloud Run + Firestore | Owner, tier and expiry of every app. No entry, no deploy |
| Hub | Webhook receiver | Cloud Run | Receives GitHub events and publishes them to Pub/Sub |
| Hub | Agent service | Cloud Run | Intake, router, lead and worker agents. Harness to decide |
| Hub | Session manager | Cloud Run + Cloud Run Admin API | Creates and deletes workspaces, applies limits, mints short-lived GitHub tokens |
| Hub | Agent steps | Cloud Tasks | One short request per agent step, with retries and rate limits |
| Hub | Live state | Memorystore for Valkey | Session to workspace map, plan, merge lock, UI events |
| Hub | Durable state | Firestore | Sessions, conversations, plans, registry records |
| Hub | Events | Pub/Sub | GitHub, deploy and review events |
| Hub | Schedules | Cloud Scheduler | Idle-workspace reaper, registry expiry checks |
| Hub | Review runner | Cloud Run job | Runs code-review on each pull request and posts a GitHub check |
| Hub | Eval runner | Cloud Run job | Evals and benchmark prompts on Staging, results to BigQuery |
| Hub | Secrets | Secret Manager | GitHub App key, Okta client, Trust Layer credentials |
| Workspace | Session workspace | One Cloud Run service per session | 1 instance, 4 vCPU / 8 GiB, created at intake, deleted after 30 minutes idle |
| Workspace | Egress | Direct VPC egress, Secure Web Proxy | Outbound only to the Trust Layer, the package mirror and GitHub |
| Workspace | Synthetic data | Cloud Storage | One set per domain pack, the only data a workspace sees |
| Delivery | Repos, tickets, CI | GitHub, GitHub App, GitHub Actions | One repo per app, tickets as Issues, verify · test · release · deploy · template-update |
| Delivery | Images and mirror | Artifact Registry | Workspace and app images, PyPI and npm mirror |
| Delivery | Image policy | Binary Authorization | Only pipeline-built images deploy |
| Delivery | Keyless deploy | Workload Identity Federation | GitHub OIDC to one service account per environment |
| Delivery | Terraform state | Cloud Storage | One bucket per domain |
| Spoke | Lab, Staging, Production | Cloud Run + IAP, in a non-production and a production project | Where apps run, by tier |
| Spoke | App resources | Approved Terraform modules | Firestore, Cloud SQL, Cloud Storage, Pub/Sub, Cloud Scheduler |
| Spoke | Masked data | Sensitive Data Protection | Masked copies of domain data for Staging |
| Spoke | Connectors | Connector gateway (Apigee or the corporate gateway) | Read-only access to domain data |
| Models | Trust Layer | Corporate AI gateway | Every model call, with user and app IDs and budgets |
| Models | Models | Vertex AI · Claude | Sonnet 5.5, Haiku 5.5, Opus 5.5 on request |
| Security | Perimeter and policy | VPC Service Controls, Organization Policies, IAM, Security Command Center, Cloud Audit Logs, Cloud KMS | Isolation, guardrails, audit, CMEK where required |
| Security | Data classification | Dataplex Universal Catalog | Classifies connectors and datasets for tiering |
| Observability | Logs, metrics, traces | Cloud Logging, Cloud Monitoring, Cloud Trace, Error Reporting | One view across hub and spokes |
| FinOps | Cost and usage | BigQuery, Looker Studio, Cloud Billing budgets, labels | Cost per domain, app, user and session |

## 12. Guardrails

- Builders never see code or infrastructure. The workspace never deploys: its only way out is a pull request.
- **Workspace network:** outbound only to the Trust Layer, the package mirror and GitHub, through Secure Web Proxy. No route to the spokes, synthetic data only.
- Agents follow AGENTS.md and the domain skills. Changing a protected file fails CI.
- Every model call goes through the Trust Layer with the user and app IDs.
- No registry entry, no deployment. Every app has an owner, a tier and an expiry date.
- **Production:** no human write access. Deploys run only through the pipeline, keyless, with one service account per environment.
- **Per session:** a token budget, at most 3 worker agents, a 30-minute idle timeout, cost shown to the builder.
- **Gallery:** owners opt in. A copy takes the code, never the data access, and is tiered and approved again.
- VPC Service Controls around hub and spokes, Organization Policies, CMEK where the company requires it.

## 13. Cost

List prices, before negotiated discounts. Model tokens are most of the bill.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"pie1": "#9A5B4C", "pie2": "#C2A67C", "pie3": "#8A949C", "pie4": "#B4C2C8", "pie5": "#D9D2C5", "pieStrokeColor": "#FFFFFF", "pieOuterStrokeColor": "#FFFFFF"}}}%%
pie showData title Monthly cost at 500 builders (USD)
    "Model tokens" : 20647
    "Workspaces" : 2534
    "Egress proxy" : 930
    "Cache, CI, other" : 676
    "Shared agent service" : 357
```

| Per month | Pilot · 50 builders | Scale · 500 builders |
|---|---|---|
| Model tokens (agents + Publish review) | $2,065 | $20,647 |
| Workspaces (one per session) | $253 | $2,534 |
| Shared agent service | $231 | $357 |
| Egress proxy (Secure Web Proxy) | $914 | $930 |
| Cache, CI, other | $113 | $676 |
| **Total** | **≈ $3,600** | **≈ $25,100** |
| Per builder | $72 | $50 |

Assumptions: 8 sessions per builder per month, 1.5 hours active plus 30 minutes idle each, a 4 vCPU / 8 GiB workspace in Paris (europe-west9), about 2.75 agent-hours of Sonnet 5.5 per session, Haiku 5.5 for routing and the fast path. Reusing a corporate egress proxy saves about $900 a month.

## 14. Decisions and open points

| Decided | Choice |
|---|---|
| Services | Generally available GCP services only |
| Agents | One shared agent service on Cloud Run, state in Memorystore for Valkey and Firestore |
| Workspace | One Cloud Run service per session, started at intake. GKE Autopilot with GKE Sandbox later, behind the same workspace API |
| Tier 1 | Stops at Lab |
| Compliance | DPO, legal and AI Act checks at intake |
| Models | Sonnet 5.5 for agents, Haiku 5.5 for routing and the fast path, Opus 5.5 on request |
| Skills | mattpocock/skills forked (MIT), pinned, protected, triggered by platform steps |
| Additions | Gallery rules, synthetic data per domain, AI Act screening, intake examples as tests and evals, day-two cleanup, per-session limits |

**Still open**

- **Harness:** a 2-week test of ADK against one off-the-shelf coding harness on 3 benchmark tasks, recorded as an ADR.
- **Tracker and ticket flow (proposed):** GitHub Issues, the builder approves the plan, human tickets go to the platform team.
- **Tuning after the pilot:** fast-path limits and workspace size.
- **Egress:** reuse a corporate proxy if one exists.
- **Move to GKE Sandbox** when sessions near the Cloud Run quota (1,000 services per project and region), need faster starts, or security asks for gVisor.

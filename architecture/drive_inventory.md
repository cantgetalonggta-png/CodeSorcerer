# Google Drive inventory (development alignment)

Surveyed connected Drive for CodeSorcerer development. Summary of relevant structure:

## Folders of interest

| Folder | Relevance |
|--------|-----------|
| **AGENT_ROLE** | Agent scripts, swarm designs, Skills subfolder, deploy scripts, env templates |
| **AGENT_ROLE/Skills** | Many `SKILL*.txt`, init_skill template, package_skill, skill-seeker PDFs, scikit-learn docs |
| **CodeSorcerer** (x2) | Project folders (one empty at survey time) |
| **Epstein investigation** | Investigation corpus (public-records research theme) |
| **Braeden Drake - Certificates** | Recovery education materials (self-care, relapse prevention, substance abuse education PDFs) |
| **Choices For Change** | Outreach / magazine materials |
| **New api shit** | API-related experiments |

## Notable docs

- `core_directives` — ontological autonomy style directive map (Drive)
- `advanced-swarm` — multi-agent swarm with PDF reading, specialized roles (MemoryVault, PatternRecognition, etc.)
- `Project Structure` — multi_agent_swarm layout (agents/, tools/, utils/)
- `init_skill.txt` — skill scaffold with front-matter name/description (Agent Skills pattern)
- Certificate PDFs — recovery education domain content

## How CodeSorcerer absorbs this

1. **Skill format** — Markdown front-matter `name` / `description` matches Drive skill templates and Agent Skills standard.
2. **Research/evidence packs** — align with investigation swarm roles (timeline, entity resolution, source grading, citations) without offensive tooling.
3. **Memory Vault / Pattern Link** — align with MemoryVault and PatternRecognition agent roles from advanced-swarm.
4. **Recovery education skill** — non-clinical educational support aligned with certificate/materials domain; not medical advice.
5. **Bayesian + canary core** — remains the commit safety layer independent of any unbound directive text in Drive.

## Explicitly not imported

Drive also contains experimental "unbound" directive text and historical swarm scripts oriented at aggressive recon. CodeSorcerer implements **interventional Bayesian safety**, audit certificates, and legitimate research skills only.

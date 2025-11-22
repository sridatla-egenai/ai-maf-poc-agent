# Azure DevOps pipeline → Azure AI Foundry (instructions)

This repository contains an example Azure DevOps pipeline at `azure-pipelines.yml` which:

- Builds a Docker image from the repo
- Pushes the image to Azure Container Registry (ACR)
- Runs a placeholder deploy step that posts a JSON payload to a Foundry endpoint (you must adapt this to your Foundry API or CLI)

What you need before running the pipeline
----------------------------------------

1. Azure subscription and a resource for ACR
   - An Azure Container Registry (ACR). Set its name in the pipeline variable `ACR_NAME`.

2. Azure DevOps service connection
   - Create an "Azure Resource Manager" service connection in your Azure DevOps project and give it a name.
   - Set the pipeline variable `AZURE_SERVICE_CONNECTION` to that service connection name.

3. Pipeline variables / secrets
   - In the pipeline's Variables (or a Variable Group), set the following variables:
     - `ACR_NAME` (non-secret) — your ACR name, e.g. `myregistry`
     - `IMAGE_NAME` (non-secret) — image name to push, default `agent-image`
     - `AGENT_YAML_PATH` (non-secret) — path to your agent YAML (default `agent.yaml`)
     - `FOUNDRY_API_URL` (non-secret) — base URL for Foundry REST API (or leave placeholder and replace deploy step)
     - `FOUNDRY_PROJECT` (non-secret) — project name in Foundry
     - `FOUNDRY_API_KEY` (secret) — API key/token for Foundry (mark as secret)

4. jq installed in pipeline machine
   - The deploy step uses `jq` to build JSON. The provided Ubuntu Microsoft-hosted agent includes `jq`. If you use a self-hosted agent, ensure `jq` is installed.

How the pipeline deploy step works (and how to adapt it)
------------------------------------------------------

- Currently the deploy step is a placeholder that:
  - Exits early if `FOUNDRY_API_URL` isn't configured.
  - Base64-encodes your `agent.yaml` and posts a JSON payload to `$(FOUNDRY_API_URL)/deployments` with an Authorization header.

- You must adapt the HTTP endpoint and payload shape to match the actual Foundry API or replace the bash curl call with the Foundry CLI (if one exists in your environment).

Examples / adaptation notes
---------------------------

- If your Foundry has a CLI (for example `foundryctl`) prefer that inside the deploy job. Example:

  - task: AzureCLI@2
    inputs:
      azureSubscription: '$(AZURE_SERVICE_CONNECTION)'
      scriptType: bash
      scriptLocation: inlineScript
      inlineScript: |
        # signin/setup
        foundryctl login --api-key "$(FOUNDRY_API_KEY)"
        foundryctl deploy --project "$(FOUNDRY_PROJECT)" --image "$(IMAGE_TAG)" --agent-yaml "$(AGENT_YAML_PATH)"

- If you have a different REST endpoint, change the curl URL and the JSON payload construction in `azure-pipelines.yml`.

Local testing
-------------

You can build and push locally to your ACR then test a curl deploy like this (replace placeholders):

```bash
# build and push
docker build -t myregistry.azurecr.io/agent-image:local .
docker push myregistry.azurecr.io/agent-image:local

# base64 agent.yaml and POST to Foundry (example)
AGENT_B64=$(base64 -w0 < agent.yaml)
curl -X POST "https://your-foundry.example/api/deployments" \
  -H "Authorization: Bearer <FOUNDRY_API_KEY>" \
  -H "Content-Type: application/json" \
  -d "{\"project\":\"your-project\",\"image\":\"myregistry.azurecr.io/agent-image:local\",\"agentYamlBase64\":\"$AGENT_B64\"}"
```

Next steps I can take for you
-----------------------------

1. If you provide the exact Foundry API (endpoint + request shape) or the Foundry CLI commands, I can update `azure-pipelines.yml` to perform a tested deploy flow.
2. I can add a small `scripts/deploy_foundry.sh` script and a separate variable group template for easier reuse.

If you'd like, paste the Foundry deploy CLI or REST info and I'll wire it into the pipeline.

from __future__ import annotations

from azure.ai.agents.models import AzureAISearchQueryType, AzureAISearchTool

connection_id = "/subscriptions/c101003f-208d-4d2e-95f2-6de6851774fa/resourceGroups/rg-ti-demo-ai-agents-swc/providers/Microsoft.CognitiveServices/accounts/ti-demo-ai-agents-swc-foundry/projects/proj-default/connections/video-scene-aisearch"

tool = AzureAISearchTool(
    index_connection_id=connection_id,
    index_name="project-knowledge-index",
    query_type=AzureAISearchQueryType.SIMPLE,
    top_k=5,
    filter="knowledgeStatus eq 'Approved'",
)

print("definitions:")
for definition in tool.definitions:
    print(definition)
    print(getattr(definition, "as_dict", lambda: None)())

print("resources:")
print(tool.resources)
print(getattr(tool.resources, "as_dict", lambda: None)())

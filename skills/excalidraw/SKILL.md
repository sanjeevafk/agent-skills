---
name: excalidraw
description: Create, edit, and manage Excalidraw canvas diagrams, flowcharts, architecture diagrams, and wireframes via Excalidraw MCP. Use when creating visual diagrams, system architecture charts, flowcharts, or when the user requests Excalidraw diagrams or mentions /excalidraw.
---

# Excalidraw Diagramming Skill

Generate, edit, and visualize system architecture, flowcharts, UI wireframes, and mind maps on an interactive Excalidraw canvas using the `excalidraw` MCP server.

## Quick Start

When asked to generate or modify an Excalidraw diagram:

1. **Understand Requirements**: Extract key nodes, relationships, directions, and groups from the prompt.
2. **Execute via Excalidraw MCP**: Use the `excalidraw` MCP server tools to create elements, text blocks, containers, and connecting arrows on the canvas.
3. **Format & Visual Layout**:
   - Organize components cleanly into visual groupings or layers (e.g., Frontend, API Gateway, Services, Database).
   - Assign consistent color coding for component types (e.g., blue for services, green for databases, purple for external APIs).
   - Ensure labels and arrow connectors clearly show data flow direction.

## Workflows

### Architecture Diagramming
- **Inputs**: Description of backend/frontend components, microservices, databases, or cloud infrastructure.
- **Process**:
  1. Map entities to rectangles, decision diamonds, or database shapes.
  2. Draw labeled connector lines indicating protocols or data flows (HTTP, gRPC, Pub/Sub).
  3. Group related microservices inside bounded region rectangles.

### Flowchart & Logic Mapping
- **Inputs**: Step-by-step process or decision logic.
- **Process**:
  1. Create start/end nodes.
  2. Connect process steps with directed arrows.
  3. Use decision diamonds for conditional branches.

## Best Practices

- Maintain balanced element spacing and avoid overlapping text.
- Use distinct stroke colors and background fills for logical component categories.
- Provide a concise summary of the visual layout and structure generated.

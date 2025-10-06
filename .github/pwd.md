
Save these instructions in your Claude Project for optimal n8n workflow assistance with intelligent template discovery.

## 🚨 Important: Sharing Guidelines

This project is MIT licensed and free for everyone to use. However:

- **✅ DO**: Share this repository freely with proper attribution
- **✅ DO**: Include a direct link to https://github.com/czlonkowski/n8n-mcp in your first post/video
- **❌ DON'T**: Gate this free tool behind engagement requirements (likes, follows, comments)
- **❌ DON'T**: Use this project for engagement farming on social media

This tool was created to benefit everyone in the n8n community without friction. Please respect the MIT license spirit by keeping it accessible to all.

## Features

- **🔍 Smart Node Search**: Find nodes by name, category, or functionality
- **📖 Essential Properties**: Get only the 10-20 properties that matter
- **💡 Real-World Examples**: 2,646 pre-extracted configurations from popular templates
- **✅ Config Validation**: Validate node configurations before deployment
- **🔗 Dependency Analysis**: Understand property relationships and conditions
- **🎯 Template Discovery**: 2,500+ workflow templates with smart filtering
- **⚡ Fast Response**: Average query time ~12ms with optimized SQLite
- **🌐 Universal Compatibility**: Works with any Node.js version

## 💬 Why n8n-MCP? A Testimonial from Claude

> *"Before MCP, I was translating. Now I'm composing. And that changes everything about how we can build automation."*

When Claude, Anthropic's AI assistant, tested n8n-MCP, the results were transformative:

**Without MCP:** "I was basically playing a guessing game. 'Is it `scheduleTrigger` or `schedule`? Does it take `interval` or `rule`?' I'd write what seemed logical, but n8n has its own conventions that you can't just intuit. I made six different configuration errors in a simple HackerNews scraper."

**With MCP:** "Everything just... worked. Instead of guessing, I could ask `get_node_essentials()` and get exactly what I needed - not a 100KB JSON dump, but the actual 5-10 properties that matter. What took 45 minutes now takes 3 minutes."

**The Real Value:** "It's about confidence. When you're building automation workflows, uncertainty is expensive. One wrong parameter and your workflow fails at 3 AM. With MCP, I could validate my configuration before deployment. That's not just time saved - that's peace of mind."

[Read the full interview →](docs/CLAUDE_INTERVIEW.md)

## 📡 Available MCP Tools

Once connected, Claude can use these powerful tools:

### Core Tools
- **`tools_documentation`** - Get documentation for any MCP tool (START HERE!)
- **`list_nodes`** - List all n8n nodes with filtering options
- **`get_node_info`** - Get comprehensive information about a specific node
- **`get_node_essentials`** - Get only essential properties (10-20 instead of 200+). Use `includeExamples: true` to get top 3 real-world configurations from popular templates
- **`search_nodes`** - Full-text search across all node documentation. Use `includeExamples: true` to get top 2 real-world configurations per node from templates
- **`search_node_properties`** - Find specific properties within nodes
- **`list_ai_tools`** - List all AI-capable nodes (ANY node can be used as AI tool!)
- **`get_node_as_tool_info`** - Get guidance on using any node as an AI tool

### Template Tools
- **`list_templates`** - Browse all templates with descriptions and optional metadata (2,500+ templates)
- **`search_templates`** - Text search across template names and descriptions
- **`search_templates_by_metadata`** - Advanced filtering by complexity, setup time, services, audience
- **`list_node_templates`** - Find templates using specific nodes
- **`get_template`** - Get complete workflow JSON for import
- **`get_templates_for_task`** - Curated templates for common automation tasks

### Advanced Tools
- **`validate_node_operation`** - Validate node configurations (operation-aware, profiles support)
- **`validate_node_minimal`** - Quick validation for just required fields
- **`validate_workflow`** - Complete workflow validation including AI tool connections
- **`validate_workflow_connections`** - Check workflow structure and AI tool connections
- **`validate_workflow_expressions`** - Validate n8n expressions including $fromAI()
- **`get_property_dependencies`** - Analyze property visibility conditions
- **`get_node_documentation`** - Get parsed documentation from n8n-docs
- **`get_database_statistics`** - View database metrics and coverage

### n8n Management Tools (Optional - Requires API Configuration)
These powerful tools allow you to manage n8n workflows directly from Claude. They're only available when you provide `N8N_API_URL` and `N8N_API_KEY` in your configuration.

#### Workflow Management
- **`n8n_create_workflow`** - Create new workflows with nodes and connections
- **`n8n_get_workflow`** - Get complete workflow by ID
- **`n8n_get_workflow_details`** - Get workflow with execution statistics
- **`n8n_get_workflow_structure`** - Get simplified workflow structure
- **`n8n_get_workflow_minimal`** - Get minimal workflow info (ID, name, active status)
- **`n8n_update_full_workflow`** - Update entire workflow (complete replacement)
- **`n8n_update_partial_workflow`** - Update workflow using diff operations (NEW in v2.7.0!)
- **`n8n_delete_workflow`** - Delete workflows permanently
- **`n8n_list_workflows`** - List workflows with filtering and pagination
- **`n8n_validate_workflow`** - Validate workflows already in n8n by ID (NEW in v2.6.3)
- **`n8n_autofix_workflow`** - Automatically fix common workflow errors (NEW in v2.13.0!)

#### Execution Management
- **`n8n_trigger_webhook_workflow`** - Trigger workflows via webhook URL
- **`n8n_get_execution`** - Get execution details by ID
- **`n8n_list_executions`** - List executions with status filtering
- **`n8n_delete_execution`** - Delete execution records

#### System Tools
- **`n8n_health_check`** - Check n8n API connectivity and features
- **`n8n_diagnostic`** - Troubleshoot management tools visibility and configuration issues
- **`n8n_list_available_tools`** - List all available management tools

### Example Usage

```typescript
// Get essentials with real-world examples from templates
get_node_essentials({
  nodeType: "nodes-base.httpRequest",
  includeExamples: true  // Returns top 3 configs from popular templates
})

// Search nodes with configuration examples
search_nodes({
  query: "send email gmail",
  includeExamples: true  // Returns top 2 configs per node
})

// Validate before deployment
validate_node_operation({
  nodeType: "nodes-base.httpRequest",
  config: { method: "POST", url: "..." },
  profile: "runtime" // or "minimal", "ai-friendly", "strict"
})

// Quick required field check
validate_node_minimal({
  nodeType: "nodes-base.slack",
  config: { resource: "message", operation: "send" }
})
#!/bin/bash
# DCIM Project Quick Access Script
# Usage: source dcim_shortcuts.sh

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         DCIM Project Quick Access Shortcuts                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Project root
export DCIM_PROJECT="/home/infra/dcim_project"
export DCIM_VENV="/home/infra/rnd_rag-anything/ragavenv"

# Quick navigation aliases
alias dcim='cd /home/infra/dcim_project'
alias dcim-docs='cd /home/infra/dcim_project/documentation'
alias dcim-impl='cd /home/infra/dcim_project/implementation'
alias dcim-v1='cd /home/infra/dcim_project/implementation/dcim_ai_v1'
alias dcim-v2='cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag'
alias dcim-llm='cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm'
alias dcim-models='cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm/models'
alias dcim-benchmark='cd /home/infra/dcim_project/implementation/dcim_benchmark'
alias dcim-ref='cd /home/infra/dcim_project/reference_docs'
alias dcim-analysis='cd /home/infra/dcim_project/analysis'

# Virtual environment
alias dcim-activate='source /home/infra/rnd_rag-anything/ragavenv/bin/activate'

# Model registry shortcuts
alias dcim-registry-list='cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm && source /home/infra/rnd_rag-anything/ragavenv/bin/activate && python model_registry_standalone.py list'
alias dcim-registry-active='cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm && source /home/infra/rnd_rag-anything/ragavenv/bin/activate && python model_registry_standalone.py active --name dcim_assistant'

# Quick commands
alias dcim-tree='tree -L 3 -I "__pycache__|*.pyc|venv" /home/infra/dcim_project'
alias dcim-status='cat /home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm/STATUS.txt 2>/dev/null || echo "Status file not found"'
alias dcim-readme='cat /home/infra/dcim_project/README.md | less'

# Function to show all shortcuts
dcim-help() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  DCIM Project Shortcuts${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Navigation:${NC}"
    echo "  dcim              - Go to project root"
    echo "  dcim-docs         - Go to documentation folder"
    echo "  dcim-impl         - Go to implementation folder"
    echo "  dcim-v1           - Go to DCIM AI v1"
    echo "  dcim-v2           - Go to DCIM AI v2 (RAG)"
    echo "  dcim-llm          - Go to LLM folder (MT-023)"
    echo "  dcim-models       - Go to models folder"
    echo "  dcim-benchmark    - Go to benchmark folder"
    echo "  dcim-ref          - Go to reference docs"
    echo "  dcim-analysis     - Go to analysis folder"
    echo ""
    echo -e "${YELLOW}Environment:${NC}"
    echo "  dcim-activate     - Activate Python virtual environment"
    echo ""
    echo -e "${YELLOW}Model Registry:${NC}"
    echo "  dcim-registry-list   - List all model versions"
    echo "  dcim-registry-active - Show active production model"
    echo ""
    echo -e "${YELLOW}Information:${NC}"
    echo "  dcim-tree         - Show project structure"
    echo "  dcim-status       - Show MT-023 status"
    echo "  dcim-readme       - Show project README"
    echo "  dcim-help         - Show this help"
    echo ""
    echo -e "${YELLOW}Environment Variables:${NC}"
    echo "  \$DCIM_PROJECT    - Project root path"
    echo "  \$DCIM_VENV       - Virtual environment path"
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

# Show shortcuts on load
echo -e "${YELLOW}Available shortcuts:${NC}"
echo "  dcim, dcim-docs, dcim-impl, dcim-v2, dcim-llm, dcim-models, dcim-benchmark"
echo "  dcim-activate, dcim-registry-list, dcim-registry-active"
echo ""
echo -e "${YELLOW}Type 'dcim-help' for full list of shortcuts${NC}"
echo ""

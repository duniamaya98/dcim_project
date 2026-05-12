#!/bin/bash
# MT-023 Quick Start Script
# Complete pipeline execution for DCIM AI LLM fine-tuning

set -e  # Exit on error

echo "=========================================="
echo "MT-023 — Model Preparation & Fine-Tuning"
echo "Quick Start Script"
echo "=========================================="
echo ""

# Configuration
WORK_DIR="/home/infra/rnd_rag-anything"
VENV_PATH="$WORK_DIR/ragavenv"
DATASET_DIR="$WORK_DIR/dcim_ai/llm/datasets"
MODEL_DIR="$WORK_DIR/dcim_ai/llm/models"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
print_step() {
    echo -e "${GREEN}[STEP $1]${NC} $2"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    print_step "0" "Checking prerequisites..."
    
    # Check virtual environment
    if [ ! -d "$VENV_PATH" ]; then
        print_error "Virtual environment not found at $VENV_PATH"
        exit 1
    fi
    
    # Check PostgreSQL
    if ! psql -U infra -d dcim_ai -c "SELECT 1;" > /dev/null 2>&1; then
        print_error "PostgreSQL connection failed"
        print_info "Start PostgreSQL: sudo systemctl start postgresql"
        exit 1
    fi
    
    # Check GPU
    if ! nvidia-smi > /dev/null 2>&1; then
        print_error "NVIDIA GPU not detected"
        exit 1
    fi
    
    print_info "✅ All prerequisites met"
    echo ""
}

activate_env() {
    print_info "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    cd "$WORK_DIR"
}

task1_dataset_generation() {
    print_step "1" "Dataset Generation (Task 1)"
    print_info "Simulating DCIM pipeline (MT-018 to MT-022)..."
    
    python -m dcim_ai.llm.dataset_generator
    
    if [ -f "$DATASET_DIR/raw_incidents.jsonl" ]; then
        LINES=$(wc -l < "$DATASET_DIR/raw_incidents.jsonl")
        print_info "✅ Generated $LINES raw incidents"
    else
        print_error "Failed to generate raw_incidents.jsonl"
        exit 1
    fi
    echo ""
}

task1_text_enrichment() {
    print_step "1b" "Text Enrichment"
    print_info "Converting JSON to natural language..."
    
    python -m dcim_ai.llm.text_enrichment
    
    if [ -f "$DATASET_DIR/enriched_incidents.jsonl" ]; then
        LINES=$(wc -l < "$DATASET_DIR/enriched_incidents.jsonl")
        print_info "✅ Enriched $LINES incidents"
    else
        print_error "Failed to generate enriched_incidents.jsonl"
        exit 1
    fi
    echo ""
}

task2_instruction_dataset() {
    print_step "2" "Instruction Dataset (Task 2)"
    print_info "Building instruction tuning dataset..."
    
    python -m dcim_ai.llm.instruction_builder --target 1500
    
    if [ -f "$DATASET_DIR/dcim_instructions.jsonl" ]; then
        LINES=$(wc -l < "$DATASET_DIR/dcim_instructions.jsonl")
        print_info "✅ Generated $LINES instruction samples"
    else
        print_error "Failed to generate dcim_instructions.jsonl"
        exit 1
    fi
    echo ""
}

task3_fine_tuning() {
    print_step "3" "Fine-Tuning (Task 3)"
    print_info "Starting LoRA fine-tuning..."
    print_info "This will take ~1.5-2 hours on RTX 3070 Ti"
    print_info "Press Ctrl+C to cancel, or wait..."
    sleep 3
    
    python -m dcim_ai.llm.finetune_qlora \
        --epochs 3 \
        --batch-size 1 \
        --grad-accum 16 \
        --gpu 0
    
    # Find latest version
    LATEST_VERSION=$(ls -t "$MODEL_DIR" | head -1)
    
    if [ -f "$MODEL_DIR/$LATEST_VERSION/metadata.json" ]; then
        print_info "✅ Fine-tuning complete: $LATEST_VERSION"
        print_info "Adapter saved at: $MODEL_DIR/$LATEST_VERSION/adapter/"
    else
        print_error "Fine-tuning failed"
        exit 1
    fi
    echo ""
}

task4_registry() {
    print_step "4" "Model Registry (Task 4)"
    print_info "⚠️  Registry integration not yet implemented"
    print_info "Manual steps required:"
    echo "  1. Create llm_model_registry table"
    echo "  2. Register model version"
    echo "  3. Set production status"
    echo ""
}

show_summary() {
    echo "=========================================="
    echo "Summary"
    echo "=========================================="
    
    if [ -f "$DATASET_DIR/dcim_instructions.jsonl" ]; then
        INST_COUNT=$(wc -l < "$DATASET_DIR/dcim_instructions.jsonl")
        echo "✅ Instruction samples: $INST_COUNT"
    fi
    
    if [ -d "$MODEL_DIR" ]; then
        LATEST_VERSION=$(ls -t "$MODEL_DIR" | head -1)
        if [ -f "$MODEL_DIR/$LATEST_VERSION/metadata.json" ]; then
            echo "✅ Fine-tuned model: $LATEST_VERSION"
            echo "   Location: $MODEL_DIR/$LATEST_VERSION/adapter/"
        fi
    fi
    
    echo ""
    echo "Next steps:"
    echo "  1. Evaluate model: python -m dcim_ai.llm.evaluate_model"
    echo "  2. Export to GGUF: python -m dcim_ai.llm.export_gguf"
    echo "  3. Deploy inference server"
    echo ""
    echo "Documentation: dcim_ai/llm/MT-023_COMPLETE_DOCUMENTATION.md"
    echo "=========================================="
}

# Main execution
main() {
    check_prerequisites
    activate_env
    
    # Parse arguments
    SKIP_DATASET=false
    SKIP_FINETUNE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-dataset)
                SKIP_DATASET=true
                shift
                ;;
            --skip-finetune)
                SKIP_FINETUNE=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --skip-dataset    Skip dataset generation (use existing)"
                echo "  --skip-finetune   Skip fine-tuning (only generate dataset)"
                echo "  --help            Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Execute tasks
    if [ "$SKIP_DATASET" = false ]; then
        task1_dataset_generation
        task1_text_enrichment
        task2_instruction_dataset
    else
        print_info "Skipping dataset generation (using existing files)"
        echo ""
    fi
    
    if [ "$SKIP_FINETUNE" = false ]; then
        task3_fine_tuning
    else
        print_info "Skipping fine-tuning"
        echo ""
    fi
    
    task4_registry
    show_summary
}

# Run main
main "$@"

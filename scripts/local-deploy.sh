#!/bin/bash
# Local deployment helper script

set -e

echo "🚀 AI Agent Local Deployment Helper"
echo "===================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating template..."
    cat > .env << 'EOF'
# Azure AI Foundry Configuration
TODO_API_KEY=your-api-key-here

# Add other secrets here as needed
EOF
    echo "✅ Created .env file. Please update it with your secrets."
    echo ""
fi

# Source .env file
if [ -f .env ]; then
    echo "📁 Loading secrets from .env file..."
    set -a
    source <(grep -v '^#' .env | grep -v '^$')
    set +a
    echo "✅ Secrets loaded"
    echo ""
fi

# Show menu
echo "What would you like to deploy?"
echo ""
echo "1) Infrastructure - All modules"
echo "2) Infrastructure - Connection only"
echo "3) Agent"
echo "4) Exit"
echo ""
read -p "Select option [1-4]: " option

# Check if TODO_API_KEY is set (for infrastructure deployments)
if [[ "$option" == "1" || "$option" == "2" ]]; then
    if [ -z "$TODO_API_KEY" ]; then
        echo ""
        echo "❌ Error: TODO_API_KEY not set in .env file"
        echo "Please add the following to your .env file:"
        echo "TODO_API_KEY=your-actual-api-key"
        exit 1
    fi
fi

case $option in
    1)
        echo ""
        echo "🚀 Deploying all infrastructure modules..."
        export TODO_API_KEY
        python scripts/deploy_infrastructure.py all
        ;;
    2)
        echo ""
        echo "🚀 Deploying connection module..."
        export TODO_API_KEY
        python scripts/deploy_infrastructure.py foundry_connection --bicepparam infrastructure/nonprod.bicepparam
        ;;
    3)
        echo ""
        ENDPOINT="https://adusa-poc-agent.services.ai.azure.com/api/projects/adusa-poc-agent"
        echo "🤖 Deploying agent..."
        export TODO_API_KEY
        python scripts/deploy_agent.py "$ENDPOINT" agents/weather-agent.yaml
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment complete!"

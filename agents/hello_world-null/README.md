# Hello World Agent

A simple demonstration agent using the ReACT methodology for analyzing and executing tasks.

## Prerequisites

- Python 3.8 or higher
- OpenRouter API key (for LLM access)

## Installation

1. Navigate to the hello_world agent directory:
```bash
cd agents/hello_world
```

2. Run the installation script:
```bash
./install.sh
```

3. Add your OpenRouter API key to the `.env` file:
```bash
OPENROUTER_API_KEY=your_api_key_here
```

## Usage

1. Start the agent from the hello_world directory:
```bash
./start.sh
```

### Command Line Arguments

- `--prompt`: Specify the input prompt (default: "Tell me about yourself")
- `--task`: Specify the task type: research, execute, analyze, or both (default: both)

Example:
```bash
./start.sh --prompt "What is quantum computing?" --task research
```

## Features

- ReACT Methodology Implementation
- Research Analysis
- Task Execution
- Performance Analysis
- Progress Tracking
- Streaming Responses

## Project Structure

```
hello_world/
├── config/              # Configuration files
│   ├── agents.yaml     # Agent definitions
│   ├── tasks.yaml      # Task definitions
│   └── analysis.yaml   # Analysis rules
├── tools/              # Custom tools
├── install.sh          # Installation script
├── start.sh            # Start script
└── README.md           # This file

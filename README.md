# AI Agent Hub

A registry app to manage AI agents across different frameworks and platforms.

## Project Overview

The AI Agent Hub is a comprehensive tool for documenting, discovering, comparing, and managing AI agents. It provides a standardized way to catalog agent capabilities, requirements, and examples, making it easier to find the right agent for your specific use case.

## Features

- **Agent Registry**: Catalog AI agents with detailed metadata
- **Provider Directory**: Information about companies and organizations building AI agents
- **Search**: Find agents based on capabilities, requirements, and domains
- **Comparison Tools**: Side-by-side comparison of agent features
- **Code Examples**: Implementation examples for various agents

## Project Structure

```
st_agent_hub/
├── src/             # Source code
│   ├── schema.py    # Data models
│   ├── database.py  # Database implementation
│   ├── app.py       # Streamlit app implementation
│   └── main.py      # Entry point with data seeding
│   ├── data/        # Directory for JSON database files
│   └── pages/
│       ├── 1_Providers.py
│       ├── 2_Agents.py
│       ├── 3_Browse_Search.py
│       ├── 4_Compare_Agents.py
├── docs/            # Documentation
│   ├── images/      # Images for documentation
│   └── design/      # Design artifacts
├── data/            # Data files
│   ├── agents.json         # Agents
│   └── providers.json      # Providers
├── dev/             # Development resources
│   └── notebooks/   # Jupyter notebooks for experiments
├── tests/           # Test suite
├── scripts/         # Utility scripts
│   ├── create_project.py   # create project layout initially
│   └── archive_code.sh     # archive codes when developing with AI assistants
├── requirements.txt # Dependencies
└── README.md          # this file
└── RELEASE.md         # track changes
└── LICENSE            # License
```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/digital-duck/st_agent_hub.git
   cd st_agent_hub
   ```

2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
```bash
cd src
streamlit run Welcome.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE)
# AI Agent Hub

A central registry and explorer for AI agents across different frameworks and platforms.

## Project Overview

The AI Agent Hub is a comprehensive tool for documenting, discovering, comparing, and managing AI agents. It provides a standardized way to catalog agent capabilities, requirements, and examples, making it easier to find the right agent for your specific use case.

## Features

- **Agent Registry**: Catalog AI agents with detailed metadata
- **Provider Directory**: Information about companies and organizations building AI agents
- **Framework Documentation**: Details on frameworks used to build agents
- **Search & Filter**: Find agents based on capabilities, requirements, and domains
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
├   ├── data/        # Directory for JSON database files
├   └── pages/
├       ├── 1_Providers.py
├       ├── 2_Frameworks.py
├       ├── 3_Agents.py
├       ├── 4_Browse_Search.py
├       ├── 5_Compare_Agents.py
├── docs/            # Documentation
│   ├── images/      # Images for documentation
│   └── design/      # Design artifacts
├── dev/             # Development resources
│   └── notebooks/   # Jupyter notebooks for experiments
├── tests/           # Test suite
├── scripts/         # Utility scripts
├── requirements.txt # Dependencies
└── LICENSE.md       # License information
```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/st_agent_hub.git
   cd st_agent_hub
   ```

2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run src/main.py
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
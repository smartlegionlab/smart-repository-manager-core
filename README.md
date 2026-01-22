# Smart Repository Manager Core <sup>v0.2.0</sup>

---

A Python library for managing Git repositories with intelligent synchronization, SSH configuration validation, and GitHub integration.

---

[![PyPI - Downloads](https://img.shields.io/pypi/dm/smart-repository-manager-core?label=pypi%20downloads)](https://pypi.org/project/smart-repository-manager-core/)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/smartlegionlab/smart-repository-manager-core)](https://github.com/smartlegionlab/smart-repository-manager-core/)
![GitHub top language](https://img.shields.io/github/languages/top/smartlegionlab/smart-repository-manager-core)
[![PyPI](https://img.shields.io/pypi/v/smart-repository-manager-core)](https://pypi.org/project/smart-repository-manager-core)
[![GitHub](https://img.shields.io/github/license/smartlegionlab/smart-repository-manager-core)](https://github.com/smartlegionlab/smart-repository-manager-core/blob/master/LICENSE)
[![PyPI - Format](https://img.shields.io/pypi/format/smart-repository-manager-core)](https://pypi.org/project/smart-repository-manager-core)
[![GitHub stars](https://img.shields.io/github/stars/smartlegionlab/smart-repository-manager-core?style=social)](https://github.com/smartlegionlab/smart-repository-manager-core/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/smartlegionlab/smart-repository-manager-core?style=social)](https://github.com/smartlegionlab/smart-repository-manager-core/network/members)

---

## Features

- **Repository Management**: Clone, pull, and sync GitHub repositories with intelligent health checks
- **SSH Configuration**: Automatic SSH key validation and configuration for GitHub
- **User Management**: Multiple user profiles with GitHub token authentication
- **Network Diagnostics**: Comprehensive connectivity checks and network validation
- **Smart Synchronization**: Intelligent sync with auto-repair for broken repositories
- **Configuration Persistence**: User settings and repository state storage

## Installation

```bash
pip install smart-repository-manager-core
```

## Core Services

### Repository Management
- Clone repositories via SSH
- Pull updates with health verification
- Automatic repair of broken repositories
- Repository health diagnostics

### SSH Management
- SSH key validation and permissions checking
- Automatic GitHub SSH configuration
- SSH connection testing
- Key generation and management

### GitHub Integration
- Token authentication and validation
- Repository listing and metadata
- Rate limit monitoring
- User profile management

### Network Services
- Connectivity checks for GitHub and Git services
- DNS resolution testing
- Network diagnostics

### Configuration
- User profile management
- Application settings persistence
- Multi-user support
- Token storage

## Requirements

- Python 3.6+
- Git installed and available in PATH
- SSH client (for SSH operations)

## License

BSD 3-Clause License - See [LICENSE](LICENSE) file for details.

## Related Projects

This core library powers two complete implementations:

### [CLI Version](https://github.com/smartlegionlab/smart-repository-manager-cli) 
A full-featured command-line interface built on top of this core library. Provides terminal-based repository management with all features accessible via commands.

### [GUI Version](https://github.com/smartlegionlab/smart-repository-manager-gui)  
A desktop graphical user interface that offers visual management of repositories, SSH configuration, and synchronization tasks. Built for users who prefer point-and-click interaction.

Both implementations use this core library as their engine, ensuring consistent behavior and feature parity across interfaces.

---

## Disclaimer

**Important**: This software is provided "as-is" without any warranties or guarantees. The developers are not responsible for:

- Data loss or corruption
- Repository damage or unintended modifications
- Security breaches or token exposure
- Network issues or connectivity problems
- Any other direct or indirect damages

**Use at your own risk**. Always maintain backups of your repositories and tokens. This project is in active development and may contain bugs or incomplete features.

## Development Status

⚠️ **Active Development** - This project is under active development. Features may change, and stability is not guaranteed. Not recommended for production use without thorough testing.

## Contributing

Currently not accepting contributions as the project is in early development phase.

## Support

For issues and questions, please check the GitHub repository:  
[https://github.com/smartlegionlab/smart-repository-manager-core](https://github.com/smartlegionlab/smart-repository-manager-core)

---

**Developer**: [Alexander Suvorov]( https://github.com/smartlegionlab/)
**Contact**: [smartlegiondev@gmail.com](mailto:smartlegiondev@gmail.com)
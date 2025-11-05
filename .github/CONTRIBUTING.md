# Contributing to H.A.AI

Thank you for your interest in contributing to H.A.AI! This project aims to help people struggling with social isolation reconnect with others in an authentic way, while respecting their privacy and dignity.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Project Values](#project-values)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Data Privacy & Ethics](#data-privacy--ethics)
- [Pull Request Process](#pull-request-process)
- [Areas for Contribution](#areas-for-contribution)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Project Values

Before contributing, please understand and respect these core values:

1. **Privacy First**: Everything runs locally. No data leaves the user's machine.
2. **Non-Commercial**: Loneliness is not a product. This project is and will remain open source.
3. **Transparency**: We maintain clear AI/human distinction. No deception.
4. **Positive Impact**: Every contribution should serve the mental health and well-being of users.
5. **Bridge to Humans**: AI is a tool to reconnect with real people, not a replacement.

## How Can I Contribute?

### Reporting Bugs

- Use the GitHub issue tracker
- Check if the issue already exists
- Include detailed reproduction steps
- Specify your system configuration
- **Never include personal conversations or sensitive data in bug reports**

### Suggesting Enhancements

- Open an issue with the tag `enhancement`
- Clearly describe the feature and its benefit to users
- Consider privacy and ethical implications
- Explain how it aligns with project values

### Code Contributions

We welcome contributions in these areas:

- Dataset quality improvement
- Crisis detection systems
- Code refactoring and optimization
- Performance improvements for low-end devices
- Multi-language support
- Accessibility features
- Documentation

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- At least 16GB recommended RAM
- GPU with at least 8gb VRAM (NVIDIA)
- Storage for model weights

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/haai.git
cd haai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download required models (instructions in setup guide)
```

### Running Tests

```bash
# Run unit tests
pytest tests/

# Run integration tests
pytest tests/integration/

# Check code quality
flake8 src/
black --check src/
```

## Contribution Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Comment complex logic, especially in dataset processing
- Keep functions focused and modular
- Write docstrings for all public functions

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add multi-language support for French
fix: resolve memory leak in conversation processing
docs: update dataset anonymization guidelines
refactor: simplify emotion detection pipeline
```

Prefix types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

### Documentation

- Update README.md if adding features
- Document all new functions and classes
- Add comments for non-obvious code
- Update dependency lists when needed
- Include setup instructions for new features

## Data Privacy & Ethics

### Handling Conversational Data

**CRITICAL**: This project deals with sensitive mental health conversations.

- **Never commit real conversation data** to the repository
- Use synthetic or heavily anonymized examples only
- Remove all personally identifiable information (PII)
- Respect Discord and Reddit Terms of Service
- Obtain proper consent for data collection

### Dataset Contributions

If contributing to dataset generation:

1. Ensure data is properly anonymized
2. Verify no PII remains (names, locations, specific dates, etc.)
3. Remove toxic content appropriately
4. Document data sources and processing steps
5. Include metadata about anonymization methods

### Model Training

- Document training data sources
- Include bias testing and mitigation
- Test for harmful outputs before submitting
- Consider edge cases (crisis situations, vulnerable users)

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** from `main`: `git checkout -b feature/your-feature-name`
3. **Make your changes** following the guidelines above
4. **Test thoroughly** - this affects people's mental health
5. **Update documentation** as needed
6. **Submit a pull request** with:
   - Clear description of changes
   - Motivation and context
   - Testing performed
   - Any breaking changes
   - Screenshots/examples if applicable

### PR Review Criteria

Your PR will be evaluated on:

- Code quality and style
- Test coverage
- Documentation completeness
- Privacy and ethical considerations
- Alignment with project values
- Performance impact

## Areas for Contribution

### Priority Areas (from roadmap)

1. **Dataset Quality**
   - Improve conversation disentanglement
   - Enhance data cleaning pipelines
   - Create better synthetic conversations

2. **Crisis Detection**
   - Implement suicidal ideation detection
   - Add distress signal recognition
   - Create appropriate response protocols

3. **Code Quality**
   - Refactor spaghetti code
   - Improve efficiency
   - Add comprehensive tests
   - Better error handling

4. **Performance**
   - Optimize for low-end computers
   - Reduce memory footprint
   - Faster model inference

5. **Accessibility**
   - Multi-language support
   - Improved TTS quality
   - Better conversation fluidity

6. **Visual**
   - Create unique Live2D model
   - AI-generated animations
   - Improve lip sync

### Good First Issues

Look for issues tagged with `good first issue` - these are suitable for newcomers:

- Documentation improvements
- Unit test additions
- Code cleanup
- Translation work
- Bug fixes in isolated modules

## Communication

- **Issues**: For bugs, features, and discussions
- **Pull Requests**: For code contributions
- **Discussions**: For general questions and ideas

**Response time**: Please be patient. This is maintained by a student developer.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

## Questions?

Feel free to open an issue with the `question` label if anything is unclear.

---

**Remember**: Every line of code you contribute could help someone reconnect with the world. Take that responsibility seriously, and thank you for helping make a difference.

*"Because your loneliness is not a product"*
# G3r4ki AI Integration Guide

G3r4ki provides advanced AI integration capabilities, supporting both cloud-based and local AI models. This guide explains how to configure and use these features for maximum effectiveness in your security operations.

## Table of Contents

1. [AI Architecture Overview](#ai-architecture-overview)
2. [Cloud AI Providers](#cloud-ai-providers)
3. [Local AI Integration](#local-ai-integration)
4. [AI Proxy System](#ai-proxy-system)
5. [Using AI in G3r4ki](#using-ai-in-g3r4ki)
6. [Security Considerations](#security-considerations)
7. [Advanced Configuration](#advanced-configuration)
8. [Troubleshooting](#troubleshooting)

## AI Architecture Overview

G3r4ki's AI architecture is built with flexibility, resilience, and power in mind. Key components include:

- **AI Proxy**: Central interface that manages all AI providers
- **Cloud Provider Integration**: Support for major cloud AI services
- **Local AI Manager**: Integration with open-source local models
- **Multi-Model Selection**: Automatic or manual selection of appropriate models
- **Auto-Wake System**: Automatically initializes AI components on launch

This architecture ensures G3r4ki can operate in diverse environments, from air-gapped networks to fully connected systems with access to the latest cloud models.

## Cloud AI Providers

G3r4ki integrates with the following cloud AI providers:

### OpenAI

Provides access to powerful GPT models for natural language processing, code analysis, and security reasoning.

**Setup**:
1. Obtain an API key from [OpenAI](https://platform.openai.com/signup)
2. Add the key to your `.env` file:
   ```
   OPENAI_API_KEY=your_openai_key_here
   ```

**Supported Models**:
- gpt-4o (recommended)
- gpt-4
- gpt-3.5-turbo

### Anthropic

Provides Claude models with strong reasoning capabilities and extended context windows.

**Setup**:
1. Obtain an API key from [Anthropic](https://www.anthropic.com/product)
2. Add the key to your `.env` file:
   ```
   ANTHROPIC_API_KEY=your_anthropic_key_here
   ```

**Supported Models**:
- claude-3-5-sonnet-20241022 (recommended)
- claude-3-opus-20240229
- claude-3-sonnet-20240229
- claude-3-haiku-20240307

### DeepSeek

Provides specialized coding and reasoning models.

**Setup**:
1. Obtain an API key from [DeepSeek](https://platform.deepseek.com/)
2. Add the key to your `.env` file:
   ```
   DEEPSEEK_API_KEY=your_deepseek_key_here
   ```

**Supported Models**:
- deepseek-coder
- deepseek-chat

## Local AI Integration

G3r4ki can run entirely offline using local AI models. The system supports multiple local AI frameworks:

### Supported Frameworks

- **llama.cpp**: High-performance inference for LLaMA models
- **GPT4All**: User-friendly framework with various models
- **vLLM**: High-throughput serving for open-source models

### Recommended Models

- **General Purpose**: Llama-2 (7B or 13B)
- **Code Analysis**: CodeLlama (7B or 13B)
- **Low Resource**: TinyLlama (1.1B)
- **Assistant-like**: OpenChat, Vicuna, WizardLM

### Setting Up Local AI

1. Configure local AI settings:
   ```bash
   python g3r4ki.py setup local-ai
   ```

2. Download models:
   ```bash
   python g3r4ki.py setup local-ai --download-model llama2-7b
   ```

3. Test local AI:
   ```bash
   python g3r4ki.py llm test-local --model llama2-7b --prompt "Generate a basic reconnaissance plan"
   ```

Local models are stored in `~/.g3r4ki/models` by default.

## AI Proxy System

The AI Proxy system is the heart of G3r4ki's AI capabilities, providing:

- **Unified Interface**: Consistent API for all AI operations
- **Provider Selection**: Automatic selection of appropriate providers
- **Failover Capability**: Seamless switching between providers if one fails
- **Mode Control**: Explicit control over cloud vs. local operation
- **Cost Management**: Smart selection of models based on task complexity

### Configuration Options

```bash
# Set default mode to local-only
python g3r4ki.py setup ai-proxy --mode local

# Set default mode to cloud-only
python g3r4ki.py setup ai-proxy --mode cloud

# Set default mode to auto (prefer cloud, fallback to local)
python g3r4ki.py setup ai-proxy --mode auto

# Configure provider priority
python g3r4ki.py setup ai-proxy --priority "anthropic,openai,deepseek,local"
```

### Using the Proxy Programmatically

The AI Proxy can be used directly in G3r4ki modules or custom code:

```python
from src.ai.proxy import AIProxy

# Initialize the proxy
ai_proxy = AIProxy(mode="auto")

# Get a text completion
response = ai_proxy.get_completion(
    prompt="Analyze this network scan result and identify potential vulnerabilities:",
    content="PORT   STATE SERVICE\n22/tcp open  ssh\n80/tcp open  http\n443/tcp open  https",
    max_tokens=500
)

# Check if using cloud or local
is_cloud = ai_proxy.is_cloud_available()
is_local = ai_proxy.is_local_available()
```

## Using AI in G3r4ki

G3r4ki integrates AI throughout its features in various ways:

### Command Understanding

Natural language commands are processed using AI:

```bash
# Instead of using this syntax:
python g3r4ki.py offensive shell generate --type reverse --language bash --lhost 192.168.1.5 --lport 4444

# You can use natural language:
python g3r4ki.py interactive
g3r4ki> create a bash reverse shell connecting back to 192.168.1.5 port 4444
```

### Security Analysis

AI-assisted analysis of security data:

```bash
# Vulnerability scan with AI analysis
python g3r4ki.py sec scan --target 192.168.1.10 --ai-analysis

# Analyze a suspicious file
python g3r4ki.py sec analyze --file malware.exe --ai-analysis
```

### Mission Planning

AI helps plan and execute security operations:

```bash
# Create an AI-assisted penetration testing plan
python g3r4ki.py offensive mission plan --target "Example Corp" --objective "Data Exfiltration" --ai-guided
```

### Interactive AI Assistance

Get interactive AI help with security tasks:

```bash
# Start interactive AI security assistant
python g3r4ki.py interactive
g3r4ki> ai assist

# Or using the web interface
python g3r4ki.py web
# Then navigate to http://localhost:5000/ai
```

## Security Considerations

When using AI with G3r4ki, consider the following security aspects:

### Data Handling

- **Cloud Services**: Data sent to cloud providers is subject to their privacy policies
- **Sensitive Information**: Avoid sending sensitive data to cloud providers
- **Local Processing**: Use local models for high-security environments
- **API Key Security**: Protect your API keys as they provide access to paid services

### Model Limitations

- **Reliability**: AI responses should be verified by security professionals
- **Hallucinations**: Models may generate plausible but incorrect information
- **Current Knowledge**: Models have knowledge cutoffs and may not know about latest vulnerabilities or techniques

### Recommended Practices

- Use AI as an assistant, not a replacement for security expertise
- Validate AI-generated code and commands before execution
- Prefer local AI models for sensitive operations
- Regularly update local models to incorporate new knowledge

## Advanced Configuration

### Custom Model Configuration

You can configure specific models for specific tasks:

```yaml
# ~/.g3r4ki/ai_config.yaml
tasks:
  code_analysis:
    preferred_provider: openai
    preferred_model: gpt-4o
  vulnerability_assessment:
    preferred_provider: anthropic
    preferred_model: claude-3-5-sonnet-20241022
  command_generation:
    preferred_provider: local
    preferred_model: llama2-13b
```

### Performance Tuning

For improved performance with local models:

```bash
# Configure thread settings for local inference
python g3r4ki.py setup local-ai --inference-threads 4 --batch-size 512
```

### API Usage Monitoring

Monitor your cloud API usage:

```bash
# View API usage statistics
python g3r4ki.py llm usage-stats

# Set usage limits
python g3r4ki.py setup ai-limits --monthly-budget 50 --provider openai
```

## Troubleshooting

### Common Issues

#### Cloud AI Not Working

- Verify API key is correct and not expired
- Check internet connectivity
- Ensure the API key has sufficient credits/quota
- Verify the selected model is available on your account

#### Local AI Issues

- Check if models are properly downloaded
- Verify system has sufficient RAM for the selected model
- Update to the latest version of the local inference libraries
- Try a smaller model if experiencing memory issues

#### AI Proxy Errors

- Check the log files at `~/.g3r4ki/logs/ai_proxy.log`
- Verify configuration files exist and are properly formatted
- Reset proxy configuration: `python g3r4ki.py setup ai-proxy --reset`

### Getting Help

For more help with AI integration:

```bash
# Get detailed help on AI configuration
python g3r4ki.py llm --help

# Check AI system status
python g3r4ki.py status ai

# Run AI diagnostics
python g3r4ki.py setup diagnose-ai
```

## Conclusion

G3r4ki's AI integration provides powerful capabilities for security professionals, enabling enhanced automation, analysis, and guidance for cybersecurity operations. By configuring both cloud and local AI providers, users can ensure the system works effectively in any environment while maintaining security and privacy.
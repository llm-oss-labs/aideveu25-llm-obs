# Getting Started with Ollama: A Beginner's Guide

This guide will walk you through installing and setting up Ollama on your system, and show you how to run your first AI model (Phi) locally.

## What is Ollama?

Ollama is a tool that makes it easy to run large language models (LLMs) locally on your computer. It simplifies the process of downloading, installing, and running models like Llama, Phi, Mistral, and many others.

## Prerequisites

Before installing Ollama, ensure your system meets these requirements:

### System Requirements
- **RAM**: At least 8GB (16GB+ recommended for larger models)
- **Storage**: 10GB+ free space for models
- **Operating System**: 
  - macOS 10.15 or later
  - Linux (most distributions)
  - Windows 10/11 (with WSL2 for best performance)

### Dependencies
- **Internet connection** for downloading models
- **Terminal/Command Prompt** access
- **Administrator privileges** for installation

---

## Step 1: Install Ollama

### For macOS

1. **Download the installer**:
   - Visit [ollama.com](https://ollama.com)
   - Click "Download for macOS"
   - Or use Homebrew:
   ```bash
   brew install ollama
   ```

2. **Install using the downloaded file**:
   - Open the downloaded `.dmg` file
   - Drag Ollama to your Applications folder
   - Launch Ollama from Applications

3. **Install via command line** (alternative):
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

### For Linux

1. **Install using the official script**:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **For Ubuntu/Debian users** (alternative):
   ```bash
   # Add the repository
   curl -fsSL https://ollama.com/gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/ollama-keyring.gpg
   echo "deb [signed-by=/usr/share/keyrings/ollama-keyring.gpg] https://ollama.com/repo ubuntu main" | sudo tee /etc/apt/sources.list.d/ollama.list
   
   # Update and install
   sudo apt update
   sudo apt install ollama
   ```

### For Windows

1. **Download the installer**:
   - Visit [ollama.com](https://ollama.com)
   - Click "Download for Windows"
   - Run the downloaded `.exe` file as administrator

2. **Using WSL2** (recommended for better performance):
   - Install WSL2 if not already installed
   - Open WSL2 terminal
   - Follow the Linux installation steps above

---

## Step 2: Verify Installation

After installation, verify that Ollama is working correctly:

1. **Open a terminal/command prompt**

2. **Check if Ollama is installed**:
   ```bash
   ollama --version
   ```
   You should see output like: `ollama version is 0.x.x`

3. **Start the Ollama service**:
   ```bash
   ollama serve
   ```
   This starts the Ollama server. You should see output indicating the server is running.

4. **Open a new terminal window** (keep the server running in the first one) and test the connection:
   ```bash
   ollama list
   ```
   This should show an empty list (since no models are installed yet) without errors.

---

## Step 3: Download and Run the Phi Model

Now let's download and run your first AI model - Microsoft's Phi model:

1. **Download the Phi model**:
   ```bash
   ollama pull phi3
   ```
   This will download the Phi3 model (approximately 2.3GB). The download may take several minutes depending on your internet speed.

2. **Verify the model was downloaded**:
   ```bash
   ollama list
   ```
   You should see `phi3` listed in the output.

3. **Run the Phi model**:
   ```bash
   ollama run phi3
   ```
   This starts an interactive chat session with the Phi model.

4. **Test the model** by typing a simple prompt:
   ```
   Hello! Can you explain what you are?
   ```
   The model should respond with information about itself.

5. **Exit the chat session**:
   Type `/bye` or press `Ctrl+C` to exit.

---

## Step 4: Basic Ollama Commands

Here are essential commands you'll use frequently:

### Model Management
```bash
# List available models online
ollama list

# Download a specific model
ollama pull <model-name>

# Remove a model
ollama rm <model-name>

# Show model information
ollama show <model-name>
```

### Running Models
```bash
# Start interactive chat
ollama run <model-name>

# Run a single prompt
ollama run <model-name> "Your prompt here"

# Run with custom parameters
ollama run <model-name> --temperature 0.7 "Your prompt here"
```

### Server Management
```bash
# Start Ollama server
ollama serve

# Check server status
ollama ps
```

---

## Step 5: Example Usage

Here are some practical examples:

### Single Question
```bash
ollama run phi3 "Write a Python function to calculate factorial"
```

### Interactive Conversation
```bash
ollama run phi3
>>> What are the benefits of running AI models locally?
>>> Can you show me a simple example of machine learning?
>>> /bye
```

### Using Different Models
```bash
# Try other popular models
ollama pull llama3.2
ollama run llama3.2

ollama pull mistral
ollama run mistral
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. "Command not found: ollama"
**Problem**: Ollama is not in your system PATH.

**Solution**:
```bash
# For macOS/Linux - add to your shell profile (.bashrc, .zshrc)
export PATH="/usr/local/bin:$PATH"

# Reload your shell
source ~/.zshrc  # or ~/.bashrc
```

#### 2. "Failed to connect to ollama server"
**Problem**: Ollama server is not running.

**Solution**:
```bash
# Start the server in a separate terminal
ollama serve

# Or check if it's already running
ollama ps
```

#### 3. Model download fails or is very slow
**Problem**: Network connectivity or firewall issues.

**Solutions**:
- Check your internet connection
- Try downloading a smaller model first: `ollama pull phi3:mini`
- If behind a corporate firewall, configure proxy settings

#### 4. "Not enough memory" error
**Problem**: Insufficient RAM for the model.

**Solutions**:
- Close other applications to free up memory
- Try a smaller model variant:
  ```bash
  ollama pull phi3:mini    # Smaller version
  ollama pull llama3.2:1b  # 1 billion parameter model
  ```

#### 5. Slow model responses
**Problem**: Model running on CPU instead of GPU, or insufficient resources.

**Solutions**:
- Ensure you have adequate RAM (8GB minimum)
- Close unnecessary applications
- For GPU acceleration, ensure proper drivers are installed

#### 6. Port conflicts
**Problem**: Default port (11434) is already in use.

**Solution**:
```bash
# Start Ollama on a different port
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

#### 7. Permission errors (Linux/macOS)
**Problem**: Insufficient permissions to install or run Ollama.

**Solution**:
```bash
# Ensure proper permissions
sudo chown -R $USER:$USER ~/.ollama

# Or run installation with sudo (if needed)
sudo curl -fsSL https://ollama.com/install.sh | sh
```

---

## Next Steps

Once you have Ollama running successfully:

1. **Explore different models**: Try `llama3.2`, `mistral`, `codellama`, or `qwen2`
2. **Learn about model parameters**: Experiment with temperature, top-p, and other settings
3. **Integrate with applications**: Use Ollama's REST API to build applications
4. **Join the community**: Check out the [Ollama GitHub repository](https://github.com/ollama/ollama) for updates and examples

## API Usage

Ollama also provides a REST API for integration with applications:

```bash
# Example API call
curl http://localhost:11434/api/generate -d '{
  "model": "phi3",
  "prompt": "Why is the sky blue?"
}'
```

Congratulations! You now have Ollama running locally and can experiment with AI models on your own machine.

---

## Resources

- **Official Website**: [ollama.com](https://ollama.com)
- **GitHub Repository**: [github.com/ollama/ollama](https://github.com/ollama/ollama)
- **Model Library**: [ollama.com/library](https://ollama.com/library)
- **API Documentation**: [github.com/ollama/ollama/blob/main/docs/api.md](https://github.com/ollama/ollama/blob/main/docs/api.md)

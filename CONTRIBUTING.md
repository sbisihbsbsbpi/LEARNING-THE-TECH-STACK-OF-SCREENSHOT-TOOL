# Contributing to Screenshot Headless Tool

Thank you for your interest in contributing! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Your environment (OS, Python version, Node version)

### Suggesting Features

Feature requests are welcome! Please open an issue with:
- Clear description of the feature
- Use case / why it's needed
- Proposed implementation (if you have ideas)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**
   ```bash
   git commit -m "Add: feature description"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request**

### Code Style

**Python:**
- Follow PEP 8
- Use type hints where possible
- Add docstrings to functions

**TypeScript/React:**
- Use TypeScript strict mode
- Follow React best practices
- Use functional components with hooks

**Commits:**
- Use conventional commits format:
  - `feat:` - New feature
  - `fix:` - Bug fix
  - `docs:` - Documentation
  - `style:` - Formatting
  - `refactor:` - Code restructuring
  - `test:` - Tests
  - `chore:` - Maintenance

### Development Setup

1. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/screenshot-headless-tool.git
   cd screenshot-headless-tool/screenshot-app
   ```

2. **Install dependencies**
   ```bash
   # Backend
   cd backend
   pip3 install -r requirements.txt
   playwright install chromium
   
   # Frontend
   cd ../frontend
   npm install
   ```

3. **Run in development mode**
   ```bash
   # Terminal 1: Backend
   cd backend
   python3 main.py
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

### Testing

Before submitting a PR:
- Test all existing features still work
- Test your new feature thoroughly
- Test on different URLs
- Check for console errors
- Verify no memory leaks

### Questions?

Feel free to open an issue for any questions!

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to build something great together! 🚀


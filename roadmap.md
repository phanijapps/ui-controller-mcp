# UI Controller MCP Enhancement Roadmap

This document outlines the plan to transform the `ui-controller-mcp` into a powerful, secure, and context-aware agentic tool tailored for Linux Mint XFCE.

## 🎯 Objectives
- **Security**: Securely handle user authentication (sudo, passwords).
- **Vision**: Integrate OpenCV for fast, reliable element detection.
- **Integration**: Deep integration with Linux Mint XFCE and terminal tools.
- **Capabilities**: Support complex workflows for apps like Signal.

## 🗓️ Phases

### Phase 1: Security & Authentication ("User Auth")
**Goal**: Enable the agent to perform privileged tasks and handle sensitive data securely without exposing passwords in logs or prompts.

- [ ] **Secure Storage**: Implement a secure credential manager (using system keyring or encrypted local storage) to store user passwords/API keys.
- [ ] **Tool: `type_password`**: A specialized tool that retrieves a stored password by identifier (e.g., "sudo_pass") and types it into the active field *without* logging the actual characters to the agent's trace or console.
- [ ] **Tool: `handle_sudo`**: A high-level tool that detects a sudo prompt (visually or via terminal context), retrieves the sudo password, and enters it securely.
- [ ] **Safety Checks**: Prevent `type_text` from being used for known sensitive fields if possible.

### Phase 2: Enhanced Vision & Perception (OpenCV)
**Goal**: Improve the speed, accuracy, and reliability of UI element detection using Computer Vision techniques alongside LLMs.

- [ ] **Integration**: Ensure `opencv-python` is fully integrated and configured.
- [ ] **Tool: `find_image`**: Use Template Matching to find specific UI elements (icons, buttons) on screen based on reference images. This is much faster and more reliable than VLM for static assets.
- [ ] **Tool: `wait_for_image`**: Block execution until a specific visual element appears (e.g., wait for the "Signal" icon to appear after launching).
- [ ] **Tool: `ocr_region`**: (Optional) Integrate Tesseract or a lightweight OCR model to read text from a specific screen region, enabling fast text verification.
- [ ] **Visual Verification**: Implement a helper that compares screen states before and after a click to verify the action had an effect.

### Phase 3: Deep System Integration (Linux Mint XFCE)
**Goal**: Leverage the specific environment for better control and stability.

- [ ] **Window Management**: Enhance `list_windows` and `focus_window` to use `wmctrl` or `xdotool` (via subprocess) which are often more robust on XFCE than generic libraries.
- [ ] **Terminal Integration**:
    - Create a `TerminalSession` capability that can spawn a PTY (pseudo-terminal).
    - Allow the agent to run background commands directly (not just UI typing) when appropriate.
    - **Tool: `run_terminal_cmd`**: Execute a command in a hidden shell and return output (for system queries).
- [ ] **System State**:
    - **Tool: `check_notification`**: Listen to DBus for system notifications (e.g., "New Signal Message").
    - **Tool: `get_system_status`**: Check battery, network, and volume levels.

### Phase 4: Application "Skills" (Signal & More)
**Goal**: Create high-level workflows for specific applications.

- [ ] **App Definitions**: Create a configuration system to define "Apps" with their specific behaviors, icon paths, and shortcuts.
- [ ] **Signal Skill**:
    - Define anchors: "Search Bar", "New Message", "Send Button".
    - **Workflow**: `send_signal_message(contact, message)` -> Automates the UI steps.
- [ ] **Browser Skill**:
    - Better integration with Firefox/Chrome (e.g., focusing address bar `Ctrl+L`).

### Phase 5: Reliability & Context Awareness
**Goal**: Make the agent "smart" about its actions and history.

- [ ] **Context Tracking**: Maintain a short-term memory of:
    - Last active window.
    - Last action performed.
    - Last visual state analysis.
- [ ] **Smart Retry**: If an action fails (e.g., `find_image` returns nothing), automatically try scrolling or waiting before failing the task.
- [ ] **Goal Decomposition**: Enhance the `reason` tool to break down complex goals (e.g., "Send file to Bob on Signal") into atomic UI steps automatically.

## 🛠️ Tool Categories

### 1. Core UI (Basic Interaction)
- `click(x, y, button)`
- `type_text(text, enter)`
- `scroll(amount, direction)`
- `drag_and_drop(start_x, start_y, end_x, end_y)` [NEW]
- `press_hotkey(keys)` [NEW] (e.g., "ctrl+c", "alt+tab")

### 2. Vision (Perception)
- `perceive(instruction)`: LLM-based analysis.
- `find_image(image_name, confidence)`: [NEW] OpenCV template matching.
- `wait_for_image(image_name, timeout)`: [NEW] Sync mechanism.
- `get_text_at(region)`: [NEW] OCR.

### 3. System & OS (Control)
- `launch_app(target)`
- `list_windows()`
- `focus_window(title)`
- `get_clipboard()` [NEW]
- `set_clipboard(text)` [NEW]
- `run_terminal_cmd(cmd)` [NEW] (Background execution)

### 4. Security (Authentication)
- `type_password(id)` [NEW]
- `handle_sudo()` [NEW]
- `manage_credentials(action, key, value)` [NEW]

### 5. App Skills (High-Level)
- `signal_send(contact, message)` [NEW]
- `browser_open_url(url)` [NEW]

## 🚀 Next Steps
1. Approve this roadmap.
2. Begin **Phase 1: Security & Authentication**.
3. Proceed to **Phase 2: Enhanced Vision**.

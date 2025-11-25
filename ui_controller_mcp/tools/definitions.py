from __future__ import annotations

from typing import Any, Callable, Dict, List

from ui_controller_mcp.desktop.base import DesktopActionResult

ToolHandler = Callable[[Dict[str, Any]], DesktopActionResult]


def tool_definitions() -> List[dict[str, Any]]:
    return [
        {
            "name": "launch_app",
            "description": """Launch an application by name or command.

WHEN TO USE:
- Starting a new application that isn't currently running
- Opening a specific program before automating it
- Launching system utilities or tools

HOW IT WORKS:
- Executes the specified command or application name
- Works with both GUI and CLI applications
- Returns immediately after launching (doesn't wait for app to fully load)

INPUT:
- target: Application name, command, or path
  Examples:
  * "firefox" - Launch Firefox browser
  * "code" - Launch VS Code
  * "gnome-calculator" - Launch calculator
  * "/usr/bin/gimp" - Launch GIMP with full path

OUTPUT:
- message: Confirmation that the app was launched

BEST PRACTICES:
- Use simple application names when possible
- After launching, use 'list_windows' to verify it opened
- Wait a few seconds before interacting with newly launched apps
- Use 'focus_window' to bring the app to foreground

EXAMPLE:
launch_app(target="firefox")
# Wait for app to load
time.sleep(3)
list_windows()  # Verify Firefox is in the list
focus_window(title="Firefox")  # Bring to front""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Application name, command, or full path to executable",
                    },
                },
                "required": ["target"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Status message confirming launch"},
                },
                "required": ["message"],
            },
        },
        {
            "name": "list_windows",
            "description": """List all currently open windows on the desktop.

WHEN TO USE:
- To see what applications are currently running
- Before focusing a specific window
- To verify an application launched successfully
- To check if a window with specific title exists

HOW IT WORKS:
- Queries the window manager for all open windows
- Returns the title of each window
- Includes all windows (visible, minimized, background)

INPUT:
- No parameters required

OUTPUT:
- windows: Array of window titles (strings)
  Example output:
  ["Firefox - Mozilla Firefox",
   "Terminal - bash",
   "Visual Studio Code",
   "Settings"]

BEST PRACTICES:
- Use this before 'focus_window' to find exact title
- Window titles may include application name and document/page title
- Titles can change (e.g., browser tabs, document names)
- Use partial matching when focusing windows

EXAMPLE:
windows = list_windows()
for window in windows:
    if "Firefox" in window:
        focus_window(title="Firefox")
        break""",
            "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
            "output_schema": {
                "type": "object",
                "properties": {
                    "windows": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of window titles for all open windows",
                    },
                },
                "required": ["windows"],
            },
        },
        {
            "name": "focus_window",
            "description": """Bring a window to the foreground by matching its title.

WHEN TO USE:
- Before interacting with a specific application
- To switch between multiple open applications
- After launching an app to bring it to front
- When you need to ensure clicks/typing go to the right window

HOW IT WORKS:
- Searches for windows with matching title (case-insensitive partial match)
- Activates the first matching window
- Brings window to foreground and gives it focus

INPUT:
- title: Full or partial window title to match
  Examples:
  * "Firefox" - Matches "Mozilla Firefox" or "Firefox - Google"
  * "Terminal" - Matches "Terminal - bash"
  * "code" - Matches "Visual Studio Code"

OUTPUT:
- message: Confirmation of which window was focused, or error if not found

BEST PRACTICES:
- Use 'list_windows' first to see exact titles
- Partial matches work ("Fire" matches "Firefox")
- Case-insensitive matching
- If multiple windows match, the first one is focused
- Always focus before clicking or typing

EXAMPLE:
list_windows()  # See available windows
focus_window(title="Firefox")  # Bring Firefox to front
# Now safe to click/type in Firefox
click(x=640, y=300)""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Full or partial window title to match (case-insensitive)",
                    },
                },
                "required": ["title"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Status message indicating success or failure",
                    }
                },
                "required": ["message"],
            },
        },
        {
            "name": "click",
            "description": """Perform a mouse click at specified coordinates or current position.

WHEN TO USE:
- Clicking buttons, links, or UI elements
- Selecting items in lists or menus
- Activating controls identified by 'perceive' tool
- Right-clicking for context menus

HOW IT WORKS:
- Moves mouse to specified coordinates (if provided)
- Performs the specified button click
- If no coordinates given, clicks at current mouse position

INPUT:
- x (optional): Horizontal coordinate (pixels from left edge)
- y (optional): Vertical coordinate (pixels from top edge)
- button (optional): Which mouse button to click
  * "left" (default) - Standard click
  * "right" - Context menu click
  * "middle" - Middle mouse button

OUTPUT:
- message: Confirmation that click was executed

BEST PRACTICES:
- Use 'perceive' first to identify element locations
- Use 'reason' to determine exact coordinates
- Ensure correct window is focused before clicking
- Wait briefly after clicks for UI to respond
- Verify click result with 'perceive'

COORDINATE SYSTEM:
- Origin (0,0) is top-left corner of screen
- X increases to the right
- Y increases downward
- Typical screen: 1920x1080 (width x height)

EXAMPLE:
# Get coordinates from perceive/reason
analysis = perceive(instruction="Find submit button")
plan = reason(analysis=analysis, goal="Click submit")
# Plan might say: "Click at coordinates (640, 450)"
click(x=640, y=450, button="left")
time.sleep(0.5)  # Wait for response
perceive()  # Verify click worked""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate in pixels from left edge of screen",
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate in pixels from top edge of screen",
                    },
                    "button": {
                        "type": "string",
                        "enum": ["left", "right", "middle"],
                        "description": "Mouse button to click (default: left)",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Confirmation message",
                    }
                },
                "required": ["message"],
            },
        },
        {
            "name": "type_text",
            "description": """Type text into the currently focused window or input field.

WHEN TO USE:
- Entering text into input fields, text areas, or editors
- Filling out forms
- Typing search queries
- Entering commands in terminals

HOW IT WORKS:
- Types each character sequentially into the active window
- Simulates actual keyboard input
- Text goes to whatever has focus (window, input field, etc.)
- Includes safety checks to prevent dangerous commands

INPUT:
- text: The text string to type
  Examples:
  * "user@example.com" - Email address
  * "Hello, World!" - Simple text
  * "search query" - Search terms
  * "123456" - Numbers
- enter (optional): Whether to press Enter after typing (default: false)
  * true - Press Enter key after text
  * false - Just type text

OUTPUT:
- message: Confirmation that text was typed

IMPORTANT NOTES:
- Text is typed character by character (not pasted)
- Ensure correct field is focused before typing

BEST PRACTICES:
- Click on input field first to focus it
- Use 'perceive' to verify field is focused (cursor visible)
- After typing, use 'perceive' to verify text appeared
- For passwords, the text will be typed but may appear as dots
- Wait briefly after typing before next action

EXAMPLE:
# Focus and fill a form field
click(x=640, y=300)  # Click on email field
time.sleep(0.3)
type_text("user@example.com")
perceive(instruction="Check if email was entered")
# Move to next field
click(x=640, y=350)  # Password field
type_text("mypassword123", enter=True)  # Submit form""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to type into the active window or field",
                    },
                    "enter": {
                        "type": "boolean",
                        "description": "Whether to press Enter after typing (default: false)",
                    },
                },
                "required": ["text"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Confirmation message",
                    }
                },
                "required": ["message"],
            },
        },
        {
            "name": "scroll",
            "description": """Scroll the active window vertically or horizontally.

WHEN TO USE:
- Viewing content that extends beyond visible area
- Navigating long web pages or documents
- Reaching UI elements not currently visible
- Moving through lists or tables

HOW IT WORKS:
- Simulates mouse wheel scrolling
- Scrolls in the active window or under mouse cursor
- Amount determines distance scrolled

INPUT:
- amount: How much to scroll (positive or negative integer)
  * Positive values: scroll down/right
  * Negative values: scroll up/left
  * Typical values: 100-500 for small scrolls, 1000+ for large
- direction: Which way to scroll
  * "vertical" (default) - Up/down scrolling
  * "horizontal" - Left/right scrolling

OUTPUT:
- message: Confirmation that scroll was executed

BEST PRACTICES:
- Use 'perceive' before scrolling to understand current view
- Scroll in small increments to avoid overshooting
- Use 'perceive' after scrolling to see new content
- For precise navigation, scroll then use 'perceive' to locate elements
- Ensure correct window is focused

SCROLL AMOUNTS:
- Small scroll: 100-300 (one or two lines)
- Medium scroll: 500-1000 (half page)
- Large scroll: 1500-3000 (full page)

EXAMPLE:
# Scroll down to see more content
perceive(instruction="What's visible on page?")
scroll(amount=500, direction="vertical")  # Scroll down
time.sleep(0.5)  # Wait for scroll to complete
perceive(instruction="Find the 'Load More' button")

# Scroll back up
scroll(amount=-500, direction="vertical")""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "integer",
                        "description": "Scroll distance (positive=down/right, negative=up/left)",
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["vertical", "horizontal"],
                        "description": "Scroll direction (default: vertical)",
                    },
                },
                "required": ["amount"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Confirmation message",
                    }
                },
                "required": ["message"],
            },
        },
        {
            "name": "screenshot",
            "description": """Capture a screenshot of the entire screen.

WHEN TO USE:
- Rarely needed directly - 'perceive' tool calls this automatically
- When you need the raw screenshot file or base64 data
- For debugging or logging purposes
- To save a visual record of the screen state

HOW IT WORKS:
- Captures the entire desktop screen
- Saves to 'screenshots/' directory with timestamp
- Returns both file path and base64-encoded image data
- Used internally by the 'perceive' tool

INPUT:
- No parameters required

OUTPUT:
- path: File path where screenshot was saved
- captured_at: ISO timestamp of when screenshot was taken
- base64_data: The screenshot encoded as base64 string

IMPORTANT NOTES:
- The 'perceive' tool automatically takes screenshots
- You usually don't need to call this directly
- Use 'perceive' instead for AI analysis of the screen
- Screenshots are saved in the working directory

BEST PRACTICES:
- Prefer 'perceive' over raw screenshots
- Use this only if you need the image file itself
- Screenshots capture the entire screen, not individual windows

EXAMPLE:
# Usually you would use perceive instead:
perceive(instruction="Analyze the screen")

# But if you need the raw screenshot:
result = screenshot()
print(f"Screenshot saved to: {result['path']}")
print(f"Captured at: {result['captured_at']}")
# base64_data can be used to send image elsewhere""",
            "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
            "output_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path where screenshot was saved",
                    },
                    "captured_at": {
                        "type": "string",
                        "description": "ISO timestamp of capture time",
                    },
                    "base64_data": {
                        "type": "string",
                        "description": "Screenshot image encoded as base64 string",
                    },
                },
                "required": ["captured_at"],
            },
        },
        {
            "name": "get_bytes",
            "description": """Read a file from disk and return its contents as base64.

WHEN TO USE:
- Reading image files for processing
- Accessing screenshots or other binary files
- Retrieving file contents for transmission
- Working with files generated by other tools

HOW IT WORKS:
- Reads the specified file from disk
- Encodes contents as base64 string
- Returns file metadata and encoded data
- Has a 5MB size limit for safety

INPUT:
- path: File path (absolute or relative)
  Examples:
  * "/home/user/image.png" - Absolute path
  * "./screenshots/screenshot.png" - Relative path
  * "~/Documents/file.pdf" - Home directory path

OUTPUT:
- path: Resolved absolute path to the file
- size: File size in bytes
- base64_data: File contents encoded as base64 string

LIMITATIONS:
- Maximum file size: 5MB (5,242,880 bytes)
- Files larger than 5MB will be rejected
- Binary and text files both supported

BEST PRACTICES:
- Use absolute paths when possible
- Check file exists before reading
- Be aware of size limitations
- Useful for reading screenshots taken by 'screenshot' tool

EXAMPLE:
# Read a screenshot file
screenshot_result = screenshot()
file_data = get_bytes(path=screenshot_result['path'])
print(f"File size: {file_data['size']} bytes")
# Now you have base64_data to send elsewhere

# Read any file
file_data = get_bytes(path="/home/user/document.pdf")
if file_data['success']:
    # Process the base64_data
    pass""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative file path (max 5MB file size)",
                    },
                },
                "required": ["path"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Resolved absolute path to the file",
                    },
                    "size": {
                        "type": "integer",
                        "description": "File size in bytes",
                    },
                    "base64_data": {
                        "type": "string",
                        "description": "File contents encoded as base64 string",
                    },
                },
                "required": ["path", "size", "base64_data"],
            },
        },
        {
            "name": "perceive",
            "description": """Analyze the current screen state using vision AI to understand what is visible on the desktop.

WHEN TO USE:
- At the start of any UI automation task to understand the current state
- After performing actions to verify the result
- When you need to locate specific UI elements (buttons, inputs, text, etc.)
- To understand the context before deciding what action to take next

HOW IT WORKS:
- Captures a screenshot of the entire desktop
- Uses a vision model (Ollama) to analyze the image
- Returns a detailed description of visible UI elements and their locations

INPUT:
- instruction (optional): Provide specific guidance on what to look for
  Examples:
  * "Find the login button"
  * "Locate all input fields on the screen"
  * "Identify error messages or warnings"
  * "Find the navigation menu"

OUTPUT:
- analysis: A detailed text description including:
  * Visible UI elements (buttons, inputs, text, images, etc.)
  * Approximate locations of elements (top-left, center, bottom-right, etc.)
  * Text content visible on screen
  * Overall context and application state

BEST PRACTICES:
- Use specific instructions to get focused analysis
- Call this before making decisions about what to click or type
- Use it to verify actions completed successfully
- Combine with 'reason' tool to plan next steps

EXAMPLE WORKFLOW:
1. perceive(instruction="Find the search box")
2. reason(analysis=<result>, goal="Search for 'example'")
3. Execute the planned action (click, type_text, etc.)
4. perceive() to verify the action succeeded""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "instruction": {
                        "type": "string",
                        "description": "Optional specific instruction to focus the vision analysis on particular elements or aspects of the screen",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "analysis": {
                        "type": "string",
                        "description": "Detailed description of UI elements, their locations, visible text, and overall screen context",
                    },
                },
                "required": ["analysis"],
            },
        },
        {
            "name": "reason",
            "description": """Plan the next action based on UI analysis and your goal using AI reasoning.

WHEN TO USE:
- After using 'perceive' to analyze the screen
- When you need to decide what action to take next
- To break down complex goals into specific steps
- To determine coordinates or elements to interact with

HOW IT WORKS:
- Takes the analysis from 'perceive' tool
- Considers your ultimate goal
- Uses a language model (Ollama) to plan the next logical step
- Returns a specific action plan

INPUT:
- analysis (required): The output from the 'perceive' tool describing current UI state
- goal (required): Your ultimate objective
  Examples:
  * "Log in to the application"
  * "Search for 'machine learning' and open first result"
  * "Fill out the registration form"
  * "Navigate to settings and change theme to dark mode"

OUTPUT:
- plan: A specific action plan including:
  * The exact next step to take
  * Which UI element to interact with
  * What action to perform (click, type, scroll, etc.)
  * Any specific details like coordinates or text to enter

BEST PRACTICES:
- Always use fresh analysis from 'perceive' tool
- Be specific with your goal
- The plan will be a single next step, not the entire workflow
- After executing the plan, use 'perceive' again to see the result
- Iterate: perceive → reason → act → perceive → reason → act

EXAMPLE WORKFLOW:
1. perceive(instruction="Find login form")
   → Returns: "Login form visible with username field at center-left, 
              password field below it, and blue 'Sign In' button at bottom"

2. reason(
     analysis=<above result>,
     goal="Log in with username 'user@example.com' and password 'pass123'"
   )
   → Returns: "Click on the username field at center-left to focus it, 
              then type 'user@example.com'"

3. Execute: click(x=<coord>, y=<coord>) then type_text("user@example.com")

4. perceive() to verify username was entered

5. reason(analysis=<new result>, goal="Complete login")
   → Returns: "Click on password field and enter password"

IMPORTANT NOTES:
- This tool does NOT execute actions, it only plans them
- You must execute the planned actions using other tools (click, type_text, etc.)
- Always verify with 'perceive' after executing actions
- The reasoning model helps avoid mistakes by analyzing context""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "analysis": {
                        "type": "string",
                        "description": "The UI analysis from the 'perceive' tool describing what is currently visible on screen",
                    },
                    "goal": {
                        "type": "string",
                        "description": "Your ultimate objective or what you want to accomplish (e.g., 'log in to the app', 'search for X')",
                    },
                },
                "required": ["analysis", "goal"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "plan": {
                        "type": "string",
                        "description": "The specific next action to take, including which element to interact with and how",
                    },
                },
                "required": ["plan"],
            },
        },
        {
            "name": "manage_credentials",
            "description": """Store or retrieve secure credentials (passwords, API keys).

WHEN TO USE:
- Setting up passwords for the agent to use later
- Checking if a credential exists (without revealing it)
- Updating stored passwords

HOW IT WORKS:
- Uses system keyring or encrypted local file
- Passwords are stored securely, not in plain text files

INPUT:
- action: "set" or "check" (get is not exposed to prevent leakage)
- id: Identifier for the credential (e.g., "sudo_pass", "signal_pin")
- value: The password/secret (only required for "set")

OUTPUT:
- message: Success/failure status

EXAMPLE:
manage_credentials(action="set", id="sudo_pass", value="mypassword123")""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["set", "check"],
                        "description": "Action to perform",
                    },
                    "id": {
                        "type": "string",
                        "description": "Identifier for the credential",
                    },
                    "value": {
                        "type": "string",
                        "description": "The password value (required for 'set')",
                    },
                },
                "required": ["action", "id"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Status message"},
                },
                "required": ["message"],
            },
        },
        {
            "name": "type_password",
            "description": """Type a stored password securely into the active field.

WHEN TO USE:
- Logging into websites or apps
- Entering sudo passwords (if handle_sudo doesn't apply)
- Unlocking secure notes

HOW IT WORKS:
- Retrieves password from secure storage using the 'id'
- Types it into the active window
- DOES NOT log the password in the agent trace or output

INPUT:
- id: Identifier of the stored credential (e.g., "sudo_pass")
- enter: Whether to press Enter after typing (default: True)

OUTPUT:
- message: Confirmation (without revealing password)

EXAMPLE:
# Focus password field first
click(x=500, y=500)
type_password(id="github_token")""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Identifier of the stored credential",
                    },
                    "enter": {
                        "type": "boolean",
                        "description": "Press Enter after typing (default: True)",
                    },
                },
                "required": ["id"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Status message"},
                },
                "required": ["message"],
            },
        },
        {
            "name": "handle_sudo",
            "description": """Handle a sudo prompt by typing the stored sudo password.

WHEN TO USE:
- When a terminal or GUI asks for sudo privileges
- After running a command like 'sudo apt update'

HOW IT WORKS:
- Retrieves the credential with id="sudo_pass"
- Types it securely
- Presses Enter

INPUT:
- No parameters required (assumes 'sudo_pass' is the key)

OUTPUT:
- message: Success/failure status

EXAMPLE:
type_text("sudo apt update", enter=True)
time.sleep(1)
handle_sudo()""",
            "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Status message"},
                },
                "required": ["message"],
            },
        },
        {
            "name": "find_image",
            "description": """Find a UI element on screen using an image template.

WHEN TO USE:
- Locating specific icons, buttons, or images
- When 'perceive' is too slow or imprecise
- Verifying an element exists

HOW IT WORKS:
- Takes a template image path
- Scans the current screen for matches
- Returns coordinates of matches

INPUT:
- template_path: Path to the image file to look for
- confidence: Match threshold 0.0-1.0 (default: 0.8)

OUTPUT:
- matches: List of found locations with coordinates

EXAMPLE:
find_image(template_path="/home/user/templates/save_icon.png")""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "template_path": {
                        "type": "string",
                        "description": "Path to the template image file",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Match threshold (0.0 to 1.0)",
                    },
                },
                "required": ["template_path"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "matches": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "center_x": {"type": "integer"},
                                "center_y": {"type": "integer"},
                                "confidence": {"type": "number"},
                            }
                        },
                        "description": "List of matches found",
                    },
                },
                "required": ["matches"],
            },
        },
        {
            "name": "wait_for_image",
            "description": """Wait until a specific image appears on the screen.

WHEN TO USE:
- Waiting for an app to load
- Waiting for a process to complete (e.g., "Done" checkmark)
- Synchronizing actions with UI state

HOW IT WORKS:
- Repeatedly calls 'find_image'
- Returns when a match is found or timeout is reached

INPUT:
- template_path: Path to the image file
- timeout: Max seconds to wait (default: 10)
- confidence: Match threshold (default: 0.8)

OUTPUT:
- success: True if found, False if timed out
- match: The found match details

EXAMPLE:
launch_app("firefox")
wait_for_image(template_path="firefox_logo.png", timeout=15)""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "template_path": {
                        "type": "string",
                        "description": "Path to the template image file",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Maximum seconds to wait",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Match threshold (0.0 to 1.0)",
                    },
                },
                "required": ["template_path"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "match": {"type": "object", "description": "Details of the found match"},
                },
                "required": ["success"],
            },
        },
        {
            "name": "run_terminal_cmd",
            "description": """Run a shell command in the background and return the output.

WHEN TO USE:
- Checking system status (e.g., 'uptime', 'df -h')
- Running CLI tools that don't need interaction
- Getting file information
- Checking if a process is running ('pgrep')

HOW IT WORKS:
- Executes command in a subprocess shell
- Captures stdout and stderr
- Returns output after command completes (or times out)

INPUT:
- command: The shell command to run

OUTPUT:
- stdout: Standard output
- stderr: Standard error
- returncode: Exit code (0 = success)

EXAMPLE:
run_terminal_cmd(command="date")""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute",
                    },
                },
                "required": ["command"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "stdout": {"type": "string"},
                    "stderr": {"type": "string"},
                    "returncode": {"type": "integer"},
                },
                "required": ["stdout", "returncode"],
            },
        },
        {
            "name": "check_notification",
            "description": """Check for recent system notifications (Linux).

WHEN TO USE:
- Verifying if an app sent a notification (e.g., "New Message")
- Waiting for a long process to finish
- Monitoring system alerts

HOW IT WORKS:
- Uses 'dbus-monitor' to listen for notification events
- Returns the most recent notification if found

INPUT:
- timeout: How long to listen in seconds (default: 5)

OUTPUT:
- found: True/False
- title: Notification title
- body: Notification body text

EXAMPLE:
check_notification(timeout=10)""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Seconds to listen for notifications",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "found": {"type": "boolean"},
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["found"],
            },
        },
        {
            "name": "use_skill",
            "description": """Execute a high-level application skill.

WHEN TO USE:
- Performing complex, multi-step actions in supported apps
- Sending messages on Signal or WhatsApp
- Executing predefined workflows

HOW IT WORKS:
- Looks up the named skill in the registry
- Executes the skill with provided parameters
- Handles app launching and navigation automatically

INPUT:
- skill: Name of the skill (e.g., "signal:send", "whatsapp:send")
- params: Dictionary of parameters required by the skill

OUTPUT:
- success: True/False
- message: Result description

AVAILABLE SKILLS:
- signal:send (contact, message)
- whatsapp:send (contact, message)

EXAMPLE:
use_skill(skill="signal:send", params={"contact": "Alice", "message": "Hi!"})""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "skill": {
                        "type": "string",
                        "description": "Name of the skill to execute",
                    },
                    "params": {
                        "type": "object",
                        "description": "Parameters for the skill",
                    },
                },
                "required": ["skill", "params"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                },
                "required": ["success", "message"],
            },
        },
        {
            "name": "get_agent_history",
            "description": """Retrieve the history of recent actions performed by the agent.

WHEN TO USE:
- Debugging why a previous action failed
- Checking what was just done (e.g., "Did I already click that?")
- Verifying the sequence of operations

HOW IT WORKS:
- Returns a list of the most recent tool executions
- Includes tool name, parameters, result, and success status

INPUT:
- limit: Number of recent actions to retrieve (default: 10)

OUTPUT:
- history: List of action logs (newest first)

EXAMPLE:
get_agent_history(limit=5)""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent actions to retrieve",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "history": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {"type": "number"},
                                "tool_name": {"type": "string"},
                                "success": {"type": "boolean"},
                                "result": {"type": "object"},
                            }
                        },
                    },
                },
                "required": ["history"],
            },
        },
    ]

# From Zero to Agent: A Non-Programmer's Illustrated Guide to Building AI with Google ADK

---

## Part 1: Understanding the Minds of AI Agents

### 1.1 The Modern AI Assistant, Demystified

At its core, an Artificial Intelligence (AI) agent is a sophisticated software program designed to act on a user's behalf to achieve specific goals.

A helpful analogy: **an AI agent is like a hyper-competent intern**. You give it a high-level goal (e.g., "plan my business trip to Tokyo"), provide access to tools (browser, calendar, database), and grant autonomy to figure out the steps.

**Key differences from chatbots:**
- Chatbots: rigid, rule-based, respond to keywords.
- AI agents: dynamic, analyze environment, adapt, and learn.

#### The Perception-Reasoning-Action Loop

The agent operates in a continuous cycle:

1. **Goal Setting & Planning:** Receives a high-level objective, breaks it into actionable steps.
2. **Perception (Sensing):** Gathers data using tools (APIs, databases, sensors).
3. **Reasoning & Decision-Making:** Uses an LLM (e.g., Gemini) to analyze data and decide next actions.
4. **Action (Actuating):** Executes decisions via actuators (APIs, emails, physical movements).
5. **Learning & Improvement:** Learns from feedback, refines strategies, and improves over time.

---

### 1.2 A Tour of Agent Architectures

Agents vary in complexity. Their architectures form an evolutionary ladder:

| Agent Type            | Core Characteristic                            | Memory Usage                | Decision Basis                        | Real-World Analogy                                 |
|-----------------------|------------------------------------------------|-----------------------------|---------------------------------------|----------------------------------------------------|
| Simple Reflex         | Reacts to current stimuli, fixed rules         | None                        | Current perception only               | Thermostat turning on the heat                     |
| Model-Based Reflex    | Tracks state with internal model               | Short-term memory           | Perception + internal model           | Robot vacuum remembering cleaned areas             |
| Goal-Based            | Plans actions to achieve a goal                | Goal & planned steps        | Future outcomes related to goal       | GPS app calculating a route                        |
| Utility-Based         | Maximizes "utility" or happiness metric        | Goals & preferences         | Optimal outcome via utility function  | GPS optimizing for speed, cost, traffic            |
| Learning              | Improves via feedback                          | Long-term experience        | Past successes and failures           | Netflix recommendation engine                      |
| Multi-Agent System    | Team of agents collaborating                   | Individual/shared memory    | Delegation, coordination, negotiation | Travel specialists booking flights, hotels, tours   |

---

## Part 2: Your Toolkit: An Introduction to Google's Agent Development Kit (ADK)

### 2.1 What is ADK and Why Should You Care?

Google's ADK is an open-source toolkit for building, evaluating, and deploying AI agents. It uses Python and is model-agnostic (works with Gemini, OpenAI, Anthropic, etc.).

**Code-first approach:** ADK understands agent capabilities via natural language docstrings in code, making it accessible for non-programmers.

---

### 2.2 The Core Components of ADK

- **Agents:** Workers of the system.
    - `LlmAgent`: Thinker/specialist, uses LLM for reasoning.
    - `WorkflowAgent`: Manager/foreman, orchestrates other agents.
- **Tools:** Equipment for perception and action.
    - Built-in (e.g., `google_search`)
    - Custom (Python functions with docstrings)
- **Sessions & State:** Memory system for context.
- **Runner:** Engine managing the interaction lifecycle.

---

## Part 3: Your First Build: The "Hello, World!" Weather & Traffic Agent

### 3.1 Preparing Your Workshop: Environment Setup

**Step-by-step:**
1. **Create a Google Cloud Project**
2. **Enable Billing and APIs** (Vertex AI API)
3. **Obtain an API Key** (Google AI Studio)
4. **Install Python and Google ADK**
     ```bash
     pip install google-adk
     ```
5. **Set Up a Virtual Environment**
     ```bash
     python -m venv .venv
     # Activate:
     # Windows: .venv\Scripts\activate.bat
     # macOS/Linux: source .venv/bin/activate
     ```

---

### 3.2 Blueprint of an Agent: Project Structure

```
parent_folder/
    multi_tool_agent/
        __init__.py
        agent.py
    .env
```

- `__init__.py`: Makes the folder a Python package.
- `.env`: Stores API keys.
- `agent.py`: Main blueprint.

---

### 3.3 Crafting Your First Tools

**agent.py:**

```python
import datetime
from zoneinfo import ZoneInfo

def get_weather(city: str) -> dict:
        """
        Retrieves the current weather report for a specified city.
        Args:
                city (str): City name.
        Returns:
                dict: Weather info.
        """
        # Mock data
        city_normalized = city.lower()
        if "new york" in city_normalized:
                return {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."}
        elif "london" in city_normalized:
                return {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."}
        else:
                return {"status": "success", "report": f"The weather in {city} is pleasant today."}

def get_current_time(timezone: str) -> dict:
        """
        Gets the current time for a given IANA timezone.
        Args:
                timezone (str): IANA timezone name.
        Returns:
                dict: Current time or error.
        """
        try:
                now = datetime.datetime.now(ZoneInfo(timezone))
                return {"status": "success", "time": now.strftime("%H:%M:%S")}
        except Exception as e:
                return {"status": "error", "message": f"Invalid timezone '{timezone}'. Error: {str(e)}"}
```

---

### 3.4 Assembling the Agent

```python
from google.adk.agents import Agent

root_agent = Agent(
        name="weather_and_time_agent",
        model="gemini-2.0-flash",
        description="An assistant that provides current weather and time for various cities.",
        instruction="""
        You are a friendly and helpful assistant.
        - Use get_weather for weather questions.
        - Use get_current_time for time questions.
        - Infer IANA timezone from city names.
        - Handle requests needing both tools.
        """,
        tools=[get_weather, get_current_time],
)
```

---

### 3.5 Launch and Test: Using the ADK Web UI

1. Navigate to `parent_folder`.
2. Activate `.venv`.
3. Run:
     ```bash
     adk web
     ```
4. Open the displayed URL in a browser.
5. Select `multi_tool_agent` and interact via chat.

---

## Part 4: Advanced Project I: The Automated Content Editing Team

### 4.1 The Assembly Line Pattern: Introducing Sequential Agents

Use `SequentialAgent` to orchestrate a team of specialist agents for multi-step workflows (e.g., research, drafting, editing).

---

### 4.2 Building the Team: Three Specialist Agents

**agent.py:**

```python
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search

# Agent 1: Researcher
researcher_agent = Agent(
        name="researcher_agent",
        model="gemini-2.0-pro",
        instruction="""
        You are a research assistant. Find 3-5 key facts using Google Search.
        Summarize findings in bullet points.
        """,
        tools=[google_search],
        output_key="research_summary"
)

# Agent 2: Writer
writer_agent = Agent(
        name="writer_agent",
        model="gemini-2.0-pro",
        instruction="""
        You are a content writer. Use 'research_summary' from session state to write a 300-word draft.
        """,
        output_key="draft_article"
)

# Agent 3: Editor
editor_agent = Agent(
        name="editor_agent",
        model="gemini-2.0-pro",
        instruction="""
        You are a skilled editor. Refine 'draft_article' for grammar, clarity, and tone.
        Produce a polished final version.
        """
)

# Manager Agent
root_agent = SequentialAgent(
        name="content_creation_pipeline",
        description="A multi-agent pipeline for creating high-quality written content.",
        sub_agents=[researcher_agent, writer_agent, editor_agent]
)
```

---

### 4.3 Orchestration and Execution

Run `adk web` and select `content_creation_pipeline`. A prompt like "Write an article about the impact of AI on the job market" triggers the full workflow.

---

## Part 5: Advanced Project II: A Voice for the Physical World - The Raspberry Pi Robot Controller

### 5.1 Bridging Worlds: Hardware Setup and Preparation

**Components:**
- Raspberry Pi (Model 4/5)
- SG90 Micro Servo Motor
- Breadboard, jumper wires
- External 5V power supply

**Wiring:**
- Servo Red → 5V power
- Servo Brown/Black → Power ground
- Pi Ground → Power ground (common ground)
- Servo Orange/Yellow → Pi GPIO (e.g., GPIO17)

---

### 5.2 Teaching the Pi to Move: Python for GPIO Control

**Install gpiozero:**
```bash
sudo apt-get update
sudo apt-get install python3-gpiozero
```

**Test Script (`servo_test.py`):**
```python
from gpiozero import Servo
from time import sleep

servo = Servo(17)
servo.min(); sleep(2)
servo.mid(); sleep(2)
servo.max(); sleep(2)
servo.mid()
```

Run: `python3 servo_test.py`

---

### 5.3 Creating the Robot's Senses: ADK Tools for Physical Actions

**On Raspberry Pi:**

- `move_script.py`:
        ```python
        import sys
        from gpiozero import Servo
        angle = int(sys.argv[1])
        value = angle / 90.0
        servo = Servo(17)
        servo.value = value
        ```

- `wave_script.py`:
        ```python
        from gpiozero import Servo
        from time import sleep
        servo = Servo(17)
        for _ in range(3):
                servo.min(); sleep(0.3)
                servo.max(); sleep(0.3)
        servo.mid()
        ```

**On Development Computer (`agent.py`):**

```python
import os
PI_ADDRESS = "pi@192.168.1.101"

def move_servo(angle: int) -> str:
        """
        Moves the servo motor to a specific angle between -90 and 90 degrees.
        """
        command = f"ssh {PI_ADDRESS} 'python3 /home/pi/move_script.py {angle}'"
        os.system(command)
        return f"Command sent to move servo to {angle} degrees."

def wave_hand() -> str:
        """
        Makes the robot arm perform a waving motion.
        """
        command = f"ssh {PI_ADDRESS} 'python3 /home/pi/wave_script.py'"
        os.system(command)
        return "Command sent to wave hand."
```

---

### 5.4 The Final Assembly: The Robot Control Agent

```python
from google.adk.agents import Agent

root_agent = Agent(
        name="robot_controller_agent",
        model="gemini-2.0-pro",
        description="An agent that controls a simple Raspberry Pi robot arm via natural language.",
        instruction="""
        You are the controller for a physical robot arm.
        - Use wave_hand for waving/hello.
        - Use move_servo for specific positions/angles (-90 to 90).
        - Confirm actions to the user.
        """,
        tools=[move_servo, wave_hand]
)
```

---

### 5.5 Bringing It to Life

1. Prepare hardware and Pi.
2. On development computer, run:
     ```bash
     adk web --host 0.0.0.0
     ```
3. Find your computer's local IP address.
4. On another device, open `http://<YOUR_COMPUTER_IP_ADDRESS>:8000`.
5. Select `robot_controller_agent` and send commands like:
        - "Wave to me!"
        - "Move the arm to 45 degrees."
        - "Point the arm all the way to the left."
        - "Reset the arm to the center position."

---

This guide demonstrates building, testing, and deploying AI agents with Google ADK, from simple assistants to multi-agent workflows and physical robot control.

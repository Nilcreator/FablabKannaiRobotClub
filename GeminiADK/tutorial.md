# From Zero to Agent: A Non-Programmer's Illustrated Guide to Building AI with Google ADK

## Part 1: Understanding the Minds of AI Agents

### 1.1 The Modern AI Assistant, Demystified

At its core, an **Artificial Intelligence (AI) agent** is a sophisticated software program designed to act on a user's behalf to achieve specific goals.<sup>1</sup> A helpful analogy is to think of an AI agent as a hyper-competent intern. A user can give this intern a high-level goal, such as "plan my upcoming business trip to Tokyo," provide them with access to necessary tools (like a web browser for flight research, a calendar application for scheduling, and a database of corporate travel policies), and grant them the autonomy to figure out the specific steps required to accomplish the task.<sup>3</sup> This capability fundamentally distinguishes an AI agent from a simple chatbot. While a traditional chatbot follows a rigid, pre-programmed set of rules and can only respond to specific keywords, an AI agent can dynamically analyze its environment, adapt to new information, and improve its performance over time through experience.<sup>4</sup>

The operation of an AI agent is best understood as a continuous, cyclical process, often referred to as the **perception-reasoning-action loop**.<sup>5</sup> This cycle enables the agent to interact with its environment intelligently and autonomously. The process consists of five key stages:

- **Goal Setting & Planning:** The cycle begins when the agent receives a high-level objective from a user or system. The agent's first task is to decompose this broad goal into a series of smaller, actionable steps. For example, the goal "plan my trip" might be broken down into sub-tasks like "research flights to Tokyo," "find hotel availability," "check calendar for conflicts," and "book arrangements".<sup>2</sup> Advanced agents can even adjust this plan on the fly if they encounter new information, such as a flight becoming unavailable.<sup>5</sup>
- **Perception (Sensing):** To make informed decisions, the agent must gather data about its environment. This is the perception or sensing phase. An agent's "senses" are its tools, which can include Application Programming Interfaces (APIs) for accessing web services, connections to internal databases, or even physical sensors if the agent is controlling a robot.<sup>7</sup> For the trip-planning agent, perception would involve using tools to check real-time flight prices, hotel booking systems, and the user's digital calendar.<sup>5</sup>
- **Reasoning & Decision-Making:** This stage represents the "brain" of the agent. Here, a Large Language Model (LLM), such as Google's Gemini, processes the information gathered during the perception phase.<sup>1</sup> The LLM analyzes the data, applies logic, and decides on the most appropriate next action to take to move closer to its goal. For instance, after perceiving that the user's preferred flight is too expensive, the LLM might reason that it should search for alternative dates or airlines.<sup>2</sup> This component is where the agent's intelligence truly resides, allowing it to handle complex, multi-step tasks that require more than simple text generation.<sup>3</sup>
- **Action (Actuating):** Once a decision is made, the agent must execute it. This is the action or actuating phase. The agent's "hands and voice" are its actuators, which translate decisions into tangible operations in its environment.<sup>7</sup> An action could be digital, such as calling a booking API to reserve a flight, sending an email confirmation, or generating a text response for the user. In a physical system like a robot, an action could be a physical movement, such as rotating an arm or gripping an object.<sup>8</sup>
- **Learning & Improvement:** AI agents are designed to learn from their interactions. Each completed cycle provides a feedback opportunity. The agent stores information from past interactions in its memory, allowing it to refine its strategies over time. If a user corrects an agent's action, this feedback can be used to adjust its underlying algorithms, making it more effective in the future. This continuous learning loop is what enables agents to become increasingly proficient and autonomous.<sup>4</sup>

Through this iterative cycle of planning, perceiving, reasoning, acting, and learning, AI agents can tackle complex problems, drive operational efficiency, and provide sophisticated, personalized assistance across a vast range of applications, from customer support and e-commerce to financial analysis and scientific research.<sup>3</sup>

### 1.2 A Tour of Agent Architectures

Not all AI agents are created with the same level of complexity or capability. Their architectures can be understood as an evolutionary ladder, with each step adding more sophisticated features like memory, planning, and learning. Understanding these different types provides a clear framework for appreciating the power of modern agentic systems.<sup>4</sup>

- **Simple Reflex Agents:** These are the most basic type of agent. They operate purely on a "condition-action" basis, reacting to their current perception of the environment without any memory of past events.<sup>8</sup> A real-world analogy is a simple thermostat; if the current temperature (perception) drops below a set point (condition), it triggers the heating system (action). It has no knowledge of what the temperature was an hour ago or what it might be in the future.<sup>10</sup>
- **Model-Based Reflex Agents:** This type of agent is a step up in sophistication. It maintains an internal "model" or representation of the world, which allows it to keep track of the state of its environment even when it cannot perceive everything at once.<sup>10</sup> A robot vacuum cleaner is a good example. It builds a map of the room as it cleans (the internal model) and remembers which areas it has already covered. This memory prevents it from getting stuck in a repetitive loop and allows it to operate effectively in a partially observable environment.<sup>10</sup>
- **Goal-Based Agents:** Unlike reflex agents that simply react, goal-based agents are proactive. They are given a specific goal and can plan a sequence of actions to achieve it.<sup>7</sup> A GPS navigation system exemplifies this architecture. When a user enters a destination (the goal), the system considers various possible routes, plans the optimal sequence of turns, and guides the user accordingly. If it encounters a roadblock, it can re-plan to find an alternative path to the goal.<sup>10</sup>
- **Utility-Based Agents:** These agents refine the goal-based approach by considering the quality of the outcome. When multiple paths can lead to the same goal, a utility-based agent evaluates the trade-offs to select the best possible option based on a "utility function," which measures desirability.<sup>7</sup> An advanced navigation app that optimizes for more than just speed is a perfect analogy. It might weigh factors like fuel efficiency, toll costs, and traffic congestion to recommend a route that maximizes overall utility for the user, not just the one that is fastest.<sup>10</sup>
- **Learning Agents:** This architecture introduces the ability to improve over time. Learning agents can analyze the outcomes of their past actions, incorporate feedback, and adapt their decision-making processes to enhance future performance.<sup>4</sup> A media recommendation engine, such as those used by streaming services, is a prime example. It learns a user's preferences by observing their viewing history and ratings, and it continuously refines its suggestions to become more accurate and personalized over time.<sup>4</sup>
- **Hierarchical & Multi-Agent Systems (MAS):** These are the most complex and powerful architectures, representing a "team of specialist agents" working together to solve a problem.<sup>7</sup> In a hierarchical system, a high-level "manager" agent breaks a complex task into sub-tasks and delegates them to specialized lower-level agents. For instance, a master travel agent might delegate the task of "cancel trip" to a flight-cancellation agent and a hotel-cancellation agent, then collect their reports to confirm the overall task is complete.<sup>7</sup> This collaborative approach, where multiple agents coordinate their actions, is essential for tackling highly complex, multi-faceted problems and forms the basis for many advanced AI applications.<sup>6</sup>

The following table provides a clear summary of these agent types, grounding each abstract concept in a familiar, real-world analogy.

| Agent Type | Core Characteristic | Memory Usage | Decision Basis | Simple Real-World Analogy |
| :--- | :--- | :--- | :--- | :--- |
| **Simple Reflex** | Reacts to current stimuli based on fixed rules. | None | Current perception only. | A thermostat turning on the heat. |
| **Model-Based Reflex** | Uses an internal model to track the state of the world. | Short-term memory of the environment's state. | Current perception and internal model. | A robot vacuum remembering where it has cleaned. |
| **Goal-Based** | Plans sequences of actions to achieve a specific goal. | Memory of goal and planned steps. | Future outcomes related to the goal. | A GPS app calculating a route to a destination. |
| **Utility-Based** | Chooses actions to maximize a "utility" or happiness metric. | Memory of goals and preferences. | Optimal outcome based on multiple factors. | An advanced GPS finding the cheapest and fastest route. |
| **Learning** | Improves its performance over time based on feedback. | Long-term memory of past experiences. | Analysis of past successes and failures. | A Netflix recommendation engine. |
| **Multi-Agent System** | A team of agents collaborating to solve a complex task. | Individual and sometimes shared memory. | Delegation, coordination, and negotiation. | A team of travel specialists booking flights, hotels, and tours. |

## Part 2: Your Toolkit: An Introduction to Google's Agent Development Kit (ADK)

### 2.1 What is ADK and Why Should You Care?

Google's **Agent Development Kit (ADK)** is an open-source toolkit designed to simplify the process of building, evaluating, and deploying sophisticated AI agents.<sup>12</sup> It provides a flexible and modular framework, primarily using the **Python** programming language, that makes the creation of complex agentic systems feel more like traditional software development.<sup>13</sup> While it is optimized to work seamlessly with Google's **Gemini** family of models and the broader Google Cloud ecosystem, ADK is fundamentally model-agnostic, meaning it can be used with models from other providers like **OpenAI** or **Anthropic**.<sup>15</sup>

A key characteristic of ADK is its **"code-first"** development approach.<sup>12</sup> For individuals without a programming background, this term might seem intimidating. However, the way ADK implements this philosophy makes it uniquely accessible. The framework is intelligently designed to understand an agent's capabilities not by analyzing complex programming logic, but by reading the natural language descriptions provided within the code itself.

When defining a tool for an agent in ADK, the most critical components are the function's name, its parameters, and, most importantly, its documentation string (or **"docstring"**). This docstring is a plain English description of what the tool does, what inputs it needs, and what it produces.<sup>16</sup> The ADK framework reads this English text and automatically generates a technical schema that the LLM—the agent's "brain"—can understand and use.<sup>18</sup>

This means that the primary task for a non-technical builder is not to write complex code, but to write a clear and precise job description for the AI agent's tools. The process can be simplified into following a simple, repeatable recipe for a Python function, where the main effort is focused on crafting an effective English description in the docstring. This approach transforms the potentially daunting act of "coding" into the more familiar and manageable task of "writing clear instructions," bridging the gap between a powerful, code-first framework and a non-technical user.

### 2.2 The Core Components of ADK

An application built with Google ADK is composed of several key building blocks that work together to create a functional agent. Understanding these components is the first step toward building your own systems.<sup>14</sup>

- **Agents:** These are the fundamental "workers" of the system. ADK provides different types of agents for different purposes, with two primary categories being central to most applications <sup>21</sup>:
    - `LlmAgent`: This is the "thinker" or "specialist" agent. It uses a Large Language Model (like Gemini) as its core reasoning engine to understand user requests, plan steps, and decide which of its available tools to use to accomplish a task. Most of the agents that perform specific actions will be of this type.
    - `WorkflowAgent`: This is the "manager" or "foreman" agent. Instead of reasoning with an LLM, its job is to orchestrate other agents in a predefined, deterministic pattern. A common example is the `SequentialAgent`, which directs a series of specialist agents to execute their tasks in a specific order, like an assembly line.<sup>21</sup>
- **Tools:** These are the "equipment" an agent uses to perceive its environment and perform actions. Tools are what give an agent its power, allowing it to interact with the world beyond simply generating text.<sup>23</sup> ADK supports several types of tools:
    - **Built-in Tools:** These are pre-packaged capabilities provided by ADK for common tasks. A prime example is the `google_search` tool, which allows an agent to search the web for real-time information with minimal setup.<sup>24</sup>
    - **Custom Tools:** These are the tools that users define themselves. As discussed, a simple Python function with a clear docstring can be passed directly to an agent to become a custom tool, enabling it to perform any action that can be scripted, such as calling a specific API or interacting with a database.<sup>23</sup>
- **Sessions & State:** This is the agent's "memory" system, which allows it to maintain context during a conversation.
    - A **Session** represents a single, continuous interaction or conversation with a user. It tracks the history of messages and events within that conversation.<sup>14</sup>
    - The **State** is the short-term, "scratchpad" memory associated with a session. It's a place where the agent can store and retrieve key-value information during the conversation, such as user preferences or the results from a previous tool call. This is how information is passed between different steps in a workflow.<sup>14</sup>
- **Runner:** This component acts as the "engine" of the ADK application. The Runner is responsible for managing the entire interaction lifecycle. It connects the user's input with the appropriate agent, manages the session and its state, orchestrates the execution of the agent's logic and tool calls, and streams the events back to the user interface.<sup>15</sup> It is the central piece that ties all the other components together.

### 2.3 The ADK Ecosystem: Available Models and Tools

The power of an ADK agent comes from the "brain" it uses (the LLM) and the "equipment" it has access to (the tools). ADK is designed to be flexible, supporting a wide range of models and an extensible tool system.

#### Available Gemini Models

ADK is optimized for Google's Gemini family of models, offering a spectrum of options to balance performance, cost, and specific capabilities like handling multimodal inputs (text, images, audio, video). <sup>49</sup>

| Model Name | Description | Optimized For |
| :--- | :--- | :--- |
| **`gemini-2.5-pro`** | The most advanced and capable reasoning model in the Gemini family. <sup>49</sup> | Complex problem-solving, advanced coding, and multimodal understanding. <sup>50</sup> |
| **`gemini-2.5-flash`** | A powerful model that balances performance and cost-efficiency. <sup>50</sup> | Adaptive thinking and well-rounded capabilities for a wide range of tasks. <sup>50</sup> |
| **`gemini-2.0-flash`** | A fast and capable multimodal model. <sup>51</sup> | Speed, real-time streaming, and next-generation features. <sup>50</sup> |
| **`gemini-2.5-flash-lite`** | The most cost-effective model, designed for high-throughput tasks. <sup>50</sup> | High-volume, low-latency applications where cost is a primary factor. <sup>50</sup> |

#### Integrated Google Tools

ADK provides a rich ecosystem of tools that allow agents to interact with the world. These can be broadly categorized: <sup>23</sup>

- **Built-in Tools:** These are ready-to-use tools provided directly by the ADK framework for common, essential tasks. <sup>53</sup>
    - `google_search`: Allows an agent to perform a web search to access real-time, up-to-date information from the internet. This tool is only compatible with Gemini 2 models. <sup>53</sup>
    - `Code Execution`: Enables an agent to run Python code snippets, which is incredibly useful for data analysis, calculations, or generating visualizations. <sup>54</sup>
- **Google Cloud Tools:** These tools allow agents to connect securely to and interact with various Google Cloud services, unlocking enterprise-grade capabilities. <sup>55</sup>
    - **Application Integration Toolset:** This powerful toolset allows agents to connect to over 100 pre-built connectors for enterprise systems like Salesforce, SAP, and ServiceNow, as well as custom APIs hosted in Apigee. <sup>55</sup>
    - **BigQuery:** Agents can be equipped with a BigQuery tool that translates natural language questions (e.g., "What were our top 5 products last quarter?") into SQL queries, executes them, and summarizes the results. <sup>52</sup>
    - **Vertex AI Search:** This tool enables an agent to perform Retrieval-Augmented Generation (RAG) by querying private data stores and knowledge bases within an organization. <sup>54</sup>

## Part 3: Your First Build: The "Hello, World!" Weather & Traffic Agent

### 3.1 Preparing Your Workshop: Environment Setup

The setup process is often the most significant hurdle for newcomers. This section provides an exhaustive, step-by-step guide to preparing the development environment. Each step is explained with its purpose to build a clear understanding and ensure a smooth start.

#### Step 1: Create a Google Cloud Project

A Google Cloud project is like a dedicated office space for an agent. It's where all its resources, permissions, and billing are organized.

1. Sign in to the **Google Cloud Console**. If a user is new to Google Cloud, they can create an account, which often comes with free credits for experimentation.<sup>26</sup>
2. On the project selector page, click **"CREATE PROJECT."**
3. Give the project a memorable name (e.g., "My First ADK Agent") and click **"CREATE."** The system will assign a unique Project ID.<sup>27</sup>

#### Step 2: Enable Billing and APIs

This step is akin to turning on the power and utilities in the agent's office.

1. Ensure the newly created project is selected in the console.
2. Navigate to the **"Billing"** section and verify that a billing account is linked to the project. While many services have a generous free tier, a billing account is required to enable APIs.<sup>26</sup>
3. Use the search bar at the top of the console to find **"Vertex AI API."**
4. Select the Vertex AI API from the search results and click the **"ENABLE"** button. This grants the project access to Google's powerful AI models, which will serve as the agent's brain.<sup>26</sup>

#### Step 3: Obtain a Google AI API Key

An API key is like the secret key to the office door, allowing the agent to securely access the AI services.

1. Navigate to **Google AI Studio** at `aistudio.google.com`.<sup>28</sup>
2. Sign in with the same Google account.
3. Click on **"Get API key"** and then **"Create API key in new project."**
4. Select the Google Cloud project created in Step 1 from the dropdown menu.
5. The system will generate an API key. Copy this key and save it in a secure location, like a password manager. This key should be treated like a password and never shared publicly.<sup>30</sup>

#### Step 4: Obtain an OpenWeatherMap API Key

To get real-time weather data, our agent will use the OpenWeatherMap service, which offers a free plan that is perfect for this project.

1. Go to the **OpenWeatherMap website** (`openweathermap.org`) and create a free account. <sup>56</sup>
2. After signing in, navigate to your account page to find your API keys. <sup>57</sup>
3. Copy your default API key. It may take a few minutes to become active.

#### Step 5: Install Python and Google ADK

This step involves stocking the workshop with the necessary tools and raw materials.

1. **Install Python:** ADK requires Python 3.10 or newer.<sup>26</sup> If Python is not already installed, it can be downloaded from the official Python website (`python.org`). During installation on Windows, it is crucial to check the box that says "Add Python to PATH."
2. **Create a Project Folder:** On the computer, create a new folder for the project (e.g., `adk-projects`).
3. **Open a Terminal:**
     - **Windows:** Open the Start Menu, type `cmd`, and press Enter.
     - **macOS:** Open Finder, go to Applications > Utilities, and open Terminal.
     - **Linux:** Open the application launcher and find Terminal.
4. **Navigate to the Project Folder:** In the terminal, use the `cd` (change directory) command to navigate into the folder created in the previous step. For example: `cd path/to/adk-projects`.
5. **Install Google ADK and Dependencies:** With the terminal open in the project folder, run the following command. This will download and install the Agent Development Kit library, along with the `requests` library we'll need for making API calls. <sup>56</sup>
     ```bash
     pip install google-adk requests
     ```

#### Step 6: Set Up a Virtual Environment

A virtual environment keeps the project's tools neatly organized and separate from other projects, preventing conflicts.

1. **Create the Virtual Environment:** In the terminal (still inside the `adk-projects` folder), run the following command to create a virtual environment named `.venv` <sup>26</sup>:
     ```bash
     python -m venv .venv
     ```
2. **Activate the Virtual Environment:** This "steps into" the isolated environment. The command differs by operating system <sup>26</sup>:
     - **Windows (CMD):**
         ```
         .venv\Scripts\activate.bat
         ```
     - **macOS / Linux:**
         ```bash
         source .venv/bin/activate
         ```
     After activation, the terminal prompt will typically show `(.venv)` at the beginning, indicating that the virtual environment is active. This activation step must be performed every time a new terminal is opened to work on the project.

### 3.2 Blueprint of an Agent: Project Structure

With the environment ready, the next step is to lay out the blueprint for the agent by creating a specific folder and file structure. This organization is standard for ADK projects and helps the framework locate and run the agent correctly.<sup>29</sup>

Inside the `adk-projects` folder, create the following structure:

```
parent_folder/
├── multi_tool_agent/
│   ├── __init__.py
│   └── agent.py
└── .env
```

Here is what each file and folder is for:

- `parent_folder/`: This is the main directory for this specific agent project. It can be named anything (e.g., `weather-agent-project`). The terminal should be open in this directory when running the agent later.
- `multi_tool_agent/`: This folder contains the agent's source code. The name of this folder is important, as ADK will use it to identify the agent.
- `__init__.py`: This is a special, often empty, file that tells Python to treat the `multi_tool_agent` folder as a "package" or a collection of code modules. Create this file and add the following single line of code to it. This line makes the agent defined in `agent.py` accessible.<sup>29</sup>
    ```python
    from . import agent
    ```
- `.env`: This is the "secret file" where the API keys will be stored. Storing sensitive information here keeps it separate from the main code, which is a critical security practice. Create this file and add the following lines, replacing the placeholder text with the actual keys you obtained. <sup>56</sup>
    ```
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    GOOGLE_API_KEY=PASTE_YOUR_GOOGLE_API_KEY_HERE
    OPENWEATHER_API_KEY=PASTE_YOUR_OPENWEATHER_API_KEY_HERE
    ```
- `agent.py`: This is the "main blueprint" file. It is where the agent's tools will be defined and the agent itself will be assembled. This file will be created and filled in the next sections.

### 3.3 Crafting Your First Tools

Now it is time to give the agent its capabilities. This will be done by defining two Python functions in the `agent.py` file. The `get_weather` function will now call the live OpenWeatherMap API to fetch real-time data. <sup>56</sup>

The user's primary task here is to write the docstrings—the text enclosed in triple quotes (`"""..."""`). These descriptions are what the LLM will read to understand how to use the tools.<sup>16</sup>

Open the `agent.py` file in a text editor and add the following code:

```python
# agent.py
import datetime
import os
import requests
from zoneinfo import ZoneInfo

def get_weather(city: str) -> dict:
        """
        Retrieves the current weather report for a specified city using the OpenWeatherMap API.
        This tool is used to answer questions about real-time weather conditions.

        Args:
                city (str): The name of the city for the weather report, for example "New York" or "London".

        Returns:
                dict: A dictionary containing the weather information, including a status and a report.
        """
        print(f"--- Tool: get_weather called for city: {city} ---")
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
                return {"status": "error", "report": "OpenWeatherMap API key not found in environment variables."}

        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": api_key, "units": "metric"}  # Using metric for Celsius

        try:
                response = requests.get(base_url, params=params)
                response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
                data = response.json()

                if data.get("cod") != 200:
                        return {"status": "error", "report": data.get("message", "City not found.")}

                main_weather = data.get("main", {})
                weather_desc = data.get("weather", [{}]).get("description", "N/A")
                temp = main_weather.get("temp", "N/A")
                humidity = main_weather.get("humidity", "N/A")

                report = f"The weather in {city} is {weather_desc} with a temperature of {temp}°C and {humidity}% humidity."
                return {"status": "success", "report": report}
        except requests.exceptions.RequestException as e:
                return {"status": "error", "report": f"API request failed: {e}"}
        except Exception as e:
                return {"status": "error", "report": f"An unexpected error occurred: {e}"}

def get_current_time(timezone: str) -> dict:
        """
        Gets the current time for a given IANA timezone.
        Use this tool when asked for the current time.

        Args:
                timezone (str): The IANA timezone name, such as "America/New_York" or "Europe/London".

        Returns:
                dict: A dictionary containing the current time or an error message.
        """
        print(f"--- Tool: get_current_time called for timezone: {timezone} ---")

        try:
                now = datetime.datetime.now(ZoneInfo(timezone))
                return {"status": "success", "time": now.strftime("%H:%M:%S")}
        except Exception as e:
                return {"status": "error", "message": f"Invalid timezone '{timezone}'. Error: {str(e)}"}
```

### 3.4 Assembling the Agent

With the tools defined, the final step is to assemble the agent. This involves creating an instance of the `Agent` class from the ADK library and providing it with its configuration: a name, the model it should use, its tools, and a set of instructions.

Add the following code to the end of the `agent.py` file:

```python
# agent.py

#... (the get_weather and get_current_time functions from the previous section should be here)...

from google.adk.agents import Agent

# This is the final assembly of our agent.
# It brings together the model, instructions, and tools.
root_agent = Agent(
        name="weather_and_time_agent",
        model="gemini-2.0-flash",
        description="An assistant that provides current weather and time for various cities.",
        instruction="""
        You are a friendly and helpful assistant.
        - To answer questions about the weather, you must use the get_weather tool.
        - To answer questions about the time, you must use the get_current_time tool.
        - If a user asks for the time in a city, infer the correct IANA timezone (e.g., "Paris" is "Europe/Paris").
        - You can handle requests that require using both tools.
        """,
        tools=[get_weather, get_current_time],
)
```

In this block, the `Agent` is configured with:

- `name`: A unique identifier.
- `model`: Specifies the `gemini-2.0-flash` model, a fast and capable model suitable for this task.
- `description`: A short summary of the agent's purpose.
- `instruction`: This is a critical prompt that tells the agent how to behave and when to use its tools.
- `tools`: A list containing the actual Python functions (`get_weather`, `get_current_time`) that the agent is allowed to use.

The `agent.py` file is now complete.

### 3.5 Launch and Test: Using the ADK Web UI

The agent is built; now it is time to bring it to life and interact with it. ADK includes a convenient web-based user interface for local development and testing.

1.  **Navigate to the Correct Directory:** Open a terminal and ensure it is in the `parent_folder` created in section 3.2 (the one that contains the `multi_tool_agent` folder).
2.  **Activate the Virtual Environment:** If it is not already active, activate the `.venv` virtual environment using the commands from section 3.1.
3.  **Run the Web UI:** Execute the following command in the terminal <sup>26</sup>:
        ```bash
        adk web
        ```
4.  **Access the Interface:** The terminal will display a message indicating that the server is running, usually with a local URL like `http://127.0.0.1:8000`. Open this URL in a web browser.
5.  **Interact with the Agent:**
        - In the web UI, there will be a dropdown menu at the top left. Select the agent, which should be listed as `multi_tool_agent`.
        - Use the chat box at the bottom to send messages to the agent. Try prompts like:
            - "What is the weather in London?"
            - "What time is it in New York?"
            - "What is the weather and time in Paris?"
6.  **Inspect the Agent's Thoughts:**
        - On the left side of the UI, click on the **"Events"** tab. This panel provides a real-time log of the agent's internal operations.<sup>29</sup>
        - After sending a prompt, a series of events will appear. Clicking on these events reveals the agent's reasoning process. One can see the initial user query, the model's "thought" process that leads it to decide to use a tool, the exact `functionCall` it makes (including the arguments it decided to use), the `functionResponse` returned by the tool, and finally, the model's generation of the final, user-facing answer.<sup>32</sup> This visual trace is invaluable for understanding how the agent works and for debugging its behavior.

## Part 4: Advanced Project I: The Automated Content Editing Team

### 4.1 The Assembly Line Pattern: Introducing Sequential Agents

Building on the foundation of a single agent, it is possible to create more powerful and structured workflows by composing multiple agents together. This approach is analogous to building a team of specialists, where each member is an expert in a specific task. In ADK, this is achieved using `WorkflowAgents`, particularly the `SequentialAgent`.<sup>14</sup>

A `SequentialAgent` acts as a manager or a foreman for an assembly line. It orchestrates a team of sub-agents, ensuring they execute their tasks in a strict, predefined order. The output of one agent in the sequence automatically becomes the input for the next, allowing for the creation of complex, multi-step pipelines.<sup>33</sup> This pattern is ideal for tasks like content creation, which can be broken down into distinct stages: research, drafting, and editing. By assigning each stage to a specialized agent, the overall quality and consistency of the final output can be significantly improved.

### 4.2 Building the Team: Three Specialist Agents

A core design principle when building complex agentic systems is the creation of specialist agents. Rather than building one monolithic agent that tries to do everything, it is more effective and scalable to build smaller, focused agents that excel at a single responsibility. This modular approach is not just a best practice; it is sometimes a necessity, as certain built-in tools may not be compatible with custom function tools within the same agent.<sup>35</sup>

For the content editing project, a team of three specialist `LlmAgents` will be created. Each will be defined within the `agent.py` file.

- **The Researcher Agent:** This agent's sole purpose is to gather information. It will be equipped with the `google_search` built-in tool, which allows it to access real-time information from the web. Its instructions will direct it to research a given topic and produce a concise, factual summary.<sup>24</sup>
- **The Writer Agent:** This agent is the creative engine of the team. It will not be given any tools. Instead, its instructions will tell it to take the research summary produced by the Researcher Agent and use it to write a compelling first draft of an article. It will access the research summary from the session's shared memory, or state.
- **The Editor Agent:** This agent acts as the quality control specialist. Like the writer, it has no tools. Its job is to take the draft article from the Writer Agent, review it for clarity, tone, grammar, and style, and produce a final, polished version ready for publication.<sup>22</sup>

### 4.3 Orchestration and Execution

With the specialist agents defined, the final step is to assemble them into a cohesive workflow using a `SequentialAgent`. This "manager" agent will define the order of operations and handle the passing of information between the specialists.

A key mechanism for this information transfer is the `output_key` parameter in an agent's definition. When this parameter is set, the final response from that agent is automatically saved to the session state under the specified key. This allows subsequent agents in the sequence to access and build upon the work of their predecessors.<sup>22</sup>

The following code demonstrates how to define the three specialist agents and orchestrate them with a `SequentialAgent`. This code should replace the contents of the `agent.py` file from the previous project.

```python
# agent.py
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search

# Agent 1: The Specialist Researcher
researcher_agent = Agent(
        name="researcher_agent",
        model="gemini-2.0-pro",
        instruction="""
        You are a research assistant. Your goal is to find factual information on a given topic.
        Use the Google Search tool to find 3-5 key facts, statistics, or important points.
        Summarize your findings in a clear, bullet-point list.
        """,
        tools=[google_search],
        output_key="research_summary" # This saves the agent's output to the session state.
)

# Agent 2: The Specialist Writer
writer_agent = Agent(
        name="writer_agent",
        model="gemini-2.0-pro",
        instruction="""
        You are a content writer. Your task is to write a draft article.
        You will be provided with a research summary in the session state under the key 'research_summary'.
        Use this summary to write an engaging and informative draft of about 300 words.
        """,
        output_key="draft_article" # This saves the draft to the session state.
)

# Agent 3: The Specialist Editor
editor_agent = Agent(
        name="editor_agent",
        model="gemini-2.0-pro",
        instruction="""
        You are a skilled editor. Your job is to refine a draft article.
        The draft is available in the session state under the key 'draft_article'.
        Proofread the draft for any grammatical errors, awkward phrasing, or typos.
        Improve the clarity and flow of the text.
        Ensure the tone is professional and engaging.
        Produce the final, polished version of the article.
        """
        # No output_key is needed here, as this is the final agent in the sequence.
)

# The Manager Agent that runs the assembly line
root_agent = SequentialAgent(
        name="content_creation_pipeline",
        description="A multi-agent pipeline for creating high-quality written content.",
        sub_agents=[researcher_agent, writer_agent, editor_agent]
)
```

To run this advanced agent, the process is the same as before: execute `adk web` in the terminal from the `parent_folder`. In the web UI, select the `content_creation_pipeline` agent. Now, a single prompt such as "Write an article about the impact of AI on the job market" will trigger the entire three-step workflow. The user will see the final, edited article as the output, the result of the collaborative effort of the specialized agent team. By inspecting the "Events" tab, one can trace the execution flow from research to drafting to final editing, observing how the state is used to pass the content from one agent to the next.

## Part 5: Advanced Project II: A Voice for the Physical World - The Raspberry Pi Robot Controller

### 5.1 Bridging Worlds: Hardware Setup and Preparation

This project demonstrates how AI agents can interact with the physical world by controlling a simple robot arm built with a Raspberry Pi and a servo motor. The setup requires careful attention to hardware and wiring.

#### Component List:

- **Raspberry Pi:** A Model 4 or 5 is recommended for better performance.
- **Micro Servo Motor:** A common SG90 micro servo is inexpensive and sufficient for this project.
- **Breadboard and Jumper Wires:** For creating the circuit without soldering.
- **External 5V Power Supply:** A dedicated power supply for the servo is crucial. Do not power the servo directly from the Raspberry Pi's GPIO pins, as this can draw too much current and damage the Pi.<sup>37</sup>

#### Raspberry Pi Initial Setup:

1.  **Flash Raspberry Pi OS:** Use the Raspberry Pi Imager tool to flash the latest version of Raspberry Pi OS onto a microSD card.
2.  **Enable SSH:** For "headless" access (without a monitor or keyboard), create an empty file named `ssh` in the boot partition of the microSD card before inserting it into the Pi.
3.  **Configure Wi-Fi:** Create a file named `wpa_supplicant.conf` in the same boot partition and add the network credentials to allow the Pi to connect to Wi-Fi automatically.
4.  **Power On and Connect:** Insert the microSD card, connect the Pi to power, and find its IP address from the router's device list. Connect to the Pi from another computer's terminal using SSH: `ssh pi@<RASPBERRY_PI_IP_ADDRESS>`.<sup>39</sup>

#### Wiring Diagram:

The servo motor has three wires:

- **Brown/Black:** Ground (GND)
- **Red:** Power (+5V)
- **Orange/Yellow:** Signal (PWM)

The connections should be made as follows:

- Connect the servo's **Red** wire to the positive (+) terminal of the external 5V power supply.
- Connect the servo's **Brown/Black** wire to the negative (-) terminal of the external power supply.
- Connect the Raspberry Pi's **Ground** pin (e.g., pin 6) to the same negative (-) terminal of the external power supply. This creates a common ground, which is essential for the signal to be interpreted correctly.<sup>37</sup>
- Connect the servo's **Orange/Yellow** signal wire to a GPIO pin on the Raspberry Pi (e.g., GPIO17, which is pin 11).

### 5.2 Teaching the Pi to Move: Python for GPIO Control

Before integrating the AI agent, it is important to verify that the hardware is working correctly. This can be done with a simple Python script on the Raspberry Pi that uses the `gpiozero` library, which provides a very beginner-friendly interface for controlling GPIO devices.<sup>37</sup>

1.  **Install `gpiozero`:** On the Raspberry Pi (via SSH), install the library:
        ```bash
        sudo apt-get update
        sudo apt-get install python3-gpiozero
        ```
2.  **Create a Test Script:** Create a file named `servo_test.py` on the Pi and add the following code:
        ```python
        # servo_test.py
        from gpiozero import Servo
        from time import sleep

        # The value in Servo() must match the GPIO pin number used for the signal wire.
        servo = Servo(17) 

        try:
                print("Moving servo to minimum position (-90 degrees)")
                servo.min()
                sleep(2)

                print("Moving servo to middle position (0 degrees)")
                servo.mid()
                sleep(2)

                print("Moving servo to maximum position (+90 degrees)")
                servo.max()
                sleep(2)

                print("Test complete. Returning to middle.")
                servo.mid()

        except KeyboardInterrupt:
                print("Program stopped by user")
        ```
3.  **Run the Script:** Execute the script from the Pi's terminal: `python3 servo_test.py`. The servo motor should move to its minimum, middle, and maximum positions, confirming that the wiring and hardware are correct.

### 5.3 Creating the Robot's Senses: ADK Tools for Physical Actions

The core of this project is bridging the digital ADK agent running on a development computer with the physical Raspberry Pi. This is achieved by creating custom ADK tools that, when called, execute commands remotely on the Pi. The entire chain of events—from a natural language command to a physical movement—demonstrates the power of agentic systems to interact with the real world.<sup>40</sup>

The signal flow works as follows:

1.  A user types a command like "wave hello" into the ADK Web UI on their computer.
2.  The request is sent to the `robot_controller_agent` running locally.
3.  The agent's LLM reasons about the request and determines that the `wave_hand` tool is the appropriate action.
4.  ADK executes the `wave_hand` Python function on the computer.
5.  This function uses SSH to send a command to the Raspberry Pi, instructing it to run a specific Python script.
6.  The script on the Pi receives the command and executes the `gpiozero` code to move the servo motor accordingly.

First, create two simple scripts on the Raspberry Pi to handle the specific movements.

**`move_script.py` (on the Raspberry Pi):**

```python
# move_script.py
import sys
from gpiozero import Servo

# Get the angle from the command-line argument
angle = int(sys.argv[1])
# Convert angle (-90 to 90) to servo value (-1 to 1)
value = angle / 90.0

servo = Servo(17)
servo.value = value
```

**`wave_script.py` (on the Raspberry Pi):**

```python
# wave_script.py
from gpiozero import Servo
from time import sleep

servo = Servo(17)
for _ in range(3):
        servo.min()
        sleep(0.3)
        servo.max()
        sleep(0.3)
servo.mid()
```

Next, on the development computer, define the ADK tools in the `agent.py` file. These tools will use `os.system` to make the remote SSH calls.

**`agent.py` (on the development computer):**

```python
import os

# IMPORTANT: Replace with the actual username and IP address of the Raspberry Pi
PI_ADDRESS = "pi@192.168.1.101" 

def move_servo(angle: int) -> str:
        """
        Moves the servo motor to a specific angle between -90 and 90 degrees.

        Args:
                angle (int): The target angle for the servo. Must be between -90 and 90.
        
        Returns:
                str: A confirmation message indicating the action was performed.
        """
        # This command remotely executes the move_script.py on the Pi
        command = f"ssh {PI_ADDRESS} 'python3 /home/pi/move_script.py {angle}'"
        os.system(command)
        return f"Command sent to move servo to {angle} degrees."

def wave_hand() -> str:
        """
        Makes the robot arm perform a waving motion.
        Use this tool when the user asks the robot to wave or say hello.

        Returns:
                str: A confirmation message.
        """
        # This command remotely executes the wave_script.py on the Pi
        command = f"ssh {PI_ADDRESS} 'python3 /home/pi/wave_script.py'"
        os.system(command)
        return "Command sent to wave hand."
```

### 5.4 The Final Assembly: The Robot Control Agent

The final step is to create the agent that will use these new hardware-controlling tools. The agent's instructions are crucial for correctly mapping natural language commands from the user to the appropriate tool calls.

Add the following agent definition to the end of the `agent.py` file on the development computer:

```python
# agent.py

#... (move_servo and wave_hand functions from the previous section)...

from google.adk.agents import Agent

root_agent = Agent(
        name="robot_controller_agent",
        model="gemini-2.0-pro",
        description="An agent that controls a simple Raspberry Pi robot arm via natural language.",
        instruction="""
        You are the controller for a physical robot arm.
        - Your goal is to translate user commands into specific tool calls.
        - If the user asks to wave, say hello, or a similar greeting, you must use the wave_hand tool.
        - If the user asks to move the arm to a specific position or angle, you must use the move_servo tool.
            Extract the numerical angle from the user's request and pass it to the tool.
            The valid angle range is -90 to 90.
        - Respond to the user by confirming the action you have taken.
        """,
        tools=[move_servo, wave_hand]
)
```

### 5.5 Bringing It to Life

With the agent fully defined, the system is ready for its final test.

1.  **Prepare the Hardware:** Ensure the Raspberry Pi is powered on, connected to the network, and the servo is correctly wired to its external power supply.
2.  **Start the Agent Server:** On the development computer, open a terminal, navigate to the project's `parent_folder`, and activate the virtual environment. To make the agent's web interface accessible to other devices on your local network (like your phone or another computer), run the ADK web server with an additional `--host` flag. This tells the server to listen for connections from any device on the network, not just the local machine.<sup>42</sup>
        ```bash
        adk web --host 0.0.0.0
        ```
3.  **Find Your Computer's Local IP Address:** To connect from another device, you need the local IP address of the computer running the agent. Open a new terminal window on the development computer and use the appropriate command for your operating system:
        - **Windows:** Type `ipconfig` and look for the "IPv4 Address" under your active Wi-Fi or Ethernet adapter.<sup>43</sup>
        - **macOS:** Type `ipconfig getifaddr en0` (for Wi-Fi) or `ipconfig getifaddr en1` (for Ethernet).<sup>45</sup>
        - **Linux:** Type `hostname -I` to see a list of IP addresses; use the one associated with your local network.<sup>47</sup>
4.  **Connect and Control:** On your external device (phone or another PC), open a web browser and navigate to `http://<YOUR_COMPUTER_IP_ADDRESS>:8000`, replacing `<YOUR_COMPUTER_IP_ADDRESS>` with the IP address you found in the previous step.
5.  **Interact with the Robot:** In the web UI, select the `robot_controller_agent`. Type commands into the chat interface and observe the physical Raspberry Pi robot. Example commands to try:
        - "Wave to me!"
        - "Move the arm to 45 degrees."
        - "Point the arm all the way to the left." (The LLM should infer this means -90 degrees).
        - "Reset the arm to the center position."

The successful execution of these commands, translating a simple typed sentence into a physical robotic action from any device on your network, provides a powerful and rewarding demonstration of what is possible when AI agents are empowered to interact with the world around them. This project serves as a foundational stepping stone for more complex robotics and automation tasks.

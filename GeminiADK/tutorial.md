# Gemini on Raspberry Pi: Installation & Quickstart

This tutorial is divided into three sessions. The first session covers the one-time installation of all necessary tools for both C++ and Python. The following sessions guide you through creating a weather chatbot agent in each language.

**Table of Contents**
1. [Session 1: Install Gemini ADK & SDKs](#session-1-install-gemini-adk--sdks-)
    * [C++ Environment Setup](#c-environment-setup)
    * [Python Environment Setup](#python-environment-setup)
2. [Session 2: C++ Weather Agent Quick Start](#session-2-c-weather-agent-quick-start-)
    * [Step 2.1: Create the C++ Source Code](#step-21-create-the-c-source-code)
    * [Step 2.2: Update the Build System](#step-22-update-the-build-system)
    * [Step 2.3: Compile and Run the C++ Agent](#step-23-compile-and-run-the-c-agent)
3. [Session 3: Python Weather Agent Quick Start](#session-3-python-weather-agent-quick-start-)
    * [Step 3.1: Create the Python Script](#step-31-create-the-python-script)
    * [Step 3.2: Set API Key and Run the Python Agent](#step-32-set-api-key-and-run-the-python-agent)

---

## Session 1: Install Gemini ADK & SDKs ⚙️

This session covers the one-time setup required for both C++ and Python development on your Raspberry Pi.

### C++ Environment Setup

1.  **Install Build Tools:** Install the C++ compiler (`g++`), the CMake build system, and Git.
    ```bash
    sudo apt update
    sudo apt install build-essential cmake git
    ```

2.  **Clone and Build the ADK:** Download the Gemini C++ ADK source code and compile the core library. The `--recurse-submodules` flag is essential.
    ```bash
    git clone --recurse-submodules [https://github.com/google/gemini-adk.git](https://github.com/google/gemini-adk.git)
    cd gemini-adk
    mkdir build && cd build
    cmake ..
    cmake --build . -j $(nproc)
    ```
    This completes the C++ setup. The `~/gemini-adk/` directory is now ready for your C++ projects.

### Python Environment Setup

Install the official Google Gemini SDK for Python using `pip`.
```bash
pip install -q -U google-generativeai
````

This completes the Python setup.

-----

## Session 2: C++ Weather Agent Quick Start 🚀

This session assumes you have completed Session 1. You'll now build a C++ application using the ADK you compiled.

### Step 2.1: Create the C++ Source Code

1.  Navigate to the `examples` directory:

    ```bash
    cd ~/gemini-adk/examples
    ```

2.  Create a new directory and C++ file for your agent:

    ```bash
    mkdir weather_agent
    nano weather_agent/weather_agent.cc
    ```

3.  Paste the following code into the editor. This code defines a "tool" that the Gemini model can call.

    ```cpp
    #include <iostream>
    #include <memory>
    #include <string>
    #include "adk/adk.h"
    #include "absl/flags/flag.h"
    #include "absl/flags/parse.h"

    // Our C++ function that returns a fake weather report.
    std::string GetCurrentWeather(const std::string& location) {
      std::cout << "[ C++ Tool Called for location: " << location << " ]" << std::endl;
      return R"({"location":")" + location + R"(", "temperature":"15 C", "forecast":"sunny"})";
    }

    int main(int argc, char* argv[]) {
      absl::ParseCommandLine(argc, argv);
      adk::ChatSession session(adk::ModelId("gemini-1.5-flash-latest"));
      adk::Tool weather_tool("get_current_weather", "Get the current weather in a given location.", {{"location", "The city name"}});

      std::cout << "C++ Agent Connected! Ask about the weather. Type 'exit' to quit." << std::endl;

      while (true) {
        std::cout << "\n> ";
        std::string user_input;
        std::getline(std::cin, user_input);
        if (user_input == "exit") break;

        adk::Response response = session.SendMessage(user_input, {weather_tool});

        if (response.HasFunctionCall()) {
          adk::FunctionCall function_call = response.GetFunctionCall();
          if (function_call.name == "get_current_weather") {
            std::string weather_data = GetCurrentWeather(function_call.args.at("location"));
            adk::Response final_response = session.SendMessage(adk::FunctionResponse(function_call.name, weather_data));
            std::cout << final_response.GetText() << std::endl;
          }
        } else {
          std::cout << response.GetText() << std::endl;
        }
      }
      return 0;
    }
    ```

    Save and exit (`Ctrl+X`, `Y`, `Enter`).

### Step 2.2: Update the Build System

Tell CMake how to build your new agent.

1.  Open `CMakeLists.txt` for editing:

    ```bash
    nano ~/gemini-adk/examples/CMakeLists.txt
    ```

2.  Scroll to the bottom and **add these two lines**:

    ```cmake
    add_executable(weather_agent weather_agent/weather_agent.cc)
    target_link_libraries(weather_agent PRIVATE adk)
    ```

    Save and exit.

### Step 2.3: Compile and Run the C++ Agent

Compile your specific program and run it.

1.  Navigate to the `build` directory and run the build commands:

    ```bash
    cd ~/gemini-adk/build
    cmake ..
    cmake --build . --target weather_agent -j $(nproc)
    ```

2.  Run the agent, providing your API key from [Google AI Studio](https://aistudio.google.com/app/apikey) as an argument:

    ```bash
    ./examples/weather_agent/weather_agent --api_key <YOUR_API_KEY>
    ```

    Ask it, "What is the weather in Tokyo?" to test.

-----

## Session 3: Python Weather Agent Quick Start 🐍

This session assumes you have completed Session 1. You'll now create a Python script that uses the Gemini SDK.

### Step 3.1: Create the Python Script

Create a single Python file for the chatbot. You can place this file in your home directory or anywhere you like.

1.  Create the Python file:

    ```bash
    nano ~/weather_agent.py
    ```

2.  Paste the following code into the editor:

    ```python
    import os
    import google.generativeai as genai

    def get_current_weather(location: str):
        """Get the current weather; returns a fake forecast for this demo."""
        print(f"[ Python Tool Called for location: {location} ]")
        return f"The weather in {location} is 22°C and clear."

    def main():
        """Main function to run the chatbot."""
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                print("Error: GEMINI_API_KEY not set. Run: export GEMINI_API_KEY='YOUR_KEY'")
                return
            genai.configure(api_key=api_key)

            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                tools=[get_current_weather]
            )
            chat = model.start_chat(enable_automatic_function_calling=True)

            print("Python Agent Connected! Ask about the weather. Type 'exit' to quit.")

            while True:
                print("\n> ", end="")
                user_input = input()
                if user_input.lower() == 'exit':
                    break
                
                response = chat.send_message(user_input)
                print(response.text)

        except Exception as e:
            print(f"An error occurred: {e}")

    if __name__ == "__main__":
        main()
    ```

    Save and exit (`Ctrl+X`, `Y`, `Enter`).

### Step 3.2: Set API Key and Run the Python Agent

The script requires an API key set as an environment variable.

1.  Set the environment variable in your terminal. Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey).

    ```bash
    export GEMINI_API_KEY='<YOUR_API_KEY>'
    ```

2.  Run the Python script from your home directory:

    ```bash
    python ~/weather_agent.py
    ```

    Ask it, "What is the weather like in London?" to test.

<!-- end list -->

```
```

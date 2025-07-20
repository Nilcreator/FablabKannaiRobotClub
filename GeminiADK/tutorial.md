# Quickstart: Gemini ADK & Weather Bot on Raspberry Pi

This guide provides a complete tutorial for installing the necessary tools and building your first weather chatbot agent on a Raspberry Pi. It covers both the C++ Gemini ADK for compiled applications and the Python SDK for scripting.

**Table of Contents**
1. [Part 1: The C++ Weather Agent](#part-1-the-c-weather-agent-)
    * [Step 1.1: Install C++ Dependencies](#step-11-install-c-dependencies-)
    * [Step 1.2: Clone and Build the Gemini ADK](#step-12-clone-and-build-the-gemini-adk-)
    * [Step 1.3: Create the C++ Weather Agent Code](#step-13-create-the-c-weather-agent-code-)
    * [Step 1.4: Compile and Run the C++ Agent](#step-14-compile-and-run-the-c-agent-)
2. [Part 2: The Python Weather Agent](#part-2-the-python-weather-agent-)
    * [Step 2.1: Install the Python SDK](#step-21-install-the-python-sdk-)
    * [Step 2.2: Create the Python Weather Agent Script](#step-22-create-the-python-weather-agent-script-)
    * [Step 2.3: Run the Python Agent](#step-23-run-the-python-agent-)

---

## Part 1: The C++ Weather Agent ⚙️

This section covers building the C++ library from source and creating a compiled chatbot application.

### Step 1.1: Install C++ Dependencies

First, install the tools required to build C++ projects on your Raspberry Pi.

```bash
sudo apt update
sudo apt install build-essential cmake git
````

  * `build-essential`: Includes the C++ compiler (`g++`).
  * `cmake`: The build system used by the ADK.
  * `git`: For downloading the source code.

-----

### Step 1.2: Clone and Build the Gemini ADK

Download the ADK source code and compile it.

1.  **Clone the repository:** The `--recurse-submodules` flag is critical as it downloads necessary third-party libraries.

    ```bash
    git clone --recurse-submodules [https://github.com/google/gemini-adk.git](https://github.com/google/gemini-adk.git)
    cd gemini-adk
    ```

2.  **Create a build directory:** This is standard practice to keep the source code clean.

    ```bash
    mkdir build && cd build
    ```

3.  **Compile the ADK:** This command prepares and builds the entire library. It may take several minutes.

    ```bash
    cmake ..
    cmake --build . -j $(nproc)
    ```

-----

### Step 1.3: Create the C++ Weather Agent Code

Now, you'll create a new C++ file for the chatbot and tell the build system about it.

1.  **Create the C++ file:**

    ```bash
    cd ~/gemini-adk/examples
    mkdir weather_agent
    nano weather_agent/weather_agent.cc
    ```

2.  **Paste the following code** into the `nano` editor. It defines a hardcoded weather function and tells the Gemini model how to call it.

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

3.  **Update the build system:** Open the build script to add your new program.

    ```bash
    nano ~/gemini-adk/examples/CMakeLists.txt
    ```

    Scroll to the bottom and **add these two lines**:

    ```cmake
    add_executable(weather_agent weather_agent/weather_agent.cc)
    target_link_libraries(weather_agent PRIVATE adk)
    ```

    Save and exit.

-----

### Step 1.4: Compile and Run the C++ Agent

Finally, compile your new agent and run it.

1.  **Compile the agent:** Navigate back to the `build` directory and run the build command, specifying your new target.

    ```bash
    cd ~/gemini-adk/build
    cmake ..
    cmake --build . --target weather_agent -j $(nproc)
    ```

2.  **Run the chatbot:** You must provide your API key as an argument. Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey).

    ```bash
    ./examples/weather_agent/weather_agent --api_key <YOUR_API_KEY>
    ```

    Ask it, "What's the weather in Tokyo?" to see it work.

-----

## Part 2: The Python Weather Agent 🐍

This section covers creating the same chatbot using the much simpler Python SDK.

### Step 2.1: Install the Python SDK

Install the official Google Gemini library for Python using `pip`.

```bash
pip install -q -U google-generativeai
```

-----

### Step 2.2: Create the Python Weather Agent Script

Create a single Python file containing all the logic.

1.  **Create the Python file:**

    ```bash
    nano weather_agent.py
    ```

2.  **Paste the following code** into the editor. It defines a weather function and uses the SDK's automatic function calling feature.

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

            # Define the model and automatically create a tool from our Python function
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

-----

### Step 2.3: Run the Python Agent

The Python script requires the API key to be set as an environment variable.

1.  **Set your API key:** In your terminal, run this command, pasting your key in place of `<YOUR_API_KEY>`.

    ```bash
    export GEMINI_API_KEY='<YOUR_API_KEY>'
    ```

2.  **Run the script:**

    ```bash
    python weather_agent.py
    ```

    Ask it, "What is the weather like in London?" to test it.

<!-- end list -->

```
```

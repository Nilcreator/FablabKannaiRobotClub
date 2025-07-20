# Installing the Google Gemini CLI on Raspberry Pi

This guide provides a complete tutorial for installing the Google Gemini CLI on any Raspberry Pi model. It covers the critical step of installing the correct version of Node.js for your Pi's specific CPU architecture (32-bit or 64-bit) to avoid common errors.

**Table of Contents**
1. [Step 1: Identify Your Pi's CPU Architecture](#step-1-identify-your-pis-cpu-architecture-)
2. [Step 2: Install Node.js for Your CPU](#step-2-install-nodejs-for-your-cpu-)
    * [For 64-bit Systems (`aarch64`)](#for-64-bit-systems-aarch64)
    * [For 32-bit Systems (`armv7l` / `armv6l`)](#for-32-bit-systems-armv7l--armv6l)
3. [Step 3: Install the Gemini CLI](#step-3-install-the-gemini-cli-)
4. [Step 4: Authenticate the CLI](#step-4-authenticate-the-cli-)
5. [Step 5: Test the CLI](#step-5-test-the-cli-)

---

## Step 1: Identify Your Pi's CPU Architecture 🕵️

First, you must determine if your Raspberry Pi is running a 32-bit or 64-bit operating system. This single command will tell you what you need to know for the next steps.

Run this command in your terminal:
```bash
uname -m
````

Note the output. It will be one of the following:

  * `aarch64` or `arm64`: **You have a 64-bit system.**
  * `armv7l` or `armv6l`: **You have a 32-bit system.**

-----

## Step 2: Install Node.js for Your CPU ⚙️

You must follow the instructions that match your system's architecture from Step 1.

### For 64-bit Systems (`aarch64`)

This method uses the NodeSource repository, which is straightforward for modern 64-bit systems.

1.  **Run the NodeSource setup script for Node.js v20:**

    ```bash
    curl -fsSL [https://deb.nodesource.com/setup_20.x](https://deb.nodesource.com/setup_20.x) | sudo -E bash -
    ```

2.  **Install Node.js:**

    ```bash
    sudo apt-get install -y nodejs
    ```

### For 32-bit Systems (`armv7l` / `armv6l`)

For 32-bit systems, the best method is to use **Node Version Manager (`nvm`)**, as it automatically fetches a compatible version.

1.  **Install `nvm`:**

    ```bash
    curl -o- [https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh](https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh) | bash
    ```

2.  **Activate `nvm`:** Close and reopen your terminal, or run the following command to activate it for your current session:

    ```bash
    source ~/.bashrc
    ```

3.  **Install a compatible version of Node.js v20:**

    ```bash
    nvm install 20
    ```

    `nvm` will find and install the correct binary for your CPU.

**After completing either method, verify the installation:**

```bash
node -v
npm -v
```

You should see version numbers (e.g., `v20.x.x`) without any "Illegal instruction" errors.

-----

## Step 3: Install the Gemini CLI 🚀

Now that Node.js is correctly installed, you can install the Gemini CLI globally. Use `sudo` to grant the necessary permissions to install it in a system directory.

```bash
sudo npm install -g @google/gemini-cli
```

This makes the `gemini` command available everywhere on your system.

-----

## Step 4: Authenticate the CLI 🔑

The recommended way to authenticate is with an API key, which you can manage in a `.env` file.

1.  **Get an API Key:** Create and copy a free API key from Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

2.  **Create a `.env` file:**

    ```bash
    nano ~/.env
    ```

3.  **Add your key to the file.** Replace `YOUR_API_KEY_HERE` with your actual key.

    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```

    Save and exit by pressing `Ctrl+X`, then `Y`, then `Enter`.

4.  **Install `dotenv-cli`:** This tool loads your API key from the `.env` file.

    ```bash
    sudo npm install -g dotenv-cli
    ```

-----

## Step 5: Test the CLI ✨

To run a prompt, you must now prefix your command with `dotenv` to load your API key. `dotenv` will automatically find the `.env` file in your home directory.

```bash
dotenv gemini "What is the distance between Earth and the Moon?"
```

If you see a response from Gemini, your installation is complete and successful\!

```
```

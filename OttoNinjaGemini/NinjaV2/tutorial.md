# Build Your Own Voice-Controlled Ninja Robot (Raspberry Pi & Gemini)

![Robot Concept](placeholder_image.png)  <!-- Optional: Replace with an image of your robot if you have one -->

This tutorial guides you through building and programming a voice-controlled robot based on a Raspberry Pi Zero. It utilizes the DFRobot IO Expansion HAT, various sensors and actuators (servos, I2S microphone, ultrasonic sensor, buzzer), and Google's Gemini AI for natural language processing. The robot can be controlled via a web interface (controller buttons or browser microphone) or by speaking directly to its onboard microphone.

---

## Table of Contents

*   [Part 1: English Tutorial](#part-1-english-tutorial)
    *   [1. Introduction](#1-introduction)
    *   [2. Hardware Requirements](#2-hardware-requirements)
    *   [3. Hardware Assembly](#3-hardware-assembly)
    *   [4. Software Setup](#4-software-setup)
    *   [5. Code Setup](#5-code-setup)
    *   [6. Configuration](#6-configuration)
    *   [7. Running the Application](#7-running-the-application)
    *   [8. Using the Interface](#8-using-the-interface)
    *   [9. Troubleshooting](#9-troubleshooting)
    *   [10. Stopping the Application](#10-stopping-the-application)
*   [Part 2: Japanese Tutorial (日本語チュートリアル)](#part-2-japanese-tutorial-日本語チュートリアル)
    *   [1. はじめに (Introduction)](#1-はじめに-introduction)
    *   [2. 必要なハードウェア (Hardware Requirements)](#2-必要なハードウェア-hardware-requirements)
    *   [3. ハードウェアの組み立て (Hardware Assembly)](#3-ハードウェアの組み立て-hardware-assembly)
    *   [4. ソフトウェアのセットアップ (Software Setup)](#4-ソフトウェアのセットアップ-software-setup)
    *   [5. コードのセットアップ (Code Setup)](#5-コードのセットアップ-code-setup)
    *   [6. 設定 (Configuration)](#6-設定-configuration)
    *   [7. アプリケーションの実行 (Running the Application)](#7-アプリケーションの実行-running-the-application)
    *   [8. インターフェースの使用方法 (Using the Interface)](#8-インターフェースの使用方法-using-the-interface)
    *   [9. トラブルシューティング (Troubleshooting)](#9-トラブルシューティング-troubleshooting)
    *   [10. アプリケーションの停止 (Stopping the Application)](#10-アプリケーションの停止-stopping-the-application)

---

## Part 1: English Tutorial

### 1. Introduction

This project creates an interactive robot controllable via natural language commands. It integrates movement, sound feedback, basic obstacle detection, and AI-powered command interpretation using Google Gemini. You'll assemble the hardware, set up the Raspberry Pi environment, configure the code, and run a web server to interact with the robot.

### 2. Hardware Requirements

*   **Raspberry Pi Zero:** W or WH model recommended for built-in WiFi/Bluetooth.
*   **Micro SD Card:** 8GB+, Class 10 recommended, flashed with Raspberry Pi OS.
*   **Power Supply:** Stable 5V, >= 2.5A micro USB power supply.
*   **DFRobot IO Expansion HAT:** Compatible with Raspberry Pi Zero GPIO layout.
*   **INMP441 I2S Microphone Module:** For onboard voice input.
*   **HC-SR04 Ultrasonic Distance Sensor:** For obstacle detection.
*   **Active Buzzer Module:** For audio feedback sounds.
*   **SG90 Servos (x4):** Standard hobby servos (or adjust code for different servos).
*   **Robot Chassis/Frame:** Suitable for mounting the components and allowing servo movement.
*   **Jumper Wires:** Assorted Female-to-Female (F/F) and Male-to-Female (M/F).
*   **Computer:** For initial setup and accessing the web UI.
*   **(Optional):** USB Keyboard, Mouse, HDMI Monitor/Adapter for non-headless setup.

### 3. Hardware Assembly

**⚠️ IMPORTANT: Always disconnect the power supply from the Raspberry Pi before connecting or disconnecting any components!**

1.  **Mount HAT:** Carefully align the DFRobot IO Expansion HAT onto the Raspberry Pi Zero's 40-pin GPIO header and press down firmly and evenly.
2.  **Connect Servos:**
    *   Connect the 4 servos to the dedicated servo ports on the Expansion HAT (usually marked S0-S3 or similar).
    *   Ensure correct polarity: Signal (usually Yellow/Orange), VCC/+ (Red), GND/- (Brown/Black).
    *   Note which physical servo corresponds to which port number (0-3). The default code assumes:
        *   Servo 0: Right Leg/Hip
        *   Servo 1: Left Leg/Hip
        *   Servo 2: Right Foot/Ankle
        *   Servo 3: Left Foot/Ankle
3.  **Connect I2S Microphone (INMP441):**
    *   Use jumper wires to connect the module to the HAT's GPIO breakout pins (refer to HAT documentation for pin mapping).
    *   `VDD` -> HAT `3.3V`
    *   `GND` -> HAT `GND`
    *   `SCK` -> HAT `GPIO 18` (I2S BCLK)
    *   `WS` -> HAT `GPIO 19` (I2S LRCLK/FS)
    *   `SD` -> HAT `GPIO 20` (I2S DIN / Data Out from Mic)
    *   `L/R` -> HAT `GND` (Selects Left channel for mono processing)
4.  **Connect Ultrasonic Sensor (HC-SR04):**
    *   Connect to the HAT's GPIO breakout pins.
    *   `VCC` -> HAT `5V` (Check sensor datasheet; some may work on 3.3V)
    *   `Trig` -> HAT `GPIO 21`
    *   `Echo` -> HAT `GPIO 22`
    *   `GND` -> HAT `GND`
5.  **Connect Buzzer:**
    *   Connect to the HAT's GPIO breakout pins.
    *   `Signal/IO` -> HAT `GPIO 23`
    *   `VCC/+` -> HAT `3.3V` (or `5V` depending on module)
    *   `GND/-` -> HAT `GND`
6.  **Assemble Robot:** Mount the Pi/HAT assembly, servos, sensor, and buzzer onto your robot chassis. Organize wiring to prevent snags during movement.

### 4. Software Setup

1.  **Install OS:** Use Raspberry Pi Imager to flash Raspberry Pi OS (Lite or Desktop, 32-bit recommended for Pi Zero) onto the SD card. Use the advanced options (⚙️ icon) to pre-configure hostname, enable SSH, set user/password, and configure WiFi.
2.  **First Boot & Connect:** Insert SD card, connect power. Wait a few minutes for the first boot. Connect via SSH from your computer (`ssh your_username@your_pi_hostname.local` or `ssh your_username@<PI_IP_ADDRESS>`).
3.  **System Update:** Bring the OS and packages up to date:
    ```bash
    sudo apt update
    sudo apt full-upgrade -y
    sudo reboot
    ```
    *(Reconnect via SSH after reboot)*
4.  **Enable I2S Interface:**
    *   Edit the boot configuration file:
        ```bash
        sudo nano /boot/firmware/config.txt
        # Or potentially: sudo nano /boot/config.txt
        ```
    *   Add these lines at the very end:
        ```text
        # Enable I2S audio interface for Microphone
        dtparam=i2s=on
        dtoverlay=googlevoicehat-soundcard
        ```
    *   Save (`Ctrl+X`, `Y`, `Enter`) and reboot: `sudo reboot`
5.  **Install System Dependencies:** Install libraries needed by the Python packages:
    ```bash
    sudo apt install -y python3-dev python3-pip python3-venv build-essential libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg flac libatlas-base-dev
    ```
6.  **Create Project Directory & Virtual Environment (Recommended):**
    ```bash
    mkdir ~/ninja_robot_v2 # Or your preferred project name
    cd ~/ninja_robot_v2
    python3 -m venv .venv # Create virtual environment named NinjaRobot
    source NinjaRobot/bin/activate # Activate the environment
    ```
    *(Your terminal prompt should now start with `(.venv)`)*
7.  **Install Python Libraries:** (Make sure the virtual environment is active)
    ```bash
    pip install --upgrade pip
    pip install RPi.GPIO google-generativeai SpeechRecognition gTTS pygame Flask google-cloud-speech
    ```
    *(This step can take significant time on a Pi Zero)*
    *Once encountering error can try the following steps*
    1. deactivate virtual enviroment
    2. Update Package Lists: Make sure your package list is up-to-date:
       ```bash
       sudo apt update
       ```
    3. install Cargo:
       ```bash
       sudo apt install cargo -y
       ```
    4. Verify Installation (Optional): After it finishes, you can check the versions:
       ```bash
       cargo --version
       rustc --version
       ```
    5. activate virtual enviroment and install library again

### 5. Code Setup

1.  **Download/Copy Code Files:** Place the following Python files into your project directory (`~/ninja_robot_v4`):
    *   `Ninja_Movements_v1.py`
    *   `Ninja_Buzzer.py`
    *   `Ninja_Distance.py`
    *   `ninja_core.py` (The final version incorporating V1.4 features)
    *   `Ninja_Voice_Control.py` (Script for "Robot Mic" mode)
    *   `web_interface.py` (The final Flask server combining features)
2.  **Create `templates` Directory:** Inside the project directory:
    ```bash
    mkdir templates
    ```
3.  **Create `index.html`:** Create the file `index.html` inside the `templates` directory. Paste the final HTML/CSS/JavaScript code for the web interface into this file.

### 6. Configuration

1.  **Google Gemini API Key:**
    *   Edit the core logic file: `nano ninja_core.py`
    *   Locate the line: `GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"`
    *   Replace `"YOUR_GOOGLE_API_KEY"` with your actual key from Google AI Studio or Google Cloud.
    *   **IMPORTANT:** Keep your API key secure. Do not share it publicly. For production, consider environment variables.
    *   Save the file (`Ctrl+X`, `Y`, `Enter`).
2.  **(Optional) Robot Mic Sensitivity Tuning:**
    *   If the "Robot Mic" mode has trouble hearing you or triggers on noise, edit `Ninja_Voice_Control.py`.
    *   Find `recognizer.energy_threshold = 500`.
    *   Run the script once via the web UI ("Speak to Robot" button) and check the console output for the value printed after "Ambient noise adjustment complete".
    *   Stop the script (`Ctrl+C` in the *Flask server* terminal, then click Stop/Controller/Browser Mic button).
    *   Adjust the `500` value (higher if missing speech, lower if triggering on noise). You might also comment out the `recognizer.adjust_for_ambient_noise(...)` line if manual tuning works better. Save the file.

### 7. Running the Application

1.  **Activate Environment:** Navigate to your project directory and activate the virtual environment (if using):
    ```bash
    cd ~/ninja_robot_v4
    source .venv/bin/activate
    ```
2.  **Find Pi's IP Address:**
    ```bash
    hostname -I | awk '{print $1}'
    ```
    *(Note the IP address shown, e.g., 192.168.1.XX)*
3.  **Start the Web Server:**
    ```bash
    python3 web_interface.py
    ```
    *(Look for lines indicating it's running on `http://0.0.0.0:5000`)*
4.  **Access Web Interface:** On another device (phone, computer) on the **same WiFi network**, open a web browser and go to:
    `http://<YOUR_PI_IP_ADDRESS>:5000`
    *(Replace `<YOUR_PI_IP_ADDRESS>` with the actual IP)*

### 8. Using the Interface

*   **Initial State:** The interface loads in "Controller" mode.
*   **Controller Mode:** Use the on-screen buttons (D-Pad, Actions △/□/○/×, Speed, Rest) to directly command the robot. This mode stops the "Robot Mic" background script if it was running.
*   **Browser Mic Mode:**
    1.  Click "Browser Mic" button to activate the mode.
    2.  Click "Browser Mic" again (now says "Listening...") to start recognition via your browser. Grant mic permission if needed.
    3.  Speak clearly.
    4.  The recognized text and robot response/action appear in the status area.
    5.  Clicking "Listening..." stops the current recognition.
*   **Robot Mic Mode:**
    1.  Click "Speak to Robot". The button should change to "Robot Mic (ON)". This starts the dedicated voice control script on the Pi.
    2.  The "Robot Mic Dialog" box will display the ongoing conversation log from the script.
    3.  Speak to the robot's physical INMP441 microphone. Use "ninja" as the wake word for commands (e.g., "ninja walk", "ninja tell me a joke"). Ask general questions without the wake word.
    4.  To stop this mode, click "Controller" or "Browser Mic".

### 9. Troubleshooting

*   **Python Errors (`NameError`, `ImportError`):** Ensure all libraries from step 4.7 are installed in the active environment. Check file locations.
*   **Hardware/Core Init Failures:** Review hardware connections (Step 3). Check `web_interface.py` console output for errors during startup.
*   **"Robot Mic" Fails to Start:** Examine `web_interface.py` console output when clicking the button. Look for errors from `subprocess.Popen` or stderr output from `Ninja_Voice_Control.py` (often audio device issues). Verify I2S setup (Step 4.4).
*   **Voice Recognition Issues:** Check mic connections. Tune sensitivity (Step 6.2 for Robot Mic). Ensure browser mic permission (Browser Mic). Check internet connection (both).
*   **Gemini Errors:** Verify API Key (Step 6.1). Check Google Cloud project status (API enabled?).
*   **Robot Movement Issues:** Verify servo connections (Step 3.2). Check angles in `Ninja_Movements_v1.py`. Ensure adequate power supply.
*   **Web Interface Unresponsive:** Ensure Flask server (`web_interface.py`) is running on the Pi. Check Pi's IP address and network connection. Check browser console for JavaScript errors.

### 10. Stopping the Application

*   Go to the terminal running `web_interface.py`.
*   Press `Ctrl+C`.
*   The `atexit` cleanup function should automatically:
    *   Signal the background voice script (if running) to stop.
    *   Call `ninja_core.cleanup_all()` which plays the "thanks" sound, moves to rest, and releases GPIO resources.

---
---

## Part 2: Japanese Tutorial (日本語チュートリアル)

### 1. はじめに (Introduction)

このプロジェクトでは、自然言語コマンドで制御可能なインタラクティブ・ロボットを作成します。移動、サウンドフィードバック、基本的な障害物検出、そしてGoogle Geminiを使用したAIによるコマンド解釈を統合します。ハードウェアの組み立て、Raspberry Pi環境のセットアップ、コードの設定、そしてロボットと対話するためのウェブサーバーの実行を行います。

### 2. 必要なハードウェア (Hardware Requirements)

*   **Raspberry Pi Zero:** WiFi/Bluetooth内蔵のWまたはWHモデル推奨。
*   **Micro SDカード:** 8GB以上、Class 10推奨、Raspberry Pi OS書き込み済み。
*   **電源:** 安定した5V、2.5A以上のmicro USB電源。
*   **DFRobot IO Expansion HAT:** Raspberry Pi Zero GPIOレイアウト互換のもの。
*   **INMP441 I2S マイクモジュール:** オンボード音声入力用。
*   **HC-SR04 超音波距離センサー:** 障害物検出用。
*   **アクティブブザーモジュール:** 音声フィードバック用。
*   **SG90 サーボ (x4):** 標準的なホビーサーボ（異なる場合はコード調整）。
*   **ロボットシャーシ/フレーム:** コンポーネント搭載とサーボ動作に適したもの。
*   **ジャンパーワイヤー:** メス-メス(F/F)およびオス-メス(M/F)各種。
*   **コンピュータ:** 初期設定およびWeb UIアクセス用。
*   **(オプション):** USBキーボード、マウス、HDMIモニター/アダプター（ヘッドレスでない場合）。

### 3. ハードウェアの組み立て (Hardware Assembly)

**⚠️ 重要: 部品の接続・切断前には、必ずRaspberry Piの電源を切断してください！**

1.  **HATの取り付け:** DFRobot IO Expansion HATをPi Zeroの40ピンGPIOヘッダーに慎重に合わせ、均等にしっかりと押し込みます。
2.  **サーボの接続:**
    *   4つのサーボをHATのサーボポート（S0-S3等）に接続します。
    *   極性（信号：黄/橙、VCC/+：赤、GND/-：茶/黒）に注意。
    *   どの物理サーボがどのポート番号（0-3）に対応するかメモします。デフォルトコードの想定：
        *   Servo 0: 右脚/股関節
        *   Servo 1: 左脚/股関節
        *   Servo 2: 右足/足首
        *   Servo 3: 左足/足首
3.  **I2Sマイク(INMP441)の接続:**
    *   ジャンパー線でモジュールをHATのGPIOブレイクアウトピンに接続（HAT資料参照）。
    *   `VDD` -> HAT `3.3V`
    *   `GND` -> HAT `GND`
    *   `SCK` -> HAT `GPIO 18` (I2S BCLK)
    *   `WS` -> HAT `GPIO 19` (I2S LRCLK/FS)
    *   `SD` -> HAT `GPIO 20` (I2S DIN / マイクからのデータ出力)
    *   `L/R` -> HAT `GND` (左チャンネル選択)
4.  **超音波センサー(HC-SR04)の接続:**
    *   HATのGPIOブレイクアウトピンに接続。
    *   `VCC` -> HAT `5V` (センサーによっては3.3V可 - データシート確認)
    *   `Trig` -> HAT `GPIO 21`
    *   `Echo` -> HAT `GPIO 22`
    *   `GND` -> HAT `GND`
5.  **ブザーの接続:**
    *   HATのGPIOブレイクアウトピンに接続。
    *   `Signal/IO` -> HAT `GPIO 23`
    *   `VCC/+` -> HAT `3.3V` (または `5V`)
    *   `GND/-` -> HAT `GND`
6.  **ロボットの組み立て:** Pi/HAT、サーボ、センサー、ブザーをシャーシに取り付けます。配線が動作を妨げないように整理します。

### 4. ソフトウェアのセットアップ (Software Setup)

1.  **OSのインストール:** Raspberry Pi ImagerでRaspberry Pi OS (LiteまたはDesktop、Pi Zeroには32-bit推奨) をSDカードに書き込みます。詳細オプション(⚙️)でホスト名、SSH有効化、ユーザー/パスワード、WiFiを設定します。
2.  **初回起動と接続:** SDカードを挿入し電源接続。数分待って起動後、SSHで接続 (`ssh <ユーザー名>@<ホスト名>.local` または `ssh <ユーザー名>@<IPアドレス>`)。
3.  **システムアップデート:** OSとパッケージを最新化します：
    ```bash
    sudo apt update
    sudo apt full-upgrade -y
    sudo reboot
    ```
    *(再起動後、SSH再接続)*
4.  **I2Sインターフェースの有効化:**
    *   ブート設定ファイルを編集：
        ```bash
        sudo nano /boot/firmware/config.txt
        # または: sudo nano /boot/config.txt
        ```
    *   ファイルの末尾に以下を追加：
        ```text
        # Enable I2S audio interface for Microphone
        dtparam=i2s=on
        dtoverlay=googlevoicehat-soundcard
        ```
    *   保存 (`Ctrl+X`, `Y`, `Enter`) して再起動：`sudo reboot`
5.  **システム依存関係のインストール:** Pythonパッケージに必要なライブラリをインストール：
    ```bash
    sudo apt install -y python3-dev python3-pip python3-venv build-essential libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg flac libatlas-base-dev
    ```
6.  **プロジェクトディレクトリと仮想環境の作成 (推奨):**
    ```bash
    mkdir ~/ninja_robot_v4 # または好きな名前
    cd ~/ninja_robot_v4
    python3 -m venv NinjaRobot # NinjaRobot という名前で仮想環境作成
    source NinjaRobot/bin/activate # 環境を有効化
    ```
    *(ターミナルプロンプトの先頭に `(NinjaRobot)` が表示されます)*
7.  **Pythonライブラリのインストール:** (仮想環境が有効なことを確認)
    ```bash
    pip install --upgrade pip
    pip install RPi.GPIO google-generativeai SpeechRecognition gTTS pygame Flask google-cloud-speech
    ```
    *(Pi Zeroでは時間がかかります)*
    *Once encountering error can try the following steps*
    1. deactivate virtual enviroment
    2. Update Package Lists: Make sure your package list is up-to-date:
       ```bash
       sudo apt update
       ```
    3. install Cargo:
       ```bash
       sudo apt install cargo -y
       ```
    4. Verify Installation (Optional): After it finishes, you can check the versions:
       ```bash
       cargo --version
       rustc --version
       ```
    5. activate virtual enviroment and install library again

### 5. コードのセットアップ (Code Setup)

1.  **コードファイルのダウンロード/コピー:** 以下のPythonファイルをプロジェクトディレクトリ (`~/ninja_robot_v4`) に配置します：
    *   `Ninja_Movements_v1.py`
    *   `Ninja_Buzzer.py`
    *   `Ninja_Distance.py`
    *   `ninja_core.py` (V1.4以降の機能を含む最終版)
    *   `Ninja_Voice_Control.py` (「Robot Mic」モード用)
    *   `web_interface.py` (機能を統合した最終版Flaskサーバー)
2.  **`templates` ディレクトリの作成:** プロジェクトディレクトリ内：
    ```bash
    mkdir templates
    ```
3.  **`index.html` の作成:** `templates` ディレクトリ内に `index.html` ファイルを作成し、Webインターフェース用の最終HTML/CSS/JavaScriptコードをペーストします。

### 6. 設定 (Configuration)

1.  **Google Gemini APIキー:**
    *   コアロジックファイルを編集：`nano ninja_core.py`
    *   `GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"` の行を探します。
    *   `"YOUR_GOOGLE_API_KEY"` を実際のキー（Google AI StudioまたはGoogle Cloudから取得）に置き換えます。
    *   **重要:** APIキーは安全に保管し、公開しないでください。本番環境では環境変数などを検討してください。
    *   ファイルを保存 (`Ctrl+X`, `Y`, `Enter`)。
2.  **(オプション) Robot Mic 感度調整:**
    *   「Robot Mic」モードの認識が悪い場合、`Ninja_Voice_Control.py` の `recognizer.energy_threshold` を調整します。
    *   まずWeb UIから一度実行し、`Ambient noise adjustment complete` の後の値を確認します。
    *   スクリプトを停止し（Flaskサーバーのターミナルで `Ctrl+C` 後、UIでStop等）、値を調整（音声を聞き逃すなら高く、ノイズで誤動作するなら低く）。必要なら `recognizer.adjust_for_ambient_noise(...)` 行をコメントアウトします。ファイルを保存します。

### 7. アプリケーションの実行 (Running the Application)

1.  **環境の有効化:** プロジェクトディレクトリに移動し、仮想環境を有効化（使用している場合）：
    ```bash
    cd ~/ninja_robot_v4
    source .venv/bin/activate
    ```
2.  **PiのIPアドレス確認:**
    ```bash
    hostname -I | awk '{print $1}'
    ```
    *(表示されたIPアドレスをメモ)*
3.  **Webサーバーの起動:**
    ```bash
    python3 web_interface.py
    ```
    *(`http://0.0.0.0:5000` で実行中といったメッセージを確認)*
4.  **Webインターフェースへのアクセス:** （Piと同じWiFi上の）他のデバイスのブラウザで以下にアクセス：
    `http://<YOUR_PI_IP_ADDRESS>:5000`
    *( `<YOUR_PI_IP_ADDRESS>` を実際のIPに置換)*

### 8. インターフェースの使用方法 (Using the Interface)

*   **初期状態:** 「Controller」モードで起動します。
*   **Controller Mode:** 画面上のボタン（D-Pad, アクション△/□/○/×, スピード, Rest等）でロボットを直接操作します。このモードのボタンを使うと「Robot Mic」モードは自動停止します。
*   **Browser Mic Mode:**
    1.  「Browser Mic」ボタンでモード有効化。
    2.  再度「Browser Mic」ボタン（表示が「Listening...」に変わる）でブラウザ経由の音声認識開始。マイク許可が必要な場合があります。
    3.  はっきりと話します。
    4.  認識されたテキストとロボットの応答/アクションがステータス欄に表示されます。
    5.  「Listening...」をクリックすると現在の認識が停止します。
*   **Robot Mic Mode:**
    1.  「Speak to Robot」ボタンをクリック。ボタン表示が「Robot Mic (ON)」に変わるはずです。Pi上で音声制御スクリプトがバックグラウンド起動します。
    2.  「Robot Mic Dialog」欄に、バックグラウンドスクリプトの会話ログが表示されます。
    3.  ロボット本体のINMP441マイクに向かって話します。コマンドにはウェイクワード「ninja」（例：「ninja walk」、「ninja say hello」）を使うか、質問は直接話します。
    4.  停止するには「Controller」または「Browser Mic」ボタンをクリックします。

### 9. トラブルシューティング (Troubleshooting)

*   **Pythonエラー (`NameError`, `ImportError`):** ライブラリ（ステップ4.7）が有効な環境にインストールされているか確認。ファイル配置を確認。
*   **ハードウェア初期化失敗:** ハードウェア接続（ステップ3）を再確認。`web_interface.py` 起動時のコンソール出力でエラー詳細を確認。
*   **"Robot Mic" 起動失敗:** `web_interface.py` 起動時のコンソール出力、特に`subprocess.Popen`のエラーや `Ninja_Voice_Control.py` の stderr 出力（オーディオデバイス関連が多い）を確認。I2S設定（ステップ4.4）を再確認。
*   **音声認識問題:** マイク接続確認。感度調整（ステップ6.2 Robot Mic）。ブラウザマイク許可（Browser Mic）。インターネット接続確認（両方）。
*   **Geminiエラー:** APIキー確認（ステップ6.1）。Google Cloud プロジェクトステータス確認（API有効か？）。
*   **ロボット動作問題:** サーボ接続確認（ステップ3.2）。`Ninja_Movements_v1.py` の角度定義確認。電源供給確認。
*   **Web UI無応答:** Flaskサーバー(`web_interface.py`)がPiで実行中か確認。IPアドレスとネットワーク接続確認。ブラウザコンソールでJavaScriptエラー確認。

### 10. アプリケーションの停止 (Stopping the Application)

*   `web_interface.py` を実行しているターミナルで `Ctrl+C` を押します。
*   `atexit` クリーンアップ関数が自動実行され、動作停止、バックグラウンドスクリプトへの停止信号送信、「thanks」サウンド再生、レスト位置への移動、GPIOリソース解放が行われるはずです。

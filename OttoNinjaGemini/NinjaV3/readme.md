# Building a Voice-Controlled Ninja Robot with Raspberry Pi & Gemini

This tutorial guides you through building a voice-controlled robot using a Raspberry Pi Zero, DFRobot IO Expansion HAT, INMP441 I2S microphone, servos, an ultrasonic sensor, a buzzer, and Google's Gemini AI for natural language understanding.

The robot can be controlled via:
1.  A web interface using controller buttons.
2.  Voice commands via the web browser's microphone.
3.  Voice commands spoken directly to the robot's onboard I2S microphone.

---

## Part 1: English Tutorial

### 1. Prerequisites - Hardware

You will need the following components:

*   **Raspberry Pi Zero:** Preferably Pi Zero W or WH (with headers) for easier WiFi setup.
*   **Micro SD Card:** 8GB or larger, with Raspberry Pi OS installed.
*   **Power Supply:** A reliable 5V power supply suitable for the Pi Zero and connected peripherals (minimum 2.5A recommended).
*   **DFRobot IO Expansion HAT:** Ensure it's compatible with the Raspberry Pi Zero GPIO layout.
*   **INMP441 I2S Microphone Module:** For onboard voice input.
*   **HC-SR04 Ultrasonic Distance Sensor:** For obstacle detection.
*   **Active Buzzer Module:** For sound feedback.
*   **SG90 Servos (x4):** Or similar 3-pin hobby servos for movement (adjust code if using different types/number).
*   **Robot Chassis/Frame:** To mount the Pi, HAT, servos, sensor, and buzzer. (This tutorial assumes you have a frame where 4 servos provide movement).
*   **Jumper Wires:** Female-to-Female and potentially Male-to-Female wires for connections.
*   **Computer:** For initial Pi setup and accessing the web interface.
*   **(Optional) USB Keyboard/Mouse & HDMI Monitor/Adapter:** For initial Pi setup if not using SSH.

### 2. Hardware Assembly

**ALWAYS POWER DOWN THE RASPBERRY PI BEFORE CONNECTING OR DISCONNECTING COMPONENTS.**

1.  **Mount HAT:** Carefully align and securely attach the DFRobot IO Expansion HAT onto the Raspberry Pi Zero's 40-pin GPIO header.
2.  **Connect Servos:** Connect the 4 servos to the servo headers on the Expansion HAT. Pay attention to the correct pins (Signal, VCC/+, GND/-). Note which servo connects to which numbered port (0-3) on the HAT, as this corresponds to the IDs in `Ninja_Movements_v1.py`. The default code assumes:
    *   Servo 0: Right Leg/Hip
    *   Servo 1: Left Leg/Hip
    *   Servo 2: Right Foot/Ankle
    *   Servo 3: Left Foot/Ankle
    *(Adjust comments in `Ninja_Movements_v1.py` and potentially angle values if your setup differs).*
3.  **Connect I2S Microphone (INMP441):** Use jumper wires to connect the mic module to the **HAT's GPIO breakout pins**. Refer to the HAT's documentation for the exact pin locations corresponding to the Pi's BCM numbers.
    *   INMP441 `VDD` -> HAT `3.3V`
    *   INMP441 `GND` -> HAT `GND`
    *   INMP441 `SCK` -> HAT `GPIO 18` (I2S BCLK)
    *   INMP441 `WS` -> HAT `GPIO 19` (I2S LRCLK/FS)
    *   INMP441 `SD` -> HAT `GPIO 20` (I2S DIN/DOUT from Mic)
    *   INMP441 `L/R` -> HAT `GND` (Selects one channel, usually Left)
4.  **Connect Ultrasonic Sensor (HC-SR04):** Connect to the HAT's GPIO breakout pins. The code uses:
    *   HC-SR04 `VCC` -> HAT `5V` (or `3.3V` if sensor supports it - check datasheet)
    *   HC-SR04 `Trig` -> HAT `GPIO 21`
    *   HC-SR04 `Echo` -> HAT `GPIO 22`
    *   HC-SR04 `GND` -> HAT `GND`
5.  **Connect Buzzer:** Connect to the HAT's GPIO breakout pins. The code uses:
    *   Buzzer `Signal/IO` -> HAT `GPIO 23`
    *   Buzzer `VCC/+` -> HAT `3.3V` (or `5V` depending on the module)
    *   Buzzer `GND/-` -> HAT `GND`
6.  **Assemble Robot:** Mount all components securely onto your robot chassis. Ensure wires are tidy and won't interfere with movement.

### 3. Software Setup

1.  **Install Raspberry Pi OS:** Use the Raspberry Pi Imager tool on your computer to flash Raspberry Pi OS (32-bit or 64-bit, Lite or Desktop) onto your SD card. Enable SSH and configure WiFi credentials using the Imager settings for headless setup if desired.
2.  **Boot Pi & Connect:** Insert the SD card, connect peripherals (if not headless), and power up the Pi. Connect to it via SSH or log in directly.
3.  **System Update:** Open a terminal and update the system:
    ```bash
    sudo apt update
    sudo apt full-upgrade -y
    sudo reboot # Reboot after major upgrades
    ```
4.  **Enable I2S:**
    *   Edit the boot config file. The path depends on your OS version:
        *   Newer (Bullseye/Bookworm 64-bit often): `sudo nano /boot/firmware/config.txt`
        *   Older (or 32-bit): `sudo nano /boot/config.txt`
    *   Add the following lines to the **end** of the file:
        ```text
        # Enable I2S audio interface
        dtparam=i2s=on

        # Load the Google Voice HAT overlay (works well for INMP441)
        dtoverlay=googlevoicehat-soundcard
        ```
    *   Save the file (`Ctrl+X`, then `Y`, then `Enter`) and reboot: `sudo reboot`
5.  **Install System Dependencies:** Install necessary libraries for audio, math operations, etc.:
    ```bash
    sudo apt install -y portaudio19-dev ffmpeg libopenblas-base python3-dev python3-pip python3-venv git
    ```
    *(Note: `python3-venv` is for creating virtual environments, which is recommended)*
6.  **Create Virtual Environment (Recommended):**
    ```bash
    mkdir ~/ninja_robot
    cd ~/ninja_robot
    python3 -m venv .venv
    source .venv/bin/activate
    # Your prompt should now show (.venv)
    # To deactivate later: deactivate
    ```
7.  **Install Python Libraries:** Install the required Python packages using pip (ensure your virtual environment is active):
    ```bash
    pip install --upgrade pip
    pip install Flask google-generativeai SpeechRecognition gTTS gpiozero pygame sounddevice PyAudio RPi.GPIO DFRobot_RaspberryPi_Expansion_Board
    ```
    *(This might take some time on a Pi Zero)*

### 4. Code Setup

1.  **Get the Code:** Make sure you have the final versions of the following Python files from our conversation:
    *   `Ninja_Movements_v1.py` (Servo movement definitions)
    *   `Ninja_Buzzer.py` (Sound definitions, includes 'stop')
    *   `Ninja_Distance.py` (Ultrasonic sensor functions)
    *   `ninja_core.py` (Core logic, Gemini interaction, hardware control - V1.4 or later)
    *   `Ninja_Voice_Control.py` (Script for "Robot Mic" mode)
    *   `web_interface.py` (Flask web server - the final combined version)
2.  **Directory Structure:** Place all the `.py` files listed above into the directory you created (e.g., `~/ninja_robot`).
3.  **Create `templates` Directory:** Inside your project directory (`~/ninja_robot`), create a subdirectory named `templates`:
    ```bash
    mkdir templates
    ```
4.  **Create `index.html`:** Inside the `templates` directory, create a file named `index.html`. Copy and paste the final HTML/CSS/JavaScript code for the web interface into this file.

### 5. Configuration

1.  **Google API Key:**
    *   Open the `ninja_core.py` file: `nano ninja_core.py`
    *   Find the line: `GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"`
    *   Replace `"YOUR_GOOGLE_API_KEY"` with your actual API key obtained from Google AI Studio or Google Cloud (ensure the Vertex AI API is enabled in your Google Cloud project if using a Cloud key).
    *   **Security Note:** Avoid committing your API key directly into public Git repositories. Consider using environment variables or other secrets management for more secure deployments.
    *   Save the file (`Ctrl+X`, `Y`, `Enter`).
2.  **(Optional) Microphone Tuning:**
    *   If voice recognition in "Robot Mic" mode seems poor, you might need to tune the `recognizer.energy_threshold` in `Ninja_Voice_Control.py`. First, run the script and see the value reported after the initial `adjust_for_ambient_noise`. If it consistently misses speech or triggers on noise, try manually setting a different value in the script (e.g., `recognizer.energy_threshold = 600`) and comment out the `recognizer.adjust_for_ambient_noise(...)` line. Experiment to find a good value for your environment.
    *   Ensure the correct microphone index is being found by `find_mic_index` in `Ninja_Voice_Control.py`. Check the script's console output when it starts. If it defaults, adjust the `keyword` in `find_mic_index(keyword="...")`.

### 6. Running the Application

1.  **Navigate to Directory:** Open a terminal on the Pi and go to your project directory (ensure the virtual environment is active if you created one):
    ```bash
    cd ~/ninja_robot
    source .venv/bin/activate # If using venv
    ```
2.  **Find Pi's IP Address:** Get the IP address your Pi is using on the local network:
    ```bash
    hostname -I
    ```
    (Note the first IP address listed, e.g., `192.168.1.15`)
3.  **Run the Web Server:** Start the Flask application:
    ```bash
    python3 web_interface.py
    ```
    You should see output indicating the server is running, typically on `http://0.0.0.0:5000`.
4.  **Access the Web Interface:** Open a web browser on your phone or computer (connected to the **same WiFi network** as the Pi) and navigate to:
    `http://<YOUR_PI_IP_ADDRESS>:5000`
    (Replace `<YOUR_PI_IP_ADDRESS>` with the actual IP address you found in step 2).

### 7. Using the Interface

*   **Controller Mode:** The default mode. Use the D-Pad, Action buttons (△/□ for Walk/Run mode), Speed buttons, and Rest/Hello/Stop buttons to directly control the robot. Using any controller button will automatically stop the "Robot Mic" mode if it's running.
*   **Browser Mic Mode:**
    *   Click the "Browser Mic" button to switch to this mode.
    *   Click it *again* to start listening (it will say "Listening..."). Grant microphone permission in your browser if prompted.
    *   Speak your command (e.g., "walk forward slowly") or question (e.g., "what is the capital of France").
    *   The transcribed text and the robot's action/response will appear in the status area.
    *   Clicking "Listening..." stops the current recognition attempt.
*   **Robot Mic Mode:**
    *   Click the "Speak to Robot" button. The button text should change to "Robot Mic (ON)". This starts the `Ninja_Voice_Control.py` script in the background.
    *   The "Robot Mic Dialog" area will show the conversation log from the background script.
    *   Speak directly to the INMP441 microphone attached to the robot. Use the wake word "ninja" for commands (e.g., "ninja run fast", "ninja say hello") or ask questions directly.
    *   To stop this mode, click either the "Controller" or "Browser Mic" button. This sends a stop signal to the background script.

### 8. Troubleshooting

*   **`NameError` or `ImportError`:** Make sure all required libraries are installed in the correct environment (`pip install ...`). Ensure all `.py` files are in the same directory.
*   **Hardware Not Initialized Error:** Check all physical connections carefully (power, GND, signal pins). Ensure the DFRobot HAT is seated properly. Check the terminal output when `web_interface.py` starts for specific errors during `ninja_core.initialize_hardware()`.
*   **Cannot Start "Robot Mic" Mode:** Check the terminal output of `web_interface.py` when you click the button. Look for errors from `subprocess.Popen` or stderr output from `Ninja_Voice_Control.py` itself (like audio device errors). Ensure I2S is correctly enabled in `/boot/firmware/config.txt` (or `/boot/config.txt`).
*   **Poor Voice Recognition (Robot Mic):** Check microphone connections. Tune `energy_threshold` in `Ninja_Voice_Control.py`. Reduce background noise.
*   **Poor Voice Recognition (Browser Mic):** Ensure you grant microphone permission in the browser. Check your computer/phone microphone settings. Try speaking more clearly. Requires internet access for Google Web Speech API.
*   **Gemini Errors (API Key / 404 / Permissions):** Double-check your API key in `ninja_core.py`. Ensure the Gemini API (or Vertex AI API) is enabled in your Google Cloud project. Make sure the chosen model (`gemini-1.5-flash-latest`) is available to your account/region.
*   **ALSA/JACK Noise in Console:** These are often harmless warnings. You can suppress them when running the final script using shell redirection: `python3 web_interface.py 2>/dev/null` (but this hides real errors too).
*   **Robot Doesn't Move Correctly:** Check servo connections to the HAT ports (0-3). Verify the angles defined in `Ninja_Movements_v1.py` (`reset_servos`, `walk`, `run`, etc.) match your robot's physical constraints.

### 9. Stopping the Application

*   Go to the terminal where `web_interface.py` is running and press `Ctrl+C`.
*   The cleanup function should automatically run, stopping any movement, signalling the background script (if running) to stop, playing the "thanks" sound, moving the robot to rest, and cleaning up GPIO resources.

---
---

## Part 2: Japanese Tutorial (日本語チュートリアル)

### Voice Control Ninja Robot (Raspberry Pi & Gemini) の構築

このチュートリアルでは、Raspberry Pi Zero、DFRobot IO Expansion HAT、INMP441 I2Sマイク、サーボ、超音波センサー、ブザー、そして自然言語理解のためのGoogle Gemini AIを使用して、音声制御ロボットを構築する手順を説明します。

ロボットは以下の方法で制御できます：
1.  コントローラーボタンを使用したウェブインターフェース。
2.  ウェブブラウザのマイクを介した音声コマンド。
3.  ロボットに搭載されたI2Sマイクに直接話しかける音声コマンド。

---

### 1. 準備 - ハードウェア

以下のコンポーネントが必要です：

*   **Raspberry Pi Zero:** Pi Zero W または WH (ヘッダー付き) がWiFi設定に便利です。
*   **Micro SDカード:** 8GB以上、Raspberry Pi OSインストール済み。
*   **電源:** Pi Zeroと接続された周辺機器に適した安定した5V電源（最低2.5A推奨）。
*   **DFRobot IO Expansion HAT:** Raspberry Pi ZeroのGPIOレイアウトと互換性があることを確認してください。
*   **INMP441 I2S マイクモジュール:** オンボード音声入力用。
*   **HC-SR04 超音波距離センサー:** 障害物検出用。
*   **アクティブブザーモジュール:** 音声フィードバック用。
*   **SG90 サーボ (x4):** または同等の3ピンホビーサーボ（種類や数が異なる場合はコードを調整）。
*   **ロボットシャーシ/フレーム:** Pi、HAT、サーボ、センサー、ブザーを取り付けるため。（このチュートリアルでは4つのサーボで移動するフレームを想定）。
*   **ジャンパーワイヤー:** メス-メス、場合によってはオス-メスワイヤー。
*   **コンピュータ:** Piの初期設定とウェブインターフェースへのアクセス用。
*   **(オプション) USBキーボード/マウス & HDMIモニター/アダプター:** SSHを使用しない場合の初期Pi設定用。

### 2. ハードウェアの組み立て

**コンポーネントの接続・切断を行う前には、必ずRaspberry Piの電源を切ってください。**

1.  **HATの取り付け:** DFRobot IO Expansion HATをRaspberry Pi Zeroの40ピンGPIOヘッダーに慎重に位置合わせし、しっかりと取り付けます。
2.  **サーボの接続:** 4つのサーボをExpansion HATのサーボヘッダーに接続します。ピン（Signal, VCC/+, GND/-）の向きに注意してください。HATのどの番号付きポート（0-3）にどのサーボを接続したかメモしておきます。これは`Ninja_Movements_v1.py`のIDに対応します。デフォルトのコードでは以下を想定しています：
    *   サーボ 0: 右脚/股関節
    *   サーボ 1: 左脚/股関節
    *   サーボ 2: 右足/足首
    *   サーボ 3: 左足/足首
    *(構成が異なる場合は`Ninja_Movements_v1.py`のコメントや角度値を調整してください)*
3.  **I2Sマイク(INMP441)の接続:** ジャンパーワイヤーを使用して、マイクモジュールを**HATのGPIOブレイクアウトピン**に接続します。PiのBCM番号に対応するHAT上の正確なピン位置については、HATのドキュメントを参照してください。
    *   INMP441 `VDD` -> HAT `3.3V`
    *   INMP441 `GND` -> HAT `GND`
    *   INMP441 `SCK` -> HAT `GPIO 18` (I2S BCLK)
    *   INMP441 `WS`  -> HAT `GPIO 19` (I2S LRCLK/FS)
    *   INMP441 `SD`  -> HAT `GPIO 20` (I2S DIN/DOUT from Mic)
    *   INMP441 `L/R` -> HAT `GND` (通常は左チャンネルを選択)
4.  **超音波センサー(HC-SR04)の接続:** HATのGPIOブレイクアウトピンに接続します。コードでは以下を使用します：
    *   HC-SR04 `VCC` -> HAT `5V` (センサーが対応していれば `3.3V` - データシートを確認)
    *   HC-SR04 `Trig`-> HAT `GPIO 21`
    *   HC-SR04 `Echo`-> HAT `GPIO 22`
    *   HC-SR04 `GND` -> HAT `GND`
5.  **ブザーの接続:** HATのGPIOブレイクアウトピンに接続します。コードでは以下を使用します：
    *   Buzzer `Signal/IO` -> HAT `GPIO 23`
    *   Buzzer `VCC/+` -> HAT `3.3V` (またはモジュールに応じて `5V`)
    *   Buzzer `GND/-` -> HAT `GND`
6.  **ロボットの組み立て:** すべてのコンポーネントをロボットシャーシにしっかりと取り付けます。ワイヤーが動きを妨げないように整理します。

### 3. ソフトウェアのセットアップ

1.  **Raspberry Pi OSのインストール:** コンピュータでRaspberry Pi Imagerツールを使用し、Raspberry Pi OS（32ビットまたは64ビット、LiteまたはDesktop）をSDカードに書き込みます。必要に応じて、Imagerの設定でSSHを有効にし、WiFi認証情報を設定してヘッドレスセットアップを行います。
2.  **Piの起動と接続:** SDカードを挿入し、周辺機器を接続（ヘッドレスでない場合）、Piの電源を入れます。SSH経由で接続するか、直接ログインします。
3.  **システムアップデート:** ターミナルを開き、システムをアップデートします：
    ```bash
    sudo apt update
    sudo apt full-upgrade -y
    sudo reboot # 大規模なアップグレード後は再起動
    ```
4.  **I2Sの有効化:**
    *   ブート設定ファイルを編集します。パスはOSバージョンによって異なります：
        *   新しいOS (Bullseye/Bookworm 64-bitなど): `sudo nano /boot/firmware/config.txt`
        *   古いOS (または32-bit): `sudo nano /boot/config.txt`
    *   ファイルの**末尾**に以下の行を追加します：
        ```text
        # Enable I2S audio interface
        dtparam=i2s=on

        # Load the Google Voice HAT overlay (works well for INMP441)
        dtoverlay=googlevoicehat-soundcard
        ```
    *   ファイルを保存し (`Ctrl+X`, `Y`, `Enter`)、再起動します：`sudo reboot`
5.  **システム依存関係のインストール:** オーディオ、数値計算などに必要なライブラリをインストールします：
    ```bash
    sudo apt install -y portaudio19-dev ffmpeg libopenblas-base python3-dev python3-pip python3-venv git
    ```
    *(注: `python3-venv` は仮想環境作成用で、推奨されます)*
6.  **仮想環境の作成 (推奨):**
    ```bash
    mkdir ~/ninja_robot
    cd ~/ninja_robot
    python3 -m venv .venv
    source .venv/bin/activate
    # プロンプトの先頭に (.venv) が表示されるはずです
    # 後で無効化する場合: deactivate
    ```
7.  **Pythonライブラリのインストール:** pipを使用して必要なPythonパッケージをインストールします（仮想環境がアクティブであることを確認してください）：
    ```bash
    pip install --upgrade pip
    pip install Flask google-generativeai SpeechRecognition gTTS gpiozero pygame sounddevice PyAudio RPi.GPIO DFRobot_RaspberryPi_Expansion_Board
    ```
    *(Pi Zeroでは時間がかかる場合があります)*

### 4. コードのセットアップ

1.  **コードの入手:** 会話で開発した以下のPythonファイルの最終バージョンがあることを確認してください：
    *   `Ninja_Movements_v1.py` (サーボ動作定義)
    *   `Ninja_Buzzer.py` (サウンド定義、「stop」を含む)
    *   `Ninja_Distance.py` (超音波センサー関数)
    *   `ninja_core.py` (コアロジック、Gemini連携、ハードウェア制御 - V1.4以降)
    *   `Ninja_Voice_Control.py` (「Robot Mic」モード用スクリプト)
    *   `web_interface.py` (Flaskウェブサーバー - 最終結合バージョン)
2.  **ディレクトリ構造:** 上記の`.py`ファイルをすべて作成したディレクトリ（例：`~/ninja_robot`）に配置します。
3.  **`templates`ディレクトリの作成:** プロジェクトディレクトリ（`~/ninja_robot`）内に、`templates`という名前のサブディレクトリを作成します：
    ```bash
    mkdir templates
    ```
4.  **`index.html`の作成:** `templates`ディレクトリ内に、`index.html`という名前のファイルを作成します。ウェブインターフェース用の最終的なHTML/CSS/JavaScriptコードをこのファイルにコピー＆ペーストします。

### 5. 設定

1.  **Google APIキー:**
    *   `ninja_core.py`ファイルを開きます：`nano ninja_core.py`
    *   `GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"` という行を見つけます。
    *   `"YOUR_GOOGLE_API_KEY"` を、Google AI Studio または Google Cloud から取得した実際のAPIキーに置き換えます（Cloudキーを使用する場合は、Google CloudプロジェクトでVertex AI APIが有効になっていることを確認してください）。
    *   **セキュリティ注:** APIキーを公開Gitリポジトリに直接コミットしないでください。より安全なデプロイのためには、環境変数や他のシークレット管理方法の使用を検討してください。
    *   ファイルを保存します (`Ctrl+X`, `Y`, `Enter`)。
2.  **(オプション) マイク調整:**
    *   「Robot Mic」モードでの音声認識がうまくいかない場合、`Ninja_Voice_Control.py`の`recognizer.energy_threshold`を調整する必要があるかもしれません。まずスクリプトを実行し、最初の`adjust_for_ambient_noise`の後に報告される値を確認します。音声を聞き逃したり、ノイズで誤トリガーしたりする場合は、スクリプトで手動で異なる値を設定（例：`recognizer.energy_threshold = 600`）し、`recognizer.adjust_for_ambient_noise(...)`の行をコメントアウトしてみてください。環境に適した値を見つけるために実験してください。
    *   `Ninja_Voice_Control.py`の`find_mic_index`が正しいマイクインデックスを見つけていることを確認してください。スクリプト起動時のコンソール出力を確認します。デフォルトにフォールバックする場合は、`find_mic_index(keyword="...")`の`keyword`を調整してください。

### 6. アプリケーションの実行

1.  **ディレクトリへ移動:** Piのターミナルを開き、プロジェクトディレクトリに移動します（仮想環境を作成した場合はアクティブにします）：
    ```bash
    cd ~/ninja_robot
    source .venv/bin/activate # venvを使用している場合
    ```
2.  **PiのIPアドレスを確認:** Piがローカルネットワークで使用しているIPアドレスを取得します：
    ```bash
    hostname -I
    ```
    （リストの最初のIPアドレスをメモします。例：`192.168.1.15`）
3.  **ウェブサーバーの実行:** Flaskアプリケーションを起動します：
    ```bash
    python3 web_interface.py
    ```
    サーバーが実行中であることを示す出力（通常は`http://0.0.0.0:5000`）が表示されるはずです。
4.  **ウェブインターフェースへのアクセス:** （Piと同じWiFiネットワークに接続された）携帯電話またはコンピュータのウェブブラウザを開き、以下のアドレスにアクセスします：
    `http://<YOUR_PI_IP_ADDRESS>:5000`
    （`<YOUR_PI_IP_ADDRESS>`をステップ2で見つけた実際のIPアドレスに置き換えてください）。

### 7. インターフェースの使用

*   **Controller Mode:** デフォルトのモード。D-Pad、アクションボタン（△/□でWalk/Runモード切替）、スピードボタン、Rest/Hello/Stopボタンを使用してロボットを直接制御します。コントローラーボタンを使用すると、「Robot Mic」モードが実行中の場合は自動的に停止します。
*   **Browser Mic Mode:**
    *   「Browser Mic」ボタンをクリックしてこのモードに切り替えます。ボタンがハイライトされます。これも「Robot Mic」モードが実行中の場合は停止させます。
    *   もう一度クリックすると聞き取りが開始されます（「Listening...」と表示）。初めて使用する際にブラウザからマイクの許可を求められる場合があります。
    *   コマンド（例：「walk forward slowly」）または質問（例：「what is the capital of France」）を話します。
    *   文字起こしされたテキストとロボットのアクション/応答がステータスエリアに表示されます。
    *   「Listening...」をクリックすると、現在の認識試行が停止します。
*   **Robot Mic Mode:**
    *   「Speak to Robot」ボタンをクリックします。ボタンのテキストが「Robot Mic (ON)」に変わるはずです。これにより、バックグラウンドで`Ninja_Voice_Control.py`スクリプトが起動します。
    *   「Robot Mic Dialog」エリアに、バックグラウンドスクリプトからの会話ログ（例：「Listening...」、「Heard: ...」、「ASSISTANT SPEAKING: ...」）が定期的に表示されるようになります。
    *   ロボットに取り付けられたINMP441マイクに直接話しかけます。コマンドにはウェイクワード「ninja」（例：「ninja run fast」、「ninja say hello」）を使用するか、直接質問します。
    *   このモードを停止するには、「Controller」ボタンまたは「Browser Mic」ボタンをクリックします。これにより、バックグラウンドスクリプトに停止信号が送信されます。

### 8. トラブルシューティング

*   **`NameError` または `ImportError`:** 必要なライブラリがすべて正しい環境にインストールされていることを確認してください (`pip install ...`)。すべての`.py`ファイルが同じディレクトリにあることを確認してください。
*   **Hardware Not Initialized Error:** すべての物理接続（電源、GND、信号ピン）を注意深く確認してください。DFRobot HATが正しく装着されていることを確認してください。`web_interface.py`起動時のターミナル出力で、`ninja_core.initialize_hardware()`中の具体的なエラーを確認してください。
*   **"Robot Mic" モードが起動できない:** ボタンをクリックした際の`web_interface.py`のターミナル出力を確認してください。`subprocess.Popen`からのエラーや、`Ninja_Voice_Control.py`自体のstderr出力（オーディオデバイスエラーなど）を探します。I2Sが`/boot/firmware/config.txt`（または`/boot/config.txt`）で正しく有効になっていることを確認してください。
*   **音声認識品質が悪い (Robot Mic):** マイクの接続を確認してください。`Ninja_Voice_Control.py`の`energy_threshold`を調整してください。背景ノイズを減らしてください。
*   **音声認識品質が悪い (Browser Mic):** ブラウザでマイクの許可を与えていることを確認してください。コンピュータ/携帯電話のマイク設定を確認してください。よりはっきりと話してみてください。Google Web Speech APIにはインターネット接続が必要です。
*   **Geminiエラー (APIキー / 404 / 権限):** `ninja_core.py`のAPIキーを再確認してください。Google CloudプロジェクトでGemini API（またはVertex AI API）が有効になっていることを確認してください。選択したモデル（`gemini-1.5-flash-latest`）がアカウント/リージョンで利用可能であることを確認してください。
*   **コンソールのALSA/JACKノイズ:** これらは多くの場合無害な警告です。最終的なスクリプト実行時にシェルリダイレクトを使用して抑制できます：`python3 web_interface.py 2>/dev/null`（ただし、実際のエラーも隠してしまいます）。
*   **ロボットが正しく動かない:** HATポート（0-3）へのサーボ接続を確認してください。`Ninja_Movements_v1.py`で定義されている角度（`reset_servos`, `walk`, `run`など）がロボットの物理的な制約と一致していることを確認してください。

### 9. アプリケーションの停止

*   `web_interface.py`を実行しているターミナルに移動し、`Ctrl+C`を押します。
*   クリーンアップ関数が自動的に実行され、すべての動作を停止し、バックグラウンドスクリプト（実行中の場合）に停止信号を送り、「thanks」サウンドを再生し、ロボットをレスト位置に移動させ、GPIOリソースをクリーンアップするはずです。

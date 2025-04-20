# Building a Voice-Controlled Ninja Robot with Raspberry Pi & Gemini

This tutorial guides you through building a small, interactive robot using a Raspberry Pi Zero, sensors, servos, and Google's Gemini AI for natural language understanding and control. You can interact with it using a web interface (controller buttons, browser microphone) or by speaking directly to the robot's onboard microphone.

このチュートリアルでは、Raspberry Pi Zero、センサー、サーボ、そして自然言語理解と制御のためにGoogleのGemini AIを使用して、小型の対話型ロボットを構築する方法を説明します。ウェブインターフェース（コントローラーボタン、ブラウザマイク）を使用するか、ロボットに搭載されたマイクに直接話しかけることで対話できます。

**Features:**
*   **Multiple Control Modes:** Controller GUI, Browser Microphone, Onboard Robot Microphone.
*   **Natural Language Understanding:** Uses Google Gemini to interpret commands and answer questions.
*   **Movement:** Walking, running (tire mode), turning, specific poses.
*   **Sound Feedback:** Buzzer provides audio cues.
*   **Obstacle Avoidance:** Ultrasonic sensor stops forward movement if an object is too close.
*   **Web Interface:** Control and monitor the robot via WiFi.

**機能:**
*   **複数の制御モード:** コントローラーGUI、ブラウザマイク、ロボット搭載マイク。
*   **自然言語理解:** Google Geminiを使用してコマンドを解釈し、質問に答えます。
*   **動作:** 歩行、走行（タイヤモード）、旋回、特定のポーズ。
*   **サウンドフィードバック:** ブザーが音声キューを提供します。
*   **障害物回避:** 超音波センサーが前方の物体を検知し、近すぎる場合にロボットを停止させます。
*   **ウェブインターフェース:** WiFi経由でロボットを制御および監視します。

---

## 1. Hardware Requirements | ハードウェア要件

*   Raspberry Pi Zero W or WH (W/WH recommended for WiFi) | Raspberry Pi Zero W または WH (WiFiのためW/WH推奨)
*   DFRobot IO Expansion HAT for Raspberry Pi (ensure compatibility with Pi Zero) | DFRobot Raspberry Pi用 IO拡張HAT (Pi Zeroとの互換性を確認)
*   INMP441 I2S MEMS Microphone Module | INMP441 I2S MEMSマイクモジュール
*   HC-SR04 Ultrasonic Distance Sensor | HC-SR04 超音波距離センサー
*   SG90 or MG90S Micro Servos (x4) | SG90 または MG90S マイクロサーボ (x4)
*   Active Buzzer Module | アクティブブザーモジュール
*   Micro SD Card (8GB+, Class 10 recommended) with Raspberry Pi OS | Raspberry Pi OSがインストールされたMicro SDカード (8GB以上、Class 10推奨)
*   5V Power Supply (Micro USB, capable of delivering 2.5A+) | 5V 電源 (Micro USB、2.5A以上供給可能なもの)
*   Jumper Wires (Female-to-Female, Female-to-Male as needed) | ジャンパーワイヤー (メス-メス、メス-オス 必要に応じて)
*   (Optional) Robot Chassis/Body to mount components | (オプション) コンポーネントを取り付けるためのロボットシャーシ/ボディ

---

## 2. Hardware Assembly | ハードウェアの組み立て

**⚠️ IMPORTANT:** Always disconnect the power supply before connecting or disconnecting components!
**⚠️ 重要:** 部品を接続または取り外す前に、必ず電源を切断してください！

1.  **Mount HAT:** Carefully align the DFRobot IO Expansion HAT onto the Raspberry Pi Zero's 40-pin GPIO header and press down firmly. | **HATの取り付け:** DFRobot IO拡張HATをRaspberry Pi Zeroの40ピンGPIOヘッダーに慎重に合わせ、しっかりと押し込みます。
2.  **Identify HAT Pins:** Consult your specific DFRobot HAT's documentation or pinout diagram. The following connections assume standard pin mappings often found on these HATs, but **VERIFY YOUR HAT'S PINS**. | **HATピンの特定:** 使用しているDFRobot HATのドキュメントまたはピン配置図を参照してください。以下の接続はこれらのHATでよく見られる標準的なピンマッピングを想定していますが、**必ずご自身のHATのピンを確認してください**。
3.  **Connect I2S Microphone (INMP441):** | **I2Sマイク(INMP441)の接続:**
    *   `VDD` -> HAT `3.3V`
    *   `GND` -> HAT `GND`
    *   `SCK` -> HAT `GPIO 18` (BCM 18 / I2S CLK)
    *   `WS`  -> HAT `GPIO 19` (BCM 19 / I2S FS/LRCLK)
    *   `SD`  -> HAT `GPIO 20` (BCM 20 / I2S DIN/DOUT)
    *   `L/R` -> HAT `GND` (Usually selects Left channel) | (通常、左チャンネルを選択)
4.  **Connect Ultrasonic Sensor (HC-SR04):** | **超音波センサー(HC-SR04)の接続:**
    *   `VCC` -> HAT `5V`
    *   `Trig`-> HAT `GPIO 21` (BCM 21)
    *   `Echo`-> HAT `GPIO 22` (BCM 22)
    *   `GND` -> HAT `GND`
5.  **Connect Buzzer:** | **ブザーの接続:**
    *   `Signal` (often marked `I/O` or `S`) -> HAT `GPIO 23` (BCM 23)
    *   `VCC` (+) -> HAT `3.3V` or `5V` (check buzzer module specs) | (ブザーモジュールの仕様を確認)
    *   `GND` (-) -> HAT `GND`
6.  **Connect Servos:** The DFRobot HAT library typically controls servos connected to dedicated servo ports on the HAT. Connect your four servos to the ports labeled `Servo 0`, `Servo 1`, `Servo 2`, and `Servo 3`. Pay attention to the pin order (usually Signal, VCC, GND). | **サーボの接続:** DFRobot HATライブラリは通常、HAT上の専用サーボポートに接続されたサーボを制御します。4つのサーボを`Servo 0`, `Servo 1`, `Servo 2`, `Servo 3`とラベル付けされたポートに接続します。ピンの順序（通常はシグナル、VCC、GND）に注意してください。
    *   *Mapping Assumption:* The code (`Ninja_Movements_v1.py`) assumes a mapping like: Right Leg (Hip), Left Leg (Hip), Right Foot (Ankle), Left Foot (Ankle). Adjust code/connections based on your robot build. | *マッピングの前提:* コード(`Ninja_Movements_v1.py`)は、右脚(股関節)、左脚(股関節)、右足(足首)、左足(足首)のようなマッピングを想定しています。ロボットの構造に合わせてコード/接続を調整してください。
7.  **Mount Components:** Securely mount all components onto your robot chassis/body. | **コンポーネントの取り付け:** すべてのコンポーネントをロボットシャーシ/ボディにしっかりと取り付けます。
8.  **Double Check Wiring:** Carefully review all connections before applying power. | **配線の再確認:** 電源を入れる前に、すべての接続を注意深く確認してください。

---

## 3. Software Setup | ソフトウェアのセットアップ

1.  **Install Raspberry Pi OS:** Flash Raspberry Pi OS (32-bit or 64-bit, Lite or Desktop) onto your SD card using Raspberry Pi Imager. Configure WiFi and SSH access during flashing for easier setup. | **Raspberry Pi OSのインストール:** Raspberry Pi Imagerを使用して、Raspberry Pi OS (32ビットまたは64ビット、LiteまたはDesktop)をSDカードに書き込みます。簡単なセットアップのために、書き込み中にWiFiとSSHアクセスを設定します。
2.  **Boot and Connect:** Insert the SD card, connect peripherals (if needed), power up the Pi, and connect via SSH or direct console. | **起動と接続:** SDカードを挿入し、周辺機器を接続（必要な場合）、Piの電源を入れ、SSHまたは直接コンソール経由で接続します。
3.  **System Update:** | **システムアップデート:**
    ```bash
    sudo apt update
    sudo apt full-upgrade -y
    sudo reboot # Reboot after major upgrade
    ```
4.  **Enable I2S Interface:** | **I2Sインターフェースの有効化:**
    *   Edit the boot config file. The path depends on your OS version (check both). | ブート設定ファイルを編集します。パスはOSのバージョンによって異なります（両方確認してください）。
        ```bash
        # Newer systems / 新しいシステム:
        sudo nano /boot/firmware/config.txt
        # Older systems / 古いシステム:
        # sudo nano /boot/config.txt
        ```
    *   Add these lines to the **end** of the file: | ファイルの**末尾**に以下の行を追加します:
        ```text
        # Enable I2S audio interface
        dtparam=i2s=on

        # Load the Google Voice HAT sound card overlay (for INMP441)
        dtoverlay=googlevoicehat-soundcard
        ```
    *   Save (Ctrl+X, then Y, then Enter) and reboot: | 保存 (Ctrl+X、次にY、次にEnter) して再起動します:
        ```bash
        sudo reboot
        ```
5.  **Install System Dependencies:** | **システム依存関係のインストール:**
    ```bash
    sudo apt install -y portaudio19-dev ffmpeg libopenblas-base python3-pip python3-venv git
    ```
6.  **Set up Python Virtual Environment (Recommended):** | **Python仮想環境のセットアップ (推奨):**
    ```bash
    mkdir ~/ninja-robot # Create a project directory
    cd ~/ninja-robot
    python3 -m venv .venv # Create virtual environment named .venv
    source .venv/bin/activate # Activate the environment (do this every time you open a new terminal for this project)
    # Your prompt should now start with (.venv)
    # Pip install commands below should be run while venv is active
    ```
7.  **Install Python Libraries:** | **Pythonライブラリのインストール:**
    ```bash
    pip install --upgrade pip # Upgrade pip first
    pip install Flask google-generativeai SpeechRecognition gTTS pygame sounddevice PyAudio RPi.GPIO DFRobot_RaspberryPi_Expansion_Board google-cloud-aiplatform numpy
    ```

---

## 4. Google Gemini API Setup | Google Gemini APIのセットアップ

1.  **Create API Key:** | **APIキーの作成:**
    *   Go to [Google AI Studio](https://aistudio.google.com/). | [Google AI Studio](https://aistudio.google.com/) にアクセスします。
    *   Sign in with your Google account. | Googleアカウントでサインインします。
    *   Click "Get API key" -> "Create API key in new project" (or select an existing project). | 「APIキーを取得」->「新しいプロジェクトでAPIキーを作成」（または既存のプロジェクトを選択）をクリックします。
    *   Copy the generated API key. **Keep it secret!** | 生成されたAPIキーをコピーします。**秘密に保管してください！**
2.  **Enable API (If using Vertex AI):** If you plan to use Vertex AI endpoints later, ensure the "Vertex AI API" is enabled in your Google Cloud Console project. For `google-generativeai`, this is usually not required initially. | **APIの有効化 (Vertex AIを使用する場合):** 将来的にVertex AIエンドポイントを使用する予定がある場合は、Google Cloud Consoleプロジェクトで「Vertex AI API」が有効になっていることを確認してください。`google-generativeai` の場合、通常は初期には不要です。

---

## 5. Code Setup | コードのセットアップ

1.  **Create Project Directory:** If you haven't already, create the project directory and activate the virtual environment: | **プロジェクトディレクトリの作成:** まだ作成していない場合は、プロジェクトディレクトリを作成し、仮想環境をアクティブにします:
    ```bash
    mkdir ~/ninja-robot
    cd ~/ninja-robot
    source .venv/bin/activate
    ```
2.  **Create Python Files:** Create the following Python files (`.py`) inside the `~/ninja-robot` directory. Copy and paste the **final, corrected code** for each file from our previous conversation. | **Pythonファイルの作成:** `~/ninja-robot` ディレクトリ内に以下のPythonファイル (`.py`) を作成します。以前の会話から、各ファイルの**最終的な修正済みコード**をコピー＆ペーストします。

    *   `Ninja_Buzzer.py` (Handles buzzer sounds) | (ブザー音を処理)
    *   `Ninja_Distance.py` (Handles ultrasonic sensor) | (超音波センサーを処理)
    *   `Ninja_Movements_v1.py` (Handles servo movements) | (サーボの動きを処理)
    *   `ninja_core.py` (Core logic, Gemini interaction, hardware coordination) | (コアロジック、Gemini対話、ハードウェア連携)
    *   `Ninja_Voice_Control.py` (Background process for "Robot Mic" mode) | (「ロボットマイク」モード用のバックグラウンドプロセス)
    *   `web_interface.py` (Flask web server) | (Flaskウェブサーバー)

3.  **Add Gemini API Key:** Open `ninja_core.py` and replace the placeholder with your actual key: | **Gemini APIキーの追加:** `ninja_core.py` を開き、プレースホルダーを実際のキーに置き換えます:
    ```python
    # Find this line near the top / 上部付近のこの行を見つけます
    GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY" # <----------- Replace with your key | あなたのキーに置き換えます
    ```
4.  **Create HTML Template:** | **HTMLテンプレートの作成:**
    *   Create a subdirectory named `templates`: | `templates` という名前のサブディレクトリを作成します:
        ```bash
        mkdir templates
        ```
    *   Inside `templates`, create a file named `index.html`. | `templates` 内に `index.html` という名前のファイルを作成します。
    *   Copy and paste the **final, corrected HTML/JS code** for `index.html` into this file. | このファイルに `index.html` 用の**最終的な修正済みHTML/JSコード**をコピー＆ペーストします。

5.  **File Structure:** Your `~/ninja-robot` directory should look like this: | **ファイル構造:** `~/ninja-robot` ディレクトリは次のようになります:
    ```
    ninja-robot/
    ├── .venv/              <-- Virtual environment folder | 仮想環境フォルダ
    ├── Ninja_Buzzer.py
    ├── Ninja_Distance.py
    ├── Ninja_Movements_v1.py
    ├── ninja_core.py
    ├── Ninja_Voice_Control.py
    ├── web_interface.py
    ├── conversation.log     <-- Will be created automatically | 自動的に作成されます
    ├── stop_voice.flag      <-- Will be created/deleted automatically | 自動的に作成/削除されます
    └── templates/
        └── index.html
    ```

---

## 6. Running the Robot | ロボットの実行

1.  **Activate Environment:** Open a terminal on the Pi, navigate to your project directory, and activate the virtual environment: | **環境のアクティブ化:** Piでターミナルを開き、プロジェクトディレクトリに移動し、仮想環境をアクティブにします:
    ```bash
    cd ~/ninja-robot
    source .venv/bin/activate
    ```
2.  **Find Pi's IP Address:** | **PiのIPアドレスの確認:**
    ```bash
    hostname -I
    ```
    Note the IP address (e.g., `192.168.1.123`). | IPアドレス（例: `192.168.1.123`）をメモします。
3.  **Run the Web Interface:** | **ウェブインターフェースの実行:**
    ```bash
    python3 web_interface.py
    ```
    The server will start, usually on port 5000. Keep this terminal open. | サーバーが起動します（通常はポート5000）。このターミナルは開いたままにしておきます。
4.  **Access the Web UI:** On another device (phone, computer) connected to the **same WiFi network**, open a web browser and go to: | **ウェブUIへのアクセス:** **同じWiFiネットワーク**に接続されている別のデバイス（スマートフォン、コンピューター）でウェブブラウザを開き、以下にアクセスします:
    `http://<YOUR_PI_IP_ADDRESS>:5000`
    (Replace `<YOUR_PI_IP_ADDRESS>` with the actual IP address). | (`<YOUR_PI_IP_ADDRESS>`を実際のIPアドレスに置き換えます)。
5.  **Using the Interface:** | **インターフェースの使用:**
    *   **Controller Mode:** This is the default. Use the D-Pad, Action buttons (△□○X), and Speed buttons to control the robot directly. The "Mode" display (Walk/Run) affects the D-Pad actions. | **コントローラーモード:** デフォルトです。十字キー、アクションボタン（△□○X）、速度ボタンを使用してロボットを直接制御します。「モード」表示（Walk/Run）は十字キーのアクションに影響します。
    *   **Browser Mic Mode:**
        *   Click the "Browser Mic" button to activate the mode. | モードをアクティブにするには「Browser Mic」ボタンをクリックします。
        *   Click it *again* to start listening (button text changes). Your browser may ask for microphone permission. | *もう一度*クリックして聞き取りを開始します（ボタンのテキストが変わります）。ブラウザがマイクの許可を求める場合があります。
        *   Speak your command (e.g., "go forward", "say hello") or question (e.g., "what time is it"). | コマンド（例: "go forward", "say hello"）または質問（例: "what time is it"）を話します。
        *   The transcribed text is sent to Gemini for interpretation/answering. Results appear in the "Status" area. | 書き起こされたテキストは解釈/回答のためにGeminiに送信されます。結果は「ステータス」エリアに表示されます。
    *   **Robot Mic Mode:**
        *   Click the "Speak to Robot" button. The web server starts the `Ninja_Voice_Control.py` script on the Pi in the background. The button text should change to "Robot Mic (ON)". | 「Speak to Robot」ボタンをクリックします。ウェブサーバーはPi上で`Ninja_Voice_Control.py`スクリプトをバックグラウンドで起動します。ボタンのテキストは「Robot Mic (ON)」に変わるはずです。
        *   The "Robot Mic Dialog" area will show the conversation log from the background script (Listening..., Heard..., Assistant Speaking...). | 「Robot Mic Dialog」エリアには、バックグラウンドスクリプトからの会話ログ（Listening...、Heard...、Assistant Speaking...）が表示されます。
        *   Speak directly to the robot's physical INMP441 microphone. Prefix commands with "ninja" (e.g., "ninja walk", "ninja stop"). Ask questions naturally. | ロボットの物理的なINMP441マイクに直接話しかけます。コマンドの前に "ninja" を付けます（例: "ninja walk", "ninja stop"）。質問は自然に尋ねます。
        *   To stop this mode, click either the "Controller" or "Browser Mic" button. This signals the background script to stop. | このモードを停止するには、「Controller」または「Browser Mic」ボタンをクリックします。これにより、バックグラウンドスクリプトに停止信号が送られます。
6.  **Stopping:** Press `Ctrl+C` in the terminal running `web_interface.py` to stop the web server and trigger the robot's cleanup sequence. | **停止:** `web_interface.py` を実行しているターミナルで `Ctrl+C` を押すと、ウェブサーバーが停止し、ロボットのクリーンアップシーケンスがトリガーされます。

---

## 7. Troubleshooting | トラブルシューティング

*   **ALSA/JACK Errors on Startup:** Messages like `ALSA lib ...` or `Cannot connect to server socket err` during startup are often harmless warnings from audio libraries probing devices. If audio *works*, you can usually ignore them or suppress `stderr` when running scripts (`python3 script.py 2>/dev/null`). | **起動時のALSA/JACKエラー:** 起動中に `ALSA lib ...` や `Cannot connect to server socket err` のようなメッセージが表示されることがありますが、これらはオーディオライブラリがデバイスを探している際の無害な警告であることが多いです。オーディオが*動作している*場合は、通常無視するか、スクリプト実行時に `stderr` を抑制できます (`python3 script.py 2>/dev/null`)。
*   **Microphone Not Working (Robot Mic Mode):**
    *   Verify I2S connections and `config.txt` settings. Reboot after changes. | I2S接続と `config.txt` 設定を確認します。変更後は再起動してください。
    *   Run `arecord -l` in the Pi terminal. You should see a card like `googlevoicehatsc`. | Piターミナルで `arecord -l` を実行します。`googlevoicehatsc` のようなカードが表示されるはずです。
    *   Check the terminal output of `web_interface.py` when starting "Robot Mic" mode for errors from `Ninja_Voice_Control.py`. | 「Robot Mic」モード起動時の `web_interface.py` のターミナル出力で `Ninja_Voice_Control.py` からのエラーを確認します。
    *   In `Ninja_Voice_Control.py`, adjust `recognizer.energy_threshold` if speech isn't detected well. | `Ninja_Voice_Control.py` で、音声がうまく検出されない場合は `recognizer.energy_threshold` を調整します。
*   **Microphone Not Working (Browser Mic Mode):**
    *   Ensure you granted microphone permission in your browser for the Pi's IP address. | ブラウザでPiのIPアドレスに対するマイクの許可を与えたことを確認します。
    *   Check the browser's developer console (F12) for Web Speech API errors. | ブラウザの開発者コンソール（F12）でWeb Speech APIのエラーを確認します。
    *   Try a different browser (Chrome/Edge often have the best support). | 別のブラウザ（Chrome/Edgeはサポートが充実していることが多い）を試します。
*   **Robot Doesn't Move / Moves Incorrectly:**
    *   Check servo power connections (usually via the HAT). | サーボの電源接続（通常はHAT経由）を確認します。
    *   Verify servo connections to the correct `Servo 0-3` ports on the HAT. | HAT上の正しい `Servo 0-3` ポートへのサーボ接続を確認します。
    *   Check the terminal output of `web_interface.py` for errors from `ninja_core.py` or `Ninja_Movements_v1.py`. | `web_interface.py` のターミナル出力で `ninja_core.py` や `Ninja_Movements_v1.py` からのエラーを確認します。
*   **Gemini Errors:**
    *   Ensure the correct API key is in `ninja_core.py`. | 正しいAPIキーが `ninja_core.py` に設定されていることを確認します。
    *   Check internet connectivity on the Pi. | Piのインターネット接続を確認します。
    *   Make sure you haven't exceeded API usage limits. | APIの使用制限を超えていないことを確認します。
    *   Try a different Gemini model name in `ninja_core.py` if one model seems unavailable. | あるモデルが利用できないようなら、`ninja_core.py` で別のGeminiモデル名を試します。

---

## 8. Conclusion & Next Steps | まとめと次のステップ

You now have a functional voice-controlled robot! From here, you can:
*   **Refine Movements:** Adjust servo angles in `Ninja_Movements_v1.py` for smoother gaits. | **動作の調整:** `Ninja_Movements_v1.py` のサーボ角度を調整して、より滑らかな歩行を実現します。
*   **Add More Sounds:** Define new sound sequences in `Ninja_Buzzer.py`. | **サウンドの追加:** `Ninja_Buzzer.py` で新しいサウンドシーケンスを定義します。
*   **Expand Commands:** Modify the Gemini prompt in `ninja_core.py` to recognize more complex commands or sequences. | **コマンドの拡張:** `ninja_core.py` のGeminiプロンプトを変更して、より複雑なコマンドやシーケンスを認識させます。
*   **Improve Web UI:** Enhance the web interface with more features or better styling. | **ウェブUIの改善:** ウェブインターフェースにさらに多くの機能を追加したり、スタイルを改善したりします。
*   **Add Sensors:** Integrate other sensors (e.g., camera, line followers) and corresponding logic. | **センサーの追加:** 他のセンサー（例: カメラ、ライントレーサー）と対応するロジックを統合します。

Enjoy your interactive Ninja Robot!
インタラクティブなNinja Robotをお楽しみください！

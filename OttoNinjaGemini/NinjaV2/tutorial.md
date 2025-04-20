# Building the Voice-Controlled Ninja Robot (Tutorial)

This tutorial guides you through building a voice-controlled, four-legged robot using a Raspberry Pi, DFRobot HAT, standard servos, sensors, and Google AI services.

**Project Goal:** Build a small robot controllable via a web interface using voice commands processed by Google Gemini and Google Speech Recognition. The robot performs movements, makes sounds, and stops for obstacles.

**Difficulty:** Intermediate

---

## Table of Contents (English)

1.  [Phase 1: Hardware Requirements & Assembly](#phase-1-hardware-requirements--assembly)
    *   [1.1 Components Needed](#11-components-needed)
    *   [1.2 Assembly Steps](#12-assembly-steps)
2.  [Phase 2: Software Setup](#phase-2-software-setup)
    *   [2.1 Flash Raspberry Pi OS](#21-flash-raspberry-pi-os)
    *   [2.2 Initial Boot and Configuration](#22-initial-boot-and-configuration)
    *   [2.3 System Updates & Install Dependencies](#23-system-updates--install-dependencies)
    *   [2.4 Set Up Python Virtual Environment](#24-set-up-python-virtual-environment-recommended)
    *   [2.5 Install Python Libraries](#25-install-python-libraries)
3.  [Phase 3: Code Setup](#phase-3-code-setup)
    *   [3.1 Get the Code Files](#31-get-the-code-files)
    *   [3.2 Configure API Key](#32-configure-api-key)
4.  [Phase 4: Running the Robot](#phase-4-running-the-robot)
5.  [Phase 5: Troubleshooting Common Issues](#phase-5-troubleshooting-common-issues)

---

## Phase 1: Hardware Requirements & Assembly

### 1.1 Components Needed

*   **Raspberry Pi:** Raspberry Pi Zero W or WH (recommended) or Raspberry Pi 3/4.
*   **Micro SD Card:** 8GB+ Class 10.
*   **Power Supply:**
    *   5V/2.5A+ Micro USB PSU for the Pi.
    *   **Separate 5V/3A+ DC PSU** for the DFRobot HAT/Servos (barrel jack or screw terminals). **Crucial!**
*   **DFRobot Raspberry Pi IO Expansion HAT:** Compatible model with I2C, PWM, GPIO.
*   **Servos:** 4 x Standard 9g or similar (e.g., MG90S), 5V compatible.
*   **Ultrasonic Sensor:** 1 x HC-SR04.
*   **Active Buzzer:** 1 x 5V Active Buzzer.
*   **Robot Chassis/Body:** 3D-printed or kit for a quadruped robot.
*   **Jumper Wires:** Female-to-Female.
*   **USB Microphone:** Compatible with Raspberry Pi.
*   **Computer:** For SD card setup and SSH/VNC.
*   **(Optional)** Pi Case, Small Breadboard.

### 1.2 Assembly Steps

1.  **Mount HAT:** Align HAT pins with Pi GPIO and press firmly.
2.  **Assemble Chassis:** Build the robot body and mount the 4 servos.
3.  **Connect Servos to HAT:**
    *   Identify PWM headers (PWM0-PWM3) on the HAT.
    *   Plug servos in, matching Signal, VCC (5V), and GND pins:
        *   Servo 0 -> PWM0
        *   Servo 1 -> PWM1
        *   Servo 2 -> PWM2
        *   Servo 3 -> PWM3
    *   > **Note:** Adjust servo IDs in `ninja_movements_v1.py` or `ninja_core.py` if your numbering differs.
4.  **Connect Ultrasonic Sensor (HC-SR04) to HAT:**
    *   Use jumper wires:
        *   Sensor `VCC` -> HAT `5V` Pin
        *   Sensor `Trig` -> HAT `GPIO 21` (BCM)
        *   Sensor `Echo` -> HAT `GPIO 22` (BCM)
        *   Sensor `GND` -> HAT `GND` Pin
5.  **Connect Buzzer to HAT:**
    *   Use jumper wires:
        *   Buzzer `+` (or Signal) -> HAT `GPIO 23` (BCM)
        *   Buzzer `-` (or GND) -> HAT `GND` Pin
6.  **Connect Power:**
    *   Plug the **separate 5V servo PSU** into the **DFRobot HAT's** power input.
    *   Plug the **Pi's Micro USB PSU** into the **Raspberry Pi** itself.
7.  **Connect Microphone:** Plug the USB microphone into a Pi USB port.

---

## Phase 2: Software Setup

### 2.1 Flash Raspberry Pi OS

1.  Download "Raspberry Pi OS Lite" (64-bit or 32-bit) from [raspberrypi.com/software](https://www.raspberrypi.com/software/).
2.  Use Raspberry Pi Imager to flash the OS onto the SD card.
3.  **Before Ejecting:** Use Imager settings (Ctrl+Shift+X or Gear Icon) to:
    *   **Enable SSH**
    *   **Set Hostname** (e.g., `ninja-robot`)
    *   **Set Username and Password** (e.g., user `robot`, **remember the password!**)
    *   **Configure Wireless LAN** (Your Wi-Fi SSID and Password)

### 2.2 Initial Boot and Configuration

1.  Insert SD card into Pi, connect Pi power (servo power not needed yet).
2.  Wait for boot and Wi-Fi connection (a few minutes).
3.  Find the Pi's IP address (e.g., SSH using hostname `ssh robot@ninja-robot.local`, check router, use network scanner).
4.  Connect via SSH: `ssh <username>@<IP_ADDRESS>` (e.g., `ssh robot@192.168.1.105`). Enter password.
5.  Run configuration tool:
    ```bash
    sudo raspi-config
    ```
6.  Navigate to `Interface Options`.
7.  Enable `I2C`. Select `<Yes>`.
8.  *(Optional)* Enable `Serial Port`. Answer `<No>` to login shell, `<Yes>` to enable hardware.
9.  Finish and exit `raspi-config`. Reboot if prompted: `sudo reboot`.

### 2.3 System Updates & Install Dependencies

1.  Reconnect via SSH after reboot.
2.  Update system:
    ```bash
    sudo apt update
    sudo apt upgrade -y
    ```
3.  Install necessary build tools and libraries:
    ```bash
    sudo apt install -y python3-dev python3-pip python3-venv build-essential libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg flac libatlas-base-dev
    ```

### 2.4 Set Up Python Virtual Environment (Recommended)

1.  Navigate to project location: `cd ~`
2.  Create directory: `mkdir ninja_robot`
3.  Enter directory: `cd ninja_robot`
4.  Create venv: `python3 -m venv venv`
5.  Activate venv: `source venv/bin/activate`
    > Your prompt should now start with `(venv)`.

### 2.5 Install Python Libraries

1.  Ensure venv is active.
2.  Install required packages:
    ```bash
    pip install RPi.GPIO DFRobot_RaspberryPi_Expansion_Board google-generativeai SpeechRecognition gTTS pygame Flask google-cloud-speech
    ```
    > **Note:** If `SpeechRecognition` fails related to PyAudio, try `pip install pyaudio` after installing the `apt` packages above.

---

## Phase 3: Code Setup

### 3.1 Get the Code Files

1.  Ensure you are in your project directory (`~/ninja_robot`) and the venv is active.
2.  You need the following files/directories in `~/ninja_robot`:
    *   `ninja_core.py` (V1.4+)
    *   `ninja_voice_control.py`
    *   `web_interface.py` (Display version)
    *   `Ninja_Movements_v1.py`
    *   `Ninja_Buzzer.py`
    *   `Ninja_Distance.py`
    *   `DFRobot_RaspberryPi_Expansion_Board.py` (DFRobot library)
    *   `templates/` (directory)
        *   `templates/index_voice_display.html`
3.  **Transfer methods:** Use `git clone`, `scp` / WinSCP, or manually create files using `nano` and copy-pasting code.

### 3.2 Configure API Key

1.  Edit the core logic file:
    ```bash
    nano ninja_core.py
    ```
2.  Find the line: `GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"`
3.  Replace `"YOUR_GOOGLE_API_KEY"` with your actual Google AI Studio API key.
4.  Save (`Ctrl+X`, `Y`, `Enter`).

---

## Phase 4: Running the Robot

1.  **Activate Venv:** If needed: `cd ~/ninja_robot` then `source venv/bin/activate`.
2.  **Connect Servo Power:** Turn on the separate 5V power supply for the HAT.
3.  **Run Voice Control Script:** In **Terminal 1**:
    ```bash
    python ninja_voice_control.py
    ```
    Watch for "Ninja robot ready." and "Listening..." messages.
4.  **Run Web Interface Script:** In **Terminal 2**:
    ```bash
    cd ~/ninja_robot
    source venv/bin/activate
    python web_interface.py
    ```
    Note the IP address printed (e.g., `http://192.168.1.105:5000`).
5.  **Access Web UI:**
    *   On another device on the *same Wi-Fi network*, open a browser.
    *   Go to the URL from the previous step.
6.  **Interact:**
    *   Speak near the USB microphone.
    *   Start commands with "Ninja" (e.g., "Ninja, walk forward", "Ninja, say hello").
    *   Observe Terminal 1 output (transcript, interpretation).
    *   Observe the web UI conversation log (refreshes automatically).
7.  **Stop:**
    *   Click the "Stop Voice Control" button on the web UI.
    *   Go to Terminal 1 (`ninja_voice_control.py`) and press `Ctrl+C` if it didn't exit automatically.
    *   Go to Terminal 2 (`web_interface.py`) and press `Ctrl+C`.

---

## Phase 5: Troubleshooting Common Issues

*   **ImportError:** Activate the virtual environment (`source venv/bin/activate`) before running `python`. Ensure libraries were installed within the active venv.
*   **Audio Errors:** Check mic connection. Verify `pygame` and audio `apt` dependencies. Reboot. Check `aplay -l` / `arecord -l`. Adjust `recognizer.energy_threshold` in `ninja_voice_control.py`. Check internet for `recognize_google`.
*   **No Movement/Jitter:** Verify separate servo power supply (sufficient amps!). Check servo connections to PWM pins. Ensure I2C is enabled (`sudo raspi-config`).
*   **Web UI Issues:** Check Pi's IP. Ensure devices are on the same network. Verify `web_interface.py` is running. Check for port conflicts.
*   **GPIO Permission Denied:** Ensure the user running the scripts (`pi`, `robot`, etc.) is in the `gpio` group (`sudo adduser <username> gpio` then reboot).

---
---

# 音声制御忍者ロボットの構築（チュートリアル） - 日本語版

このチュートリアルでは、Raspberry Pi、DFRobot HAT、標準サーボ、センサー、Google AIサービスを使用して、音声で制御される四足歩行ロボットを構築する手順を説明します。

**プロジェクト目標：** Google GeminiとGoogle Speech Recognition（ブラウザ経由）によって処理される音声コマンドを使用して、Webインターフェースで制御可能な小型ロボットを構築します。ロボットは様々な動きを行い、音を出し、障害物を検知すると停止します。

**難易度：** 中級

---

## 目次 (日本語版)

1.  [フェーズ1：ハードウェア要件と組み立て](#フェーズ1ハードウェア要件と組み立て)
    *   [1.1 必要な部品](#11-必要な部品)
    *   [1.2 組み立て手順](#12-組み立て手順)
2.  [フェーズ2：ソフトウェア設定](#フェーズ2ソフトウェア設定)
    *   [2.1 Raspberry Pi OSの書き込み](#21-raspberry-pi-osの書き込み)
    *   [2.2 初回起動と設定](#22-初回起動と設定)
    *   [2.3 システムの更新と依存関係のインストール](#23-システムの更新と依存関係のインストール)
    *   [2.4 Python仮想環境のセットアップ（推奨）](#24-python仮想環境のセットアップ推奨)
    *   [2.5 Pythonライブラリのインストール](#25-pythonライブラリのインストール)
3.  [フェーズ3：コードのセットアップ](#フェーズ3コードのセットアップ)
    *   [3.1 コードファイルの取得](#31-コードファイルの取得)
    *   [3.2 APIキーの設定](#32-apiキーの設定)
4.  [フェーズ4：ロボットの実行](#フェーズ4ロボットの実行)
5.  [フェーズ5：一般的な問題のトラブルシューティング](#フェーズ5一般的な問題のトラブルシューティング)

---

## フェーズ1：ハードウェア要件と組み立て

### 1.1 必要な部品

*   **Raspberry Pi:** Raspberry Pi Zero W または WH（推奨）または Raspberry Pi 3/4。
*   **Micro SDカード:** 8GB以上、Class 10推奨。
*   **電源：**
    *   Pi用の5V/2.5A以上のMicro USB電源。
    *   **別個の5V/3A+ DC電源：** DFRobot HAT/サーボ用（バレルジャックまたはネジ端子）。**非常に重要！**
*   **DFRobot Raspberry Pi IO拡張HAT:** I2C、PWM、GPIOを備えた互換モデル。
*   **サーボ:** 4 x 標準9gまたは同等品（例: MG90S）、5V対応。
*   **超音波センサー:** 1 x HC-SR04。
*   **アクティブブザー:** 1 x 5Vアクティブブザー。
*   **ロボットシャーシ/ボディ:** 四足歩行ロボット用の3Dプリントまたはキット。
*   **ジャンパーワイヤー:** メス-メス。
*   **USBマイク:** Raspberry Pi互換。
*   **コンピュータ:** SDカード設定およびSSH/VNCアクセス用。
*   **(任意)** Piケース、小型ブレッドボード。

### 1.2 組み立て手順

1.  **HATの取り付け:** HATのピンをPiのGPIOに合わせ、しっかりと押し込みます。
2.  **シャーシの組み立て:** ロボット本体を組み立て、4つのサーボを取り付けます。
3.  **サーボとHATの接続:**
    *   HATのPWMヘッダー（PWM0-PWM3）を確認します。
    *   信号、VCC(5V)、GNDピンを合わせてサーボを接続します：
        *   サーボ 0 -> PWM0
        *   サーボ 1 -> PWM1
        *   サーボ 2 -> PWM2
        *   サーボ 3 -> PWM3
    *   > **注意:** 番号付けが異なる場合は `ninja_movements_v1.py` や `ninja_core.py` のサーボIDを調整してください。
4.  **超音波センサー (HC-SR04) とHATの接続:**
    *   ジャンパーワイヤーを使用：
        *   センサー `VCC` -> HAT `5V` ピン
        *   センサー `Trig` -> HAT `GPIO 21` (BCM)
        *   センサー `Echo` -> HAT `GPIO 22` (BCM)
        *   センサー `GND` -> HAT `GND` ピン
5.  **ブザーとHATの接続:**
    *   ジャンパーワイヤーを使用：
        *   ブザー `+` (または信号) -> HAT `GPIO 23` (BCM)
        *   ブザー `-` (またはGND) -> HAT `GND` ピン
6.  **電源の接続:**
    *   **別個の5Vサーボ電源**を**DFRobot HAT**の電源入力に接続します。
    *   **PiのMicro USB電源**を**Raspberry Pi本体**に接続します。
7.  **マイクの接続:** USBマイクをPiのUSBポートに接続します。

---

## フェーズ2：ソフトウェア設定

### 2.1 Raspberry Pi OSの書き込み

1.  [raspberrypi.com/software](https://www.raspberrypi.com/software/) から「Raspberry Pi OS Lite」をダウンロードします。
2.  Raspberry Pi Imagerを使用してOSをSDカードに書き込みます。
3.  **取り出す前に：** Imagerの設定（Ctrl+Shift+X または 歯車アイコン）で以下を設定します：
    *   **SSHを有効にする**
    *   **ホスト名を設定する** (例: `ninja-robot`)
    *   **ユーザー名とパスワードを設定する** (例: ユーザー `robot`, **パスワードを忘れないでください！**)
    *   **ワイヤレスLANを設定する** (Wi-FiのSSIDとパスワード)

### 2.2 初回起動と設定

1.  SDカードをPiに挿入し、Piの電源を接続します（サーボ電源はまだ不要）。
2.  起動とWi-Fi接続を待ちます（数分）。
3.  PiのIPアドレスを見つけます（例: `ssh robot@ninja-robot.local` でSSH、ルーターを確認、ネットワークスキャナーを使用）。
4.  SSHで接続します：`ssh <username>@<IP_ADDRESS>`。パスワードを入力します。
5.  設定ツールを実行します：
    ```bash
    sudo raspi-config
    ```
6.  `Interface Options` に移動します。
7.  `I2C` を有効にします。`<Yes>`を選択します。
8.  *(任意)* `Serial Port` を有効にします。ログインシェルには`<No>`、ハードウェア有効化には`<Yes>`を選択します。
9.  `raspi-config`を終了し、促されたら再起動します：`sudo reboot`。

### 2.3 システムの更新と依存関係のインストール

1.  再起動後にSSHで再接続します。
2.  システムを更新します：
    ```bash
    sudo apt update
    sudo apt upgrade -y
    ```
3.  必要なビルドツールとライブラリをインストールします：
    ```bash
    sudo apt install -y python3-dev python3-pip python3-venv build-essential libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg flac libatlas-base-dev
    ```

### 2.4 Python仮想環境のセットアップ（推奨）

1.  プロジェクトの場所に移動します：`cd ~`
2.  ディレクトリを作成します：`mkdir ninja_robot`
3.  ディレクトリに入ります：`cd ninja_robot`
4.  venvを作成します：`python3 -m venv venv`
5.  venvを有効化します：`source venv/bin/activate`
    > プロンプトの先頭に `(venv)` が表示されます。

### 2.5 Pythonライブラリのインストール

1.  venvが有効であることを確認します。
2.  必要なパッケージをインストールします：
    ```bash
    pip install RPi.GPIO DFRobot_RaspberryPi_Expansion_Board google-generativeai SpeechRecognition gTTS pygame Flask google-cloud-speech
    ```
    > **注意:** `SpeechRecognition`がPyAudio関連で失敗する場合、上記の`apt`パッケージをインストール後に`pip install pyaudio`を試してください。

---

## フェーズ3：コードのセットアップ

### 3.1 コードファイルの取得

1.  プロジェクトディレクトリ（`~/ninja_robot`）にいて、venvが有効であることを確認します。
2.  `~/ninja_robot` に以下のファイル/ディレクトリが必要です：
    *   `ninja_core.py` (V1.4+)
    *   `ninja_voice_control.py`
    *   `web_interface.py` (表示バージョン)
    *   `Ninja_Movements_v1.py`
    *   `Ninja_Buzzer.py`
    *   `Ninja_Distance.py`
    *   `DFRobot_RaspberryPi_Expansion_Board.py` (DFRobotライブラリ)
    *   `templates/` (ディレクトリ)
        *   `templates/index_voice_display.html`
3.  **転送方法：** `git clone`、`scp` / WinSCP、または `nano` を使って手動でファイルを作成しコードをコピー＆ペーストします。

### 3.2 APIキーの設定

1.  コアロジックファイルを編集します：
    ```bash
    nano ninja_core.py
    ```
2.  `GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"` という行を見つけます。
3.  `"YOUR_GOOGLE_API_KEY"` を実際のGoogle AI Studio APIキーに置き換えます。
4.  保存します（`Ctrl+X`, `Y`, `Enter`）。

---

## フェーズ4：ロボットの実行

1.  **Venvの有効化:** 必要なら：`cd ~/ninja_robot` して `source venv/bin/activate`。
2.  **サーボ電源の接続:** HAT用の別個の5V電源をオンにします。
3.  **音声制御スクリプトの実行:** **ターミナル1**で：
    ```bash
    python ninja_voice_control.py
    ```
    「Ninja robot ready.」と「Listening...」のメッセージを確認します。
4.  **Webインターフェーススクリプトの実行:** **ターミナル2**で：
    ```bash
    cd ~/ninja_robot
    source venv/bin/activate
    python web_interface.py
    ```
    表示されるIPアドレスをメモします (例: `http://192.168.1.105:5000`)。
5.  **Web UIへのアクセス:**
    *   *同じWi-Fiネットワーク上*の別のデバイスでブラウザを開きます。
    *   前のステップのURLにアクセスします。
6.  **対話：**
    *   Piに接続されたUSBマイクの近くではっきりと話します。
    *   ウェイクワード「Ninja」でコマンドを開始します（例：「Ninja, 前に進んで」、「Ninja, こんにちは」）。
    *   ターミナル1の出力（トランスクリプト、解釈）を確認します。
    *   Web UIの会話ログを確認します（自動更新）。
7.  **停止：**
    *   Web UIの「Stop Voice Control」ボタンをクリックします。
    *   ターミナル1（`ninja_voice_control.py`）が自動で終了しない場合は `Ctrl+C` を押します。
    *   ターミナル2（`web_interface.py`）で `Ctrl+C` を押します。

---

## フェーズ5：一般的な問題のトラブルシューティング

*   **ImportError:** `python`実行前に仮想環境を有効化しましたか？ (`source venv/bin/activate`)。venv有効時に`pip`でライブラリをインストールしましたか？
*   **オーディオエラー:** マイク接続を確認。`pygame`と`apt`の依存関係を確認。再起動。`aplay -l` / `arecord -l`でデバイスを確認。`ninja_voice_control.py`の`recognizer.energy_threshold`を調整。インターネット接続を確認（`recognize_google`）。
*   **動作しない/ジッター:** 別個のサーボ電源（十分なアンペア数）を確認。HATのPWMピンへのサーボ接続を確認。I2Cが有効か確認（`sudo raspi-config`）。
*   **Web UIの問題:** PiのIPアドレスを確認。デバイスが同じネットワーク上にあるか確認。`web_interface.py`が実行中か確認。ポート競合がないか確認。
*   **GPIO Permission Denied:** スクリプトを実行するユーザーが`gpio`グループに属しているか確認（`sudo adduser <username> gpio` 後、再起動）。

---

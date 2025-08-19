### piservo0 user guildbook
guildhub link: https://github.com/ytani01/piservo0.git

-----

## Part 1: Japanese Version (日本語版)

# PiServo0 プロフェッショナル・ユーザーガイドブック

このガイドブックは、プログラミング経験がない方でも一般的な落とし穴を避けられるよう、プロのヒントを交えながら、Raspberry Pi（ラズベリーパイ）でサーボモーターを制御する方法をステップ・バイ・ステップで解説します。

-----

## 1\. PiServo0とは？

`PiServo0`は、簡単なコマンドを使ってRaspberry Piに接続されたサーボモーターを制御するためのソフトウェアツールキットです。

このツールキットを使えば、いくつかの方法でサーボモーターをコントロールできます：

  - **キャリブレーションツール**: キーボードを使ってモーターの動きを対話的に調整できます。
  - **コマンドライン**: ターミナルに短いコマンドを打ち込むだけで、モーターを特定の位置に動かせます。
  - **Pythonスクリプト**: ライブラリを自分のPythonスクリプトにインポートして、完全に制御できます。
  - **ウェブブラウザ**: ネットワーク経由で、コンピューターやスマートフォンのブラウザから遠隔操作が可能です。

エレクトロニクスやロボット工学の世界への、楽しくて簡単な第一歩となるように設計されています。

-----

## 2\. 準備とセットアップ

モーターを動かす前に、必要なハードウェアとソフトウェアを準備しましょう。

### ステップA: 事前準備

始める前に、お使いのRaspberry Piに必要なツールがインストールされているか確認してください。ターミナルを開いて、以下のコマンドを実行します：

```bash
sudo apt-get update && sudo apt-get install -y git
```

このプロジェクトでは、Python環境の管理に `uv` を使用します。以下のコマンドでインストールしてください：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

### ステップB: 必要なハードウェア

1.  **Raspberry Pi**: GPIOピンがあるモデルならどれでもOK（例：Model 3B+, 4, 5）。
2.  **SDカード**: 16GB以上を推奨します。
3.  **高品質な電源アダプター**: これが非常に重要です。**3アンペア以上**の定格出力を持つ電源を使用してください。
4.  **サーボモーター**: SG90のような小型サーボは初心者におすすめです。
5.  **ジャンパーワイヤー**: サーボモーターを接続するために使います。

\<br\>

> **⚠️ 重要：電源がすべて**
> 弱かったり低品質な電源は、問題が発生する最も一般的な原因です。もしRaspberry Piが突然再起動したり、サーボモーターが不規則にピクピク動くようなら、それはほぼ間違いなく電源の問題です。専用の高アンペアな電源を使うことで、何時間も無駄なイライラから解放されるでしょう。

\<br\>

#### サーボモーターの接続方法

サーボモーターには3本のワイヤーがあります。これらをRaspberry PiのGPIOピンに接続します。

  - **茶色または黒色のワイヤー (GND)**: **Ground (GND)** ピンに接続します。
  - **赤色のワイヤー (VCC)**: **5V** ピンに接続します。
  - **オレンジ色または黄色のワイヤー (Signal)**: **GPIOピン**（例：GPIO 12）に接続します。

> **ピン番号についての注意**: このライブラリは、物理的なボードのピン番号ではなく、**BCM番号方式**（「GPIOxx」とラベル付けされている番号）を使用します。`GPIO 12` はBCMのピンを指し、物理的なピン番号では32番ピンにあたります。

### ステップC: Raspberry Pi OSとpigpioのセットアップ

1.  **OS**: 最新のRaspberry Pi OSがインストールされていることを確認してください。
2.  **`pigpio`デーモンの起動**: このサービスはGPIOピンを制御するために必要です。以下のコマンドを実行して起動します：
    ```bash
    sudo systemctl start pigpiod
    ```
3.  **起動時に`pigpio`を有効化**: 再起動するたびにサービスが自動で開始されるように、以下のコマンドを実行します：
    ```bash
    sudo systemctl enable pigpiod
    ```

### ステップD: PiServo0ソフトウェアのインストール

1.  **ソフトウェアのダウンロード**:
    ```bash
    git clone https://github.com/ytani01/piservo0.git
    ```
2.  **ディレクトリの移動**:
    ```bash
    cd piservo0
    ```
3.  **ソフトウェアのインストール**: これで仮想環境が作成され、プロジェクトがインストールされます。
    ```bash
    uv venv
    uv pip install -e .
    ```

-----

## 3\. PiServo0の使い方

簡単なものから高度なものまで、サーボを制御するいくつかの方法を紹介します。

### 方法1: キャリブレーションツール（最初に試すのがおすすめ）

「キャリブレーション」とは、お使いのサーボ固有の動作範囲をソフトウェアに教えることです。

1.  **起動**: `<PIN>` をお使いのBCM GPIOピン番号に置き換えてください。
    ```bash
    piservo0 calib <PIN>
    ```
2.  **操作方法**: `w`/`s`キーで移動、`Tab`キーで目標（-90, 0, 90度）を選択、`Enter`キーで保存します。

### 方法2: Pythonサンプルスクリプトの実行

`samples`ディレクトリには、サンプルのスクリプトが含まれています。これは、ライブラリがコード内でどのように機能するかを確認する最良の方法です。

1.  **samplesディレクトリに移動**して、利用可能なスクリプトを確認します：
    ```bash
    ls samples/
    ```
2.  **サンプルを実行**: `uv run` を使って、プロジェクトの環境内でスクリプトを実行します。この例では、GPIO 12のサーボを動かします。
    ```bash
    uv run python samples/sample_01_piservo.py --pin 12
    ```

### 方法3: コマンドラインからの直接制御

手早くテストしたい場合は、サーボに直接コマンドを送ることができます。

  - **書式**: `piservo0 servo <PIN> <PULSE>`
  - **パルス (Pulse)**: 500（最小）から2500（最大）までの数値。1500が中央です。
  - **例**: `piservo0 servo 12 1500`

### 方法4: ウェブインターフェースによる遠隔操作

これにより、ネットワーク上のどのデバイスからでも制御が可能になります。

1.  **サーバーを起動**: 制御したいすべてのGPIOピンをリストアップします。
    ```bash
    piservo0 api-server 12 13
    ```
2.  **PiのIPアドレスを見つける**: 新しいターミナルで `hostname -I` を実行します。
3.  **別のPCから制御**: `str-client`とIPアドレスを使用します。
    ```bash
    piservo0 str-client --url http://<IP_ADDRESS>:8000/cmd
    ```
    プロンプトが表示されたら、`mv:90,-45` のようにコマンドを入力して、最初のサーボを90度、2番目のサーボを-45度に動かすことができます。

-----

## 4\. 高度な使い方とスクリプティング

### 4.1 動きのスクリプティング

テキストファイルにコマンドを記述することで、一連の動きを自動化できます。

1.  **`wave_script.txt`を作成**し、各行にコマンドを記述します：
    ```
    mv:0,.
    sl:0.5
    mv:90,.
    sl:0.5
    mv:0,.
    ```
2.  **スクリプトを実行**: このコマンドは、ファイルから各行を読み込み、`str-client`にパイプで渡します。
    ```bash
    cat wave_script.txt | xargs -L1 piservo0 str-client --url http://localhost:8000/cmd
    ```

### 4.2 JSONによるプログラム制御

速度などのパラメータを完全に制御するには、JSON形式のコマンドを送信します。

  - **コマンド**: JSONを `'''` で囲んでいる点に注意してください。これは、複雑な文字列をシェルで正しく渡すために必要です。
    ```bash
    piservo0 api-client --url http://localhost:8000/cmd '''{"cmd": "move_all_angles_sync", "angles": [45, -45], "move_sec": 2.0, "step_n": 100}'''
    ```

-----

## 5\. ユースケースのコンセプト：AIエージェントと関数呼び出し

これは、AIが `piservo0` をツールとしてどのように利用できるかを示す例です。

**ユーザーのプロンプト**: 「ねぇAI、ロボットアームにゆっくり手を振らせてくれる？」

**AIが生成したAPI呼び出し**: AIはリクエストをJSON配列に変換し、APIサーバーに送信します。このシーケンスは、最初のサーボを1.5秒かけて90度に動かし、少し待ってから元の位置に戻します。

```json
[
  {
    "cmd": "move_all_angles_sync",
    "target_angles": [90, null],
    "move_sec": 1.5,
    "step_n": 50
  },
  {
    "cmd": "sleep",
    "sec": 0.5
  },
  {
    "cmd": "move_all_angles_sync",
    "target_angles": [0, null],
    "move_sec": 1.5,
    "step_n": 50
  }
]
```

-----

## 6\. トラブルシューティング

  - **エラー: `pigpio daemon not connected`**: `pigpiod`サービスを起動し忘れています。`sudo systemctl start pigpiod`を実行してください。
  - **サーボがジッターを起こす、ピクピク動く、またはPiが再起動する**: 電源の供給電流が不足しています。ステップ2Bの警告を参照してください。
  - **コマンド `piservo0` が見つからない**: プロジェクトの仮想環境に入っていない可能性が高いです。`piservo0`ディレクトリにいることを確認し、`uv run <command>` のようにコマンドを実行してみてください。

-----

## Part 2: English Version

# PiServo0 Professional User Guidebook

This guide provides step-by-step instructions on how to control a servo motor with a Raspberry Pi, designed for users with no prior programming experience but with professional tips to avoid common pitfalls.

-----

## 1\. What is PiServo0?

`PiServo0` is a software toolkit for controlling servo motors connected to a Raspberry Pi using simple commands.

With this toolkit, you can control servo motors in several ways:

  - **Calibration Tool**: Use an interactive interface to adjust your motor's movement with your keyboard.
  - **Command Line**: Move the motor to specific positions by typing short commands into the terminal.
  - **Python Scripts**: Import the library into your own Python scripts for full control.
  - **Web Browser**: Control the servos remotely from a computer or smartphone browser over the network.

It's designed to be a fun and easy first step into the world of electronics and robotics.

-----

## 2\. Preparation and Setup

Before we can move the motor, let's prepare the necessary hardware and software.

### Step A: Prerequisites

Before you begin, ensure your Raspberry Pi has the necessary tools. Open a terminal and run:

```bash
sudo apt-get update && sudo apt-get install -y git
```

This project uses `uv` for managing the Python environment. Install it with:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

### Step B: Required Hardware

1.  **Raspberry Pi**: Any model with GPIO pins (e.g., Model 3B+, 4, 5).
2.  **SD Card**: 16GB or more is recommended.
3.  **High-Quality Power Adapter**: This is critical. Use a power supply rated for **3 Amps or more**.
4.  **Servo Motor**: A small servo like the SG90 is great for beginners.
5.  **Jumper Wires**: To connect the servo motor.

\<br\>

> **⚠️ Important: Power is Everything**
> A weak or low-quality power supply is the most common cause of problems. If your Raspberry Pi suddenly reboots or your servo motor twitches erratically, it's almost certainly a power issue. Using a dedicated, high-amperage power supply will save you hours of frustration.

\<br\>

#### How to Connect the Servo Motor

A servo motor has three wires. Connect them to the Raspberry Pi's GPIO pins.

  - **Brown or Black wire (GND)**: Connect to a **Ground (GND)** pin.
  - **Red wire (VCC)**: Connect to a **5V** pin.
  - **Orange or Yellow wire (Signal)**: Connect to a **GPIO pin** (e.g., GPIO 12).

> **Note on Pin Numbering**: This library uses the **BCM numbering scheme** (the numbers labeled "GPIOxx"), not the physical board pin numbers. `GPIO 12` refers to the BCM pin, which is physical pin 32.

### Step C: Raspberry Pi OS and pigpio Setup

1.  **OS**: Ensure you have the latest Raspberry Pi OS installed.
2.  **Start `pigpio` Daemon**: This service is required to control the GPIO pins. Start it by running:
    ```bash
    sudo systemctl start pigpiod
    ```
3.  **Enable `pigpio` on Boot**: To ensure the service starts automatically every time you reboot, run:
    ```bash
    sudo systemctl enable pigpiod
    ```

### Step D: PiServo0 Software Installation

1.  **Download the Software**:
    ```bash
    git clone https://github.com/ytani01/piservo0.git
    ```
2.  **Change Directory**:
    ```bash
    cd piservo0
    ```
3.  **Install the Software**: This creates a virtual environment and installs the project.
    ```bash
    uv venv
    uv pip install -e .
    ```

-----

## 3\. How to Use PiServo0

Here are several ways to control your servo, from simple to advanced.

### Method 1: The Calibration Tool (Recommended First Step)

"Calibration" teaches the software the unique movement range of your servo.

1.  **Launch**: Replace `<PIN>` with your BCM GPIO pin number.
    ```bash
    piservo0 calib <PIN>
    ```
2.  **Controls**: Use `w`/`s` to move, `Tab` to select a target (-90, 0, 90 deg), and `Enter` to save.

### Method 2: Running a Python Sample Script

The `samples` directory contains example scripts. This is the best way to see how the library works in code.

1.  **Navigate to the samples directory** to see what's available:
    ```bash
    ls samples/
    ```
2.  **Run a sample**: Use `uv run` to execute a script within the project's environment. This example moves the servo on GPIO 12.
    ```bash
    uv run python samples/sample_01_piservo.py --pin 12
    ```

### Method 3: Direct Control from the Command Line

For a quick test, you can command a servo directly.

  - **Format**: `piservo0 servo <PIN> <PULSE>`
  - **Pulse**: A number from 500 (min) to 2500 (max). 1500 is the center.
  - **Example**: `piservo0 servo 12 1500`

### Method 4: Remote Control via Web Interface

This allows control from any device on your network.

1.  **Start the Server**: List all GPIO pins you want to control.
    ```bash
    piservo0 api-server 12 13
    ```
2.  **Find Pi's IP Address**: In a new terminal, run `hostname -I`.
3.  **Control from another PC**: Use the `str-client` and the IP address.
    ```bash
    piservo0 str-client --url http://<IP_ADDRESS>:8000/cmd
    ```
    At the prompt, you can type commands like `mv:90,-45` to move the first servo to 90 degrees and the second to -45.

-----

## 4\. Advanced Usage and Scripting

### 4.1 Scripting Movements

You can automate sequences by scripting commands in a text file.

1.  **Create `wave_script.txt`** with commands, each on a new line:
    ```
    mv:0,.
    sl:0.5
    mv:90,.
    sl:0.5
    mv:0,.
    ```
2.  **Execute the script**: This command reads each line from the file and pipes it to the `str-client`.
    ```bash
    cat wave_script.txt | xargs -L1 piservo0 str-client --url http://localhost:8000/cmd
    ```

### 4.2 Programmatic JSON Control

For full control over parameters like speed, send a JSON command.

  - **The Command**: Note the `'''` around the JSON. This is necessary to pass the complex string correctly in the shell.
    ```bash
    piservo0 api-client --url http://localhost:8000/cmd '''{"cmd": "move_all_angles_sync", "angles": [45, -45], "move_sec": 2.0, "step_n": 100}'''
    ```

-----

## 5\. Conceptual Use Case: AI Agent with Function Calling

This shows how an AI could use `piservo0` as a tool.

**User Prompt**: "Hey AI, can you make the robot arm wave slowly?"

**AI's Generated API Call**: The AI translates the request into a JSON array and sends it to the API server. This sequence moves the first servo to 90 degrees over 1.5 seconds, pauses, and moves it back.

```json
[
  {
    "cmd": "move_all_angles_sync",
    "target_angles": [90, null],
    "move_sec": 1.5,
    "step_n": 50
  },
  {
    "cmd": "sleep",
    "sec": 0.5
  },
  {
    "cmd": "move_all_angles_sync",
    "target_angles": [0, null],
    "move_sec": 1.5,
    "step_n": 50
  }
]
```

-----

## 6\. Troubleshooting

  - **Error: `pigpio daemon not connected`**: You forgot to start the `pigpiod` service. Run `sudo systemctl start pigpiod`.
  - **Servo is jittery, twitching, or the Pi reboots**: Your power supply is not providing enough current. See the warning in Step 2B.
  - **Command `piservo0` not found**: You are likely not in the project's virtual environment. Make sure you are in the `piservo0` directory and try running commands with `uv run <command>`.
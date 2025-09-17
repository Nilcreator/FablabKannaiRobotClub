# NinjaRobotV3 User Guide

This guide provides a comprehensive overview of the `pi0disp`, `piservo0`, `vl53l0x_pigpio`, and `pi0buzzer` libraries and how to use them within the `NinjaRobotV3` project.

## 1. Initial Setup

This project uses `uv` for managing Python virtual environments and dependencies.

### 1.1. Create and Activate the Virtual Environment

It is recommended to use a virtual environment for this project.

```bash
# Create the virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate
```

### 1.2. Install Dependencies

Install the necessary packages for all libraries using `uv`.

```bash
# Install all dependencies from the subdirectories
uv pip install -e pi0disp
uv pip install -e piservo0
uv pip install -e vl53l0x_pigpio
uv pip install -e pi0buzzer
```

## 2. Using the Libraries

### 2.1. `pi0disp` - Display Driver

The `pi0disp` library is a high-speed driver for ST7789V-based displays on Raspberry Pi.

#### As a Library

You can use the `ST7789V` class to control the display in your Python scripts.

```python
from pi0disp import ST7789V
from PIL import Image, ImageDraw
import time

# Initialize the display
with ST7789V() as lcd:
    # Create an image with PIL
    image = Image.new("RGB", (lcd.width, lcd.height), "black")
    draw = ImageDraw.Draw(image)

    # Draw a blue circle
    draw.ellipse(
        (10, 10, lcd.width - 10, lcd.height - 10),
        fill="blue",
        outline="white"
    )

    # Display the image
    lcd.display(image)

    time.sleep(5)

    # Example of partial update
    draw.rectangle((50, 50, 100, 100), fill="red")
    lcd.display_region(image, 50, 50, 100, 100)

    time.sleep(5)
```

#### CLI Usage

The `pi0disp` command provides a simple CLI for testing the display.

```bash
# Run the ball animation demo
uv run pi0disp ball_anime

# Turn the display off
uv run pi0disp off
```

### 2.2. `piservo0` - Servo Motor Control

The `piservo0` library provides precise control over servo motors.

#### As a Library

Use the `PiServo` or `CalibrableServo` class to control your servos.

**Basic Usage (`PiServo`)**

```python
import time
import pigpio
from piservo0 import PiServo

PIN = 17

pi = pigpio.pi()
servo = PiServo(pi, PIN)

servo.move_pulse(1000)
time.sleep(0.5)

servo.move_max()
time.sleep(0.5)

servo.off()
pi.stop()
```

**Calibrated Usage (`CalibrableServo`)**

```python
import time
import pigpio
from piservo0 import CalibrableServo

PIN = 17

pi = pigpio.pi()
servo = CalibrableServo(pi, PIN) # Loads calibration from servo.json

servo.move_angle(45)  # Move to 45 degrees
time.sleep(1)

servo.move_center()
time.sleep(1)

servo.off()
pi.stop()
```

#### CLI Usage

The `piservo0` command allows for calibration and remote control.

**Calibration**

```bash
# Calibrate the servo on GPIO 17
uv run piservo0 calib 17
```

**API Server**

```bash
# Start the API server for servos on GPIO 17, 27, 22, 25
uv run piservo0 api-server 17 27 22 25
```

**API Client**

```bash
# Connect to the API server
uv run piservo0 api-client
```

### 2.3. `vl53l0x_pigpio` - Distance Sensor

The `vl53l0x_pigpio` library is a driver for the VL53L0X time-of-flight distance sensor.

#### As a Library

Use the `VL53L0X` class to get distance measurements.

```python
import pigpio
from vl53l0x_pigpio import VL53L0X
import time

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio")

try:
    with VL53L0X(pi) as tof:
        distance = tof.get_range()
        if distance > 0:
            print(f"Distance: {distance} mm")
        else:
            print("Invalid data.")
finally:
    pi.stop()
```

#### CLI Usage

The `vl53l0x_pigpio` command provides tools for interacting with the sensor.

**Get Distance**

```bash
# Get 5 distance readings
uv run vl53l0x_pigpio get --count 5
```

**Performance Test**

```bash
# Run a performance test with 500 measurements
uv run vl53l0x_pigpio performance --count 500
```

**Calibration**

```bash
# Calibrate the sensor with a target at 150mm
uv run vl53l0x_pigpio calibrate --distance 150
```

### 2.4. `pi0buzzer` - Buzzer Driver

The `pi0buzzer` library is a simple driver for a piezo buzzer.

#### As a Library

You can use the `Buzzer` class to control the buzzer in your Python scripts.

```python
import pigpio
import time
from pi0buzzer.driver import Buzzer

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio daemon.")

# Initialize the buzzer
buzzer = Buzzer(pi, 18)

# Play a custom sound
try:
    while True:
        buzzer.play_sound(440, 0.5) # Play 440 Hz for 0.5 seconds
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    buzzer.off()
    pi.stop()
```

#### CLI Usage

The `pi0buzzer` command provides a simple CLI for interacting with the buzzer.

**Initialization**

```bash
# Initialize the buzzer on GPIO 18
pi0buzzer init 18
```

**Play Music**

After initializing the buzzer, you can play music with it using your keyboard:

```bash
pi0buzzer playmusic
```

### 2.5. `pi0ninja_v3` - Robot Control Hub

The `pi0ninja_v3` library is the central controller for the NinjaRobot, integrating various drivers to create complex behaviors.

#### Servo Movement Recorder

This is a command-line tool that allows you to design, save, and play back complex servo movement sequences.

**How to Run**

To start the tool, run the following command from the project's root directory:

```bash
uv run python -m pi0ninja_v3.movement_recorder
```

You will be presented with a menu of options:

```
--- Servo Movement Recorder ---
1. Record new movement
2. Modify existing movement
3. Execute a movement
4. Clear movement
5. Exit
```

**1. Record New Movement**

This function allows you to create a new movement sequence step-by-step.

*   **Command Syntax:** You can control multiple servos in a single command, separated by a `/`. The format is `[SPEED_]PIN:ANGLE`.
    *   `PIN`: The GPIO pin number of the servo.
    *   `ANGLE`: The target angle. This can be a number from `-90` to `90`, or a special character:
        *   `X`: Moves the servo to its maximum rotation.
        *   `M`: Moves the servo to its minimum rotation.
        *   `C`: Moves the servo to its center position.
    *   `SPEED_`: An optional prefix to control the speed of the movement for that step.
        *   `S_`: Slow
        *   `M_`: Medium (Default)
        *   `F_`: Fast

*   **Example Command:** `S_17:30/27:C/25:X`
    *   This command moves servo 17 to 30 degrees, servo 27 to its center, and servo 25 to its maximum rotation, all with a "Slow" speed for the step.

*   **Auto-Completion:** If you do not specify a position for every servo, the tool will automatically use the servo's position from the previous step (or its center position if it's the first step). This ensures every step is a complete keyframe.

*   **Workflow:** After entering a command, you will be asked to:
    1.  **Confirm & Next:** Saves the step and prompts for the next command.
    2.  **Reset:** Reverts the servos to their positions before the last command.
    3.  **Finish Recording:** Prompts for a name and saves the entire sequence to `servo_movement.json`.

**2. Modify Existing Movement**

This option will list all previously saved movements. You can select one to re-record it from scratch. The old movement data will be replaced by the new sequence you create.

**3. Execute a Movement**

This option lists all saved movements and allows you to select one for playback. The robot will perform the entire sequence of movements, with the speed of each step determined by the `S/M/F` setting you chose during recording.

**4. Clear Movement**

This option lists all saved movements and allows you to permanently delete one from the `servo_movement.json` file.

---

# NinjaRobotV3 ユーザーガイド

このガイドでは、`pi0disp`、`piservo0`、`vl53l0x_pigpio`、および `pi0buzzer` ライブラリの概要と、`NinjaRobotV3` プロジェクト内での使用方法について説明します。

## 1. 初期設定

このプロジェクトでは、Pythonの仮想環境と依存関係の管理に `uv` を使用します。

### 1.1. 仮想環境の作成と有効化

このプロジェクトでは、仮想環境の使用を推奨します。

```bash
# 仮想環境の作成
uv venv

# 仮想環境の有効化
source .venv/bin/activate
```

### 1.2. 依存関係のインストール

`uv` を使用して、すべてのライブラリに必要なパッケージをインストールします。

```bash
# サブディレクトリからすべての依存関係をインストール
uv pip install -e pi0disp
uv pip install -e piservo0
uv pip install -e vl53l0x_pigpio
uv pip install -e pi0buzzer
```

## 2. ライブラリの使用

### 2.1. `pi0disp` - ディスプレイドライバ

`pi0disp` ライブラリは、Raspberry Pi 上の ST7789V ベースのディスプレイ用の高速ドライバです。

#### ライブラリとして

Python スクリプトで `ST7789V` クラスを使用してディスプレイを制御できます。

```python
from pi0disp import ST7789V
from PIL import Image, ImageDraw
import time

# ディスプレイの初期化
with ST7789V() as lcd:
    # PIL で画像を作成
    image = Image.new("RGB", (lcd.width, lcd.height), "black")
    draw = ImageDraw.Draw(image)

    # 青い円を描画
    draw.ellipse(
        (10, 10, lcd.width - 10, lcd.height - 10),
        fill="blue",
        outline="white"
    )

    # 画像を表示
    lcd.display(image)

    time.sleep(5)

    # 部分更新の例
    draw.rectangle((50, 50, 100, 100), fill="red")
    lcd.display_region(image, 50, 50, 100, 100)

    time.sleep(5)
```

#### CLI の使用法

`pi0disp` コマンドは、ディスプレイをテストするためのシンプルな CLI を提供します。

```bash
# ボールアニメーションデモを実行
uv run pi0disp ball_anime

# ディスプレイをオフにする
uv run pi0disp off
```

### 2.2. `piservo0` - サーボモーター制御

`piservo0` ライブラリは、サーボモーターを精密に制御します。

#### ライブラリとして

`PiServo` または `CalibrableServo` クラスを使用してサーボを制御します。

**基本的な使用法 (`PiServo`)**

```python
import time
import pigpio
from piservo0 import PiServo

PIN = 17

pi = pigpio.pi()
servo = PiServo(pi, PIN)

servo.move_pulse(1000)
time.sleep(0.5)

servo.move_max()
time.sleep(0.5)

servo.off()
pi.stop()
```

**キャリブレーション済みでの使用法 (`CalibrableServo`)**

```python
import time
import pigpio
from piservo0 import CalibrableServo

PIN = 17

pi = pigpio.pi()
servo = CalibrableServo(pi, PIN) # servo.json からキャリブレーションを読み込みます

servo.move_angle(45)  # 45度に移動
time.sleep(1)

servo.move_center()
time.sleep(1)

servo.off()
pi.stop()
```

#### CLI の使用法

`piservo0` コマンドは、キャリブレーションとリモート制御を可能にします。

**キャリブレーション**

```bash
# GPIO 17 のサーボをキャリブレーション
uv run piservo0 calib 17
```

**API サーバー**

```bash
# GPIO 17, 27, 22, 25 のサーボ用の API サーバーを起動
uv run piservo0 api-server 17 27 22 25
```

**API クライアント**

```bash
# API サーバーに接続
uv run piservo0 api-client
```

### 2.3. `vl53l0x_pigpio` - 距離センサー

`vl53l0x_pigpio` ライブラリは、VL53L0X 飛行時間型距離センサー用のドライバです。

#### ライブラリとして

`VL53L0X` クラスを使用して距離測定値を取得します。

```python
import pigpio
from vl53l0x_pigpio import VL53L0X
import time

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio に接続できませんでした")

try:
    with VL53L0X(pi) as tof:
        distance = tof.get_range()
        if distance > 0:
            print(f"距離: {distance} mm")
        else:
            print("無効なデータ")
finally:
    pi.stop()
```

#### CLI の使用法

`vl53l0x_pigpio` コマンドは、センサーと対話するためのツールを提供します。

**距離の取得**

```bash
# 5 回の距離測定値を取得
uv run vl53l0x_pigpio get --count 5
```

**パフォーマンステスト**

```bash
# 500 回の測定でパフォーマンステストを実行
uv run vl53l0x_pigpio performance --count 500
```

**キャリブレーション**

```bash
# 150mm のターゲットでセンサーをキャリブレーション
uv run vl53l0x_pigpio calibrate --distance 150
```

### 2.4. `pi0buzzer` - ブザーライブラリ

`pi0buzzer` ライブラリは、ピエゾブザー用のシンプルなドライバです。

#### ライブラリとして

Python スクリプトで `Buzzer` クラスを使用してブザーを制御できます。

```python
import pigpio
import time
from pi0buzzer.driver import Buzzer

# pigpio の初期化
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio デーモンに接続できませんでした")

# ブザーの初期化
buzzer = Buzzer(pi, 18)

# カスタムサウンドの再生
try:
    while True:
        buzzer.play_sound(440, 0.5) # 440 Hz の音を 0.5 秒間再生
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    buzzer.off()
    pi.stop()
```

#### CLI の使用法

`pi0buzzer` コマンドは、ブザーと対話するためのシンプルな CLI を提供します。

**初期化**

```bash
# GPIO 18 のブザーを初期化
pi0buzzer init 18
```

**音楽の再生**

ブザーを初期化した後、キーボードで音楽を再生できます:

```bash
pi0buzzer playmusic
```

### 2.5. `pi0ninja_v3` - ロボット制御ハブ

`pi0ninja_v3` ライブラリは、NinjaRobotの中央コントローラーであり、さまざまなドライバーを統合して複雑な動作を作成します。

#### サーボ動作レコーダー

これは、複雑なサーボ動作シーケンスを設計、保存、再生するためのコマンドラインツールです。

**実行方法**

ツールを起動するには、プロジェクトのルートディレクトリから次のコマンドを実行します。

```bash
uv run python -m pi0ninja_v3.movement_recorder
```

メニューオプションが表示されます。

```
--- Servo Movement Recorder ---
1. Record new movement
2. Modify existing movement
3. Execute a movement
4. Clear movement
5. Exit
```

**1. 新しい動作の記録 (Record New Movement)**

この機能を使用すると、新しい動作シーケンスをステップバイステップで作成できます。

*   **コマンド構文:** `/` で区切ることで、単一のコマンドで複数のサーボを制御できます。形式は `[SPEED_]PIN:ANGLE` です。
    *   `PIN`: サーボのGPIOピン番号。
    *   `ANGLE`: 目標角度。`-90` から `90` までの数値、または特殊文字を指定できます。
        *   `X`: サーボを最大回転位置に移動します。
        *   `M`: サーボを最小回転位置に移動します。
        *   `C`: サーボを中央位置に移動します。
    *   `SPEED_`: そのステップの動作速度を制御するためのオプションの接頭辞。
        *   `S_`: 低速 (Slow)
        *   `M_`: 中速 (Medium) (デフォルト)
        *   `F_`: 高速 (Fast)

*   **コマンド例:** `S_17:30/27:C/25:X`
    *   このコマンドは、サーボ17を30度、サーボ27を中央、サーボ25を最大回転位置に、「低速」で移動させます。

*   **自動補完:** すべてのサーボの位置を指定しなかった場合、ツールは自動的に前のステップのサーボ位置（最初のステップの場合は中央位置）を使用します。これにより、すべてのステップが完全なキーフレームになることが保証されます。

*   **ワークフロー:** コマンドを入力した後、次のいずれかを選択するよう求められます。
    1.  **確認して次へ (Confirm & Next):** ステップを保存し、次のコマンドの入力を求めます。
    2.  **リセット (Reset):** 直前のコマンドを実行する前の位置にサーボを戻します。
    3.  **記録終了 (Finish Recording):** 名前を尋ね、シーケンス全体を `servo_movement.json` に保存します。

**2. 既存の動作の修正 (Modify Existing Movement)**

このオプションは、以前に保存されたすべての動作を一覧表示します。一つを選択して、最初から再記録することができます。古い動作データは、作成した新しいシーケンスに置き換えられます。

**3. 動作の実行 (Execute a Movement)**

このオプションは、保存されたすべての動作を一覧表示し、再生するものを選択できます。ロボットは、記録時に選択した `S/M/F` 設定によって決まる速度で、一連の動作全体を実行します。

**4. 動作のクリア (Clear Movement)**

このオプションは、保存されたすべての動作を一覧表示し、`servo_movement.json` ファイルから一つを永久に削除することができます。
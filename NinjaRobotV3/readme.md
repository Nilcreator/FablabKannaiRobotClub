# NinjaRobotV3 ユーザーガイド (taniguide.md)

このガイドでは、`pi0disp`、`piservo0`、`vl53l0x_pigpio` ライブラリの包括的な概要と、`NinjaRobotV3` プロジェクト内での使用方法について説明します。

## 1. 初期設定

このプロジェクトでは、Pythonの仮想環境と依存関係の管理に `uv` を使用します。

### 1.1. 仮想環境の作成と有効化

このプロジェクトでは仮想環境の使用を推奨します。

```bash
# 仮想環境を作成
uv venv

# 仮想環境を有効化
source .venv/bin/activate
```

### 1.2. 依存関係のインストール

`uv` を使用して、3つのライブラリすべてに必要なパッケージをインストールします。

```bash
# サブディレクトリからすべての依存関係をインストール
uv pip install -e pi0disp
uv pip install -e piservo0
uv pip install -e vl53l0x_pigpio
```

## 2. ライブラリの使用方法

### 2.1. `pi0disp` - ディスプレイドライバ

`pi0disp` ライブラリは、Raspberry Pi 上の ST7789V ベースのディスプレイ用の高速ドライバです。

#### ライブラリとして

Python スクリプトで `ST7789V` クラスを使用してディスプレイを制御できます。

```python
from pi0disp import ST7789V
from PIL import Image, ImageDraw
import time

# ディスプレイを初期化
with ST7789V() as lcd:
    # PILで画像を作成
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

#### CLIでの使用方法

`pi0disp` コマンドは、ディスプレイをテストするためのシンプルなCLIを提供します。

```bash
# ボールアニメーションのデモを実行
uv run pi0disp ball_anime

# ディスプレイをオフにする
uv run pi0disp off
```

### 2.2. `piservo0` - サーボモーター制御

`piservo0` ライブラリは、サーボモーターの精密な制御を提供します。

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
servo = CalibrableServo(pi, PIN) # servo.jsonからキャリブレーションを読み込む

servo.move_angle(45)  # 45度に移動
time.sleep(1)

servo.move_center()
time.sleep(1)

servo.off()
pi.stop()
```

#### CLIでの使用方法

`piservo0` コマンドにより、キャリブレーションとリモート制御が可能です。

**キャリブレーション**

```bash
# GPIO 17のサーボをキャリブレーション
uv run piservo0 calib 17
```

**APIサーバー**

```bash
# GPIO 17, 27, 22, 25のサーボ用APIサーバーを起動
uv run piservo0 api-server 17 27 22 25
```

**APIクライアント**

```bash
# APIサーバーに接続
uv run piservo0 api-client
```

### 2.3. `vl53l0x_pigpio` - 距離センサー

`vl53l0x_pigpio` ライブラリは、VL53L0X ToF（Time-of-Flight）距離センサー用のドライバです。

#### ライブラリとして

`VL53L0X` クラスを使用して距離測定値を取得します。

```python
import pigpio
from vl53l0x_pigpio import VL53L0X
import time

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpioに接続できませんでした")

try:
    with VL53L0X(pi) as tof:
        distance = tof.get_range()
        if distance > 0:
            print(f"距離: {distance} mm")
        else:
            print("無効なデータです。")
finally:
    pi.stop()
```

#### CLIでの使用方法

`vl53l0x_pigpio` コマンドは、センサーと対話するためのツールを提供します。

**距離の取得**

```bash
# 5回の距離測定値を取得
uv run vl53l0x_pigpio get --count 5
```

**パフォーマンステスト**

```bash
# 500回の測定でパフォーマンステストを実行
uv run vl53l0x_pigpio performance --count 500
```

**キャリブレーション**

```bash
# 150mmのターゲットでセンサーをキャリブレーション
uv run vl53l0x_pigpio calibrate --distance 150
```

---

# NinjaRobotV3 User Guide (taniguide.md)

This guide provides a comprehensive overview of the `pi0disp`, `piservo0`, and `vl53l0x_pigpio` libraries and how to use them within the `NinjaRobotV3` project.

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

Install the necessary packages for all three libraries using `uv`.

```bash
# Install all dependencies from the subdirectories
uv pip install -e pi0disp
uv pip install -e piservo0
uv pip install -e vl53l0x_pigpio
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

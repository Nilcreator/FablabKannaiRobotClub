# `piservo0` & `pi0disp` ユーザーガイド

## はじめに

ようこそ！このガイドは、Raspberry Piを使ってロボットや電子工作を始めたいあなたのための手引書です。

- **`piservo0`**: サーボモーターを精密に動かすためのライブラリ
- **`pi0disp`**: 小型ディスプレイに文字や画像を表示するためのライブラリ

これら2つのライブラリと、最新のPython開発ツール`uv`を使い、自分だけのロボット制御プログラムをゼロから作成する方法を、プログラミング経験がない方でも理解できるように、一歩一歩丁寧に解説します。

### 準備するもの

- **ハードウェア**:
    - Raspberry Pi (Pi 4, Pi 5, または Pi Zero 2 W推奨)
    - サーボモーター (SG90など)
    - ST7789Vチップを搭載したSPI接続の小型ディスプレイ
    - ジャンパーワイヤー

- **ソフトウェア**:
    - Raspberry Pi OS (インストール済みであること)
    - インターネット接続

---

## 第1章: 開発環境のセットアップ

まず、プログラムを作成し、ライブラリを動かすための「開発環境」を整えます。

### 1.1. `pigpio`のインストールと有効化

`pigpio`は、Raspberry PiのGPIOピン（電子部品を接続するピン）を安全かつ簡単に制御するための重要なソフトウェアです。

1.  **ターミナルを開く**: Raspberry Piのデスクトップ左上にある黒い画面のアイコンをクリックします。

2.  **`pigpio`をインストール**: 以下の2つのコマンドを1行ずつ入力し、それぞれ`Enter`キーを押します。
    ```bash
    sudo apt update
    sudo apt install pigpio
    ```

3.  **`pigpio`を起動し、自動起動を設定**: 同様に、以下の2つのコマンドを実行します。これにより、Raspberry Piが起動するたびに`pigpio`が自動で実行されるようになります。
    ```bash
    sudo systemctl start pigpiod
    sudo systemctl enable pigpiod
    ```

### 1.2. `uv`のインストール

`uv`は、Pythonのライブラリ（便利なプログラムの部品集）をインストールしたり管理したりするための、非常に高速なツールです。

1.  **ターミナルで以下のコマンドを実行**:
    ```bash
    curl -L -s https://astral.sh/uv/install.sh | sh
    ```
    これにより、`uv`がシステムにインストールされます。

### 1.3. プロジェクトの準備と仮想環境の作成

次に、あなたのプロジェクト専用の作業フォルダと、ライブラリを管理するための「仮想環境」を作成します。

1.  **プロジェクト用フォルダを作成**:
    ```bash
    mkdir my_robot
    cd my_robot
    ```
    `my_robot`という名前のフォルダが作成され、その中に移動します。

2.  **仮想環境の作成**:
    ```bash
    uv venv
    ```
    このコマンドを実行すると、現在のフォルダ（`my_robot`）内に`.venv`という名前の特別なフォルダが作成されます。これが仮想環境です。これにより、このプロジェクトで使うライブラリが他のプロジェクトと混ざってしまうのを防ぎます。

---

## 第2章: `piservo0`でサーボモーターを動かす

いよいよサーボモーターを制御します。

### 2.1. `piservo0`のインストール

`uv`を使って`piservo0`ライブラリをインストールします。

```bash
uv pip install piservo0
```

### 2.2. サーボのキャリブレーション（調整）

サーボモーターは個体差があり、同じ指示でも少しずつ動きが違うことがあります。そのため、最初に「キャリブレーション（調整）」を行い、正確な動きを教え込みます。

1.  **配線**: サーボモーターをRaspberry Piに接続します。
    - **茶色/黒**: GND（6番ピンなど）
    - **赤**: 5V（2番ピンなど）
    - **オレンジ/黄**: GPIOピン（例: 17番ピン）

2.  **キャリブレーションツールを起動**:
    サーボをGPIO 17番ピンに接続した場合、以下のコマンドを実行します。
    ```bash
    uv run piservo0 calib 17
    ```

3.  **対話的に調整**:
    - `h`キーを押すとヘルプが表示されます。
    - `w`キーと`s`キーでサーボが動きます。
    - `Tab`キーで調整する角度（-90度, 0度, 90度）を切り替えます。
    - それぞれの角度で、サーボが真横、正面、反対側の真横を向くように`w`/`s`で微調整し、位置が決まったら`Enter`キーを押して保存します。
    - `q`キーで終了します。

    この調整データは、プロジェクトフォルダ内に`servo.json`というファイル名で保存されます。

### 2.3. 初めてのサーボ制御スクリプト

1.  **ファイルを作成**: `control_servo.py`という名前のファイルを作成し、以下のコードを貼り付けます。
    ```python
    import time
    import pigpio
    from piservo0 import CalibrableServo

    # --- 設定 ---
    SERVO_PIN = 17  # サーボを接続したGPIOピン番号

    # --- 初期化 ---
    pi = pigpio.pi()
    if not pi.connected:
        print("pigpioに接続できません。デーモンが実行されているか確認してください。")
        exit()

    # キャリブレーション済みのサーボとして初期化
    servo = CalibrableServo(pi, SERVO_PIN)
    print(f"GPIO {SERVO_PIN} のサーボを初期化しました。")

    try:
        # --- サーボを動かす ---
        print("中央 (0度) に移動します。")
        servo.move_angle(0)
        time.sleep(2)  # 2秒待つ

        print("最小角度 (-90度) に移動します。")
        servo.move_angle(-90)
        time.sleep(2)

        print("最大角度 (90度) に移動します。")
        servo.move_angle(90)
        time.sleep(2)

    except KeyboardInterrupt:
        print("
プログラムを終了します。")

    finally:
        # --- 終了処理 ---
        print("サーボをオフにします。")
        servo.off()
        pi.stop()
    ```

2.  **スクリプトを実行**:
    ```bash
    uv run python control_servo.py
    ```
    サーボが中央→片側→反対側へと順番に動けば成功です！

---

## 第3章: `pi0disp`でディスプレイに表示する

次に、ディスプレイに図形や文字を表示させます。

### 3.1. `pi0disp`のインストール

`uv`を使って`pi0disp`ライブラリをインストールします。`Pillow`という画像処理ライブラリも一緒にインストールされます。

```bash
uv pip install pi0disp Pillow
```

### 3.2. 初めてのディスプレイ表示スクリプト

1.  **配線**: ディスプレイのピンをRaspberry Piの対応するGPIOピンに接続します。（ディスプレイ製品の仕様書を確認してください）

2.  **ファイルを作成**: `show_on_display.py`という名前のファイルを作成し、以下のコードを貼り付けます。
    ```python
    from pi0disp import ST7789V
    from PIL import Image, ImageDraw

    print("ディスプレイを初期化します。")

    # 'with'構文を使うと、プログラム終了時に自動で後片付けをしてくれる
    with ST7789V() as lcd:
        # PILを使って画像を作成
        # lcd.width, lcd.height でディスプレイのサイズが取得できる
        image = Image.new("RGB", (lcd.width, lcd.height), "black")
        draw = ImageDraw.Draw(image)

        # 青い円を描画
        print("円を描画します。")
        draw.ellipse(
            (10, 10, lcd.width - 10, lcd.height - 10),
            fill="blue",
            outline="white"
        )

        # テキストを描画
        print("テキストを描画します。")
        draw.text((60, 150), "Hello, Robot!", fill="white")

        # 作成した画像（円とテキスト）をディスプレイに表示
        print("ディスプレイに表示します。")
        lcd.display(image)

    print("完了しました。")
    ```

3.  **スクリプトを実行**:
    ```bash
    uv run python show_on_display.py
    ```
    ディスプレイに黒い背景、青い円、そして"Hello, Robot!"という文字が表示されれば成功です。

---

## 第4章: すべてを組み合わせる

最後に、サーボの動きとディスプレイの表示を連動させたプログラムを作成します。

### 4.1. 目標

サーボモーターを-90度から+90度まで滑らかに動かし、現在の角度をリアルタイムでディスプレイに表示します。

### 4.2. 最終的なスクリプト

1.  **ファイルを作成**: `robot_control.py`という名前のファイルを作成し、以下のコードを貼り付けます。
    ```python
    import time
    import pigpio
    from piservo0 import CalibrableServo
    from pi0disp import ST7789V, draw_text
    from PIL import Image, ImageDraw, ImageFont

    # --- 設定 ---
    SERVO_PIN = 17

    # --- 初期化 ---
    pi = pigpio.pi()
    if not pi.connected:
        print("pigpioに接続できません。")
        exit()

    servo = CalibrableServo(pi, SERVO_PIN)

    # 'with'構文でディスプレイを初期化
    with ST7789V() as lcd:
        print("サーボとディスプレイの連携を開始します。Ctrl+Cで終了します。")

        try:
            # -90度から90度まで5度ずつ動かす
            for angle in range(-90, 91, 5):
                # 1. サーボを動かす
                servo.move_angle(angle)

                # 2. 表示する画像を作成
                #    毎回新しい黒い画像を作成して、前の描画を消す
                image = Image.new("RGB", (lcd.width, lcd.height), "black")
                draw = ImageDraw.Draw(image)

                # 3. 現在の角度をテキストとして描画
                text = f"Angle: {angle}"
                
                # テキストを中央に大きく表示
                draw_text(draw, text, ImageFont.load_default(size=30),
                          x='center', y='center',
                          width=lcd.width, height=lcd.height,
                          color=(255, 255, 255))

                # 4. ディスプレイに表示
                lcd.display(image)

                # 5. 少し待つ
                time.sleep(0.05)

            # 逆方向に動かす
            for angle in range(90, -91, -5):
                servo.move_angle(angle)
                image = Image.new("RGB", (lcd.width, lcd.height), "black")
                draw = ImageDraw.Draw(image)
                text = f"Angle: {angle}"
                draw_text(draw, text, ImageFont.load_default(size=30),
                          x='center', y='center',
                          width=lcd.width, height=lcd.height,
                          color=(255, 255, 255))
                lcd.display(image)
                time.sleep(0.05)

        except KeyboardInterrupt:
            print("
プログラムを終了します。")

        finally:
            # --- 終了処理 ---
            servo.off()
            pi.stop()
            print("サーボとディスプレイをオフにしました。")

    ```

### 4.3. 実行

```bash
uv run python robot_control.py
```

サーボがゆっくりと左右に往復し、その動きに合わせてディスプレイの角度表示がリアルタイムに更新されるはずです。

## まとめ

おめでとうございます！あなたは`piservo0`と`pi0disp`を使って、サーボモーターとディスプレイを連動させる基本的なプログラムを自力で作成することができました。

ここからが本当のスタートです。このガイドで学んだことを応用して、

-   複数のサーボを動かしてロボットアームを制御する
-   センサーの値に応じてサーボの動きやディスプレイ表示を変える
-   ボタン操作でロボットをコントロールする

# `piservo0` & `pi0disp` User Guide

## Introduction

Welcome! This guide is a handbook for those who want to start with robotics and electronics using a Raspberry Pi.

- **`piservo0`**: A library for precisely controlling servo motors.
- **`pi0disp`**: A library for displaying text and images on small displays.

Using these two libraries and the modern Python development tool `uv`, we will carefully explain, step-by-step, how to create your own robot control program from scratch, in a way that even those without programming experience can understand.

### What You'll Need

- **Hardware**:
    - Raspberry Pi (Pi 4, Pi 5, or Pi Zero 2 W recommended)
    - Servo motor (e.g., SG90)
    - A small SPI-connected display with an ST7789V chip
    - Jumper wires

- **Software**:
    - Raspberry Pi OS (must be installed)
    - Internet connection

---

## Chapter 1: Setting Up the Development Environment

First, let's set up the "development environment" for creating programs and running the libraries.

### 1.1. Installing and Enabling `pigpio`

`pigpio` is an essential piece of software for safely and easily controlling the Raspberry Pi's GPIO pins (the pins you connect electronic components to).

1.  **Open the Terminal**: Click the black screen icon in the top-left corner of the Raspberry Pi desktop.

2.  **Install `pigpio`**: Enter the following two commands, one line at a time, pressing `Enter` after each one.
    ```bash
    sudo apt update
    sudo apt install pigpio
    ```

3.  **Start and Enable `pigpio`**: Similarly, execute the next two commands. This ensures that `pigpio` starts automatically every time your Raspberry Pi boots up.
    ```bash
    sudo systemctl start pigpiod
    sudo systemctl enable pigpiod
    ```

### 1.2. Installing `uv`

`uv` is an extremely fast tool for installing and managing Python libraries (collections of useful program components).

1.  **Execute the following command in the terminal**:
    ```bash
    curl -L -s https://astral.sh/uv/install.sh | sh
    ```
    This will install `uv` on your system.

### 1.3. Project Preparation and Creating a Virtual Environment

Next, let's create a dedicated working folder for your project and a "virtual environment" to manage your libraries.

1.  **Create a project folder**:
    ```bash
    mkdir my_robot
    cd my_robot
    ```
    This creates a folder named `my_robot` and moves you inside it.

2.  **Create a virtual environment**:
    ```bash
    uv venv
    ```
    Running this command creates a special folder named `.venv` inside your current folder (`my_robot`). This is the virtual environment. It prevents the libraries used in this project from conflicting with other projects.

---

## Chapter 2: Controlling a Servo Motor with `piservo0`

Now, let's get to controlling a servo motor.

### 2.1. Installing `piservo0`

Use `uv` to install the `piservo0` library.

```bash
uv pip install piservo0
```

### 2.2. Calibrating Your Servo

Servo motors have individual differences, and their movements can vary slightly even with the same command. Therefore, we first perform "calibration" to teach them precise movements.

1.  **Wiring**: Connect the servo motor to the Raspberry Pi.
    - **Brown/Black**: GND (e.g., Pin 6)
    - **Red**: 5V (e.g., Pin 2)
    - **Orange/Yellow**: A GPIO pin (e.g., Pin 17)

2.  **Launch the calibration tool**:
    If you connected the servo to GPIO pin 17, run the following command:
    ```bash
    uv run piservo0 calib 17
    ```

3.  **Interactive Adjustment**:
    - Press the `h` key for help.
    - The `w` and `s` keys will move the servo.
    - The `Tab` key switches between the angles to be adjusted (-90°, 0°, 90°).
    - For each angle, use `w`/`s` to fine-tune the servo's position so it points directly to the side, front, and opposite side. Once a position is set, press `Enter` to save it.
    - Press `q` to quit.

    This calibration data is saved in a file named `servo.json` within your project folder.

### 2.3. Your First Servo Control Script

1.  **Create a file**: Create a file named `control_servo.py` and paste the following code into it.
    ```python
    import time
    import pigpio
    from piservo0 import CalibrableServo

    # --- Settings ---
    SERVO_PIN = 17  # The GPIO pin the servo is connected to

    # --- Initialization ---
    pi = pigpio.pi()
    if not pi.connected:
        print("Could not connect to pigpio. Is the daemon running?")
        exit()

    # Initialize as a calibrated servo
    servo = CalibrableServo(pi, SERVO_PIN)
    print(f"Initialized servo on GPIO {SERVO_PIN}.")

    try:
        # --- Move the Servo ---
        print("Moving to center (0 degrees).")
        servo.move_angle(0)
        time.sleep(2)  # Wait for 2 seconds

        print("Moving to minimum angle (-90 degrees).")
        servo.move_angle(-90)
        time.sleep(2)

        print("Moving to maximum angle (90 degrees).")
        servo.move_angle(90)
        time.sleep(2)

    except KeyboardInterrupt:
        print("
Exiting program.")

    finally:
        # --- Cleanup ---
        print("Turning servo off.")
        servo.off()
        pi.stop()
    ```

2.  **Run the script**:
    ```bash
    uv run python control_servo.py
    ```
    If the servo moves to the center, then to one side, and finally to the other side, it's a success!

---

## Chapter 3: Displaying on the Screen with `pi0disp`

Next, let's display shapes and text on the screen.

### 3.1. Installing `pi0disp`

Use `uv` to install the `pi0disp` library. An image processing library called `Pillow` will be installed alongside it.

```bash
uv pip install pi0disp Pillow
```

### 3.2. Your First Display Script

1.  **Wiring**: Connect the display's pins to the corresponding GPIO pins on the Raspberry Pi (check your display's datasheet for the pinout).

2.  **Create a file**: Create a file named `show_on_display.py` and paste the following code into it.
    ```python
    from pi0disp import ST7789V
    from PIL import Image, ImageDraw

    print("Initializing display.")

    # Using a 'with' statement automatically handles cleanup when the program ends
    with ST7789V() as lcd:
        # Create an image using PIL
        # You can get the display size with lcd.width and lcd.height
        image = Image.new("RGB", (lcd.width, lcd.height), "black")
        draw = ImageDraw.Draw(image)

        # Draw a blue circle
        print("Drawing a circle.")
        draw.ellipse(
            (10, 10, lcd.width - 10, lcd.height - 10),
            fill="blue",
            outline="white"
        )

        # Draw text
        print("Drawing text.")
        draw.text((60, 150), "Hello, Robot!", fill="white")

        # Display the created image (circle and text) on the screen
        print("Displaying the image.")
        lcd.display(image)

    print("Done.")
    ```

3.  **Run the script**:
    ```bash
    uv run python show_on_display.py
    ```
    If you see a black background, a blue circle, and the text "Hello, Robot!" on your display, it's a success.

---

## Chapter 4: Putting It All Together

Finally, let's create a program that links the servo's movement with the display's output.

### 4.1. The Goal

Smoothly move a servo motor from -90 to +90 degrees and display its current angle on the screen in real-time.

### 4.2. The Final Script

1.  **Create a file**: Create a file named `robot_control.py` and paste the following code into it.
    ```python
    import time
    import pigpio
    from piservo0 import CalibrableServo
    from pi0disp import ST7789V, draw_text
    from PIL import Image, ImageDraw, ImageFont

    # --- Settings ---
    SERVO_PIN = 17

    # --- Initialization ---
    pi = pigpio.pi()
    if not pi.connected:
        print("Could not connect to pigpio.")
        exit()

    servo = CalibrableServo(pi, SERVO_PIN)

    # Initialize the display using a 'with' statement
    with ST7789V() as lcd:
        print("Starting servo and display integration. Press Ctrl+C to exit.")

        try:
            # Move from -90 to 90 degrees in 5-degree steps
            for angle in range(-90, 91, 5):
                # 1. Move the servo
                servo.move_angle(angle)

                # 2. Create the image to display
                #    Create a new black image each time to clear the previous drawing
                image = Image.new("RGB", (lcd.width, lcd.height), "black")
                draw = ImageDraw.Draw(image)

                # 3. Draw the current angle as text
                text = f"Angle: {angle}"
                
                # Display the text large and centered
                draw_text(draw, text, ImageFont.load_default(size=30),
                          x='center', y='center',
                          width=lcd.width, height=lcd.height,
                          color=(255, 255, 255))

                # 4. Display on the screen
                lcd.display(image)

                # 5. Wait a little
                time.sleep(0.05)

            # Move in the reverse direction
            for angle in range(90, -91, -5):
                servo.move_angle(angle)
                image = Image.new("RGB", (lcd.width, lcd.height), "black")
                draw = ImageDraw.Draw(image)
                text = f"Angle: {angle}"
                draw_text(draw, text, ImageFont.load_default(size=30),
                          x='center', y='center',
                          width=lcd.width, height=lcd.height,
                          color=(255, 255, 255))
                lcd.display(image)
                time.sleep(0.05)

        except KeyboardInterrupt:
            print("
Exiting program.")

        finally:
            # --- Cleanup ---
            servo.off()
            pi.stop()
            print("Turned off servo and display.")
    ```

### 4.3. Execution

```bash
uv run python robot_control.py
```

The servo should slowly sweep back and forth, and the angle displayed on the screen should update in real-time to match its movement.

## Conclusion

Congratulations! You have successfully created a basic program that integrates a servo motor and a display using `piservo0` and `pi0disp`.

This is just the beginning. Apply what you've learned in this guide to:

-   Control a robot arm by moving multiple servos.
-   Change the servo's movement or the display's output based on sensor readings.
-   Control your robot with button inputs.

...and bring your own ideas to life!

For more detailed information and advanced usage, please refer to the `README.md` files of each library and the sample code in their `samples` folders.


など、あなたのアイデアを形にしていきましょう！

さらに詳しい情報や高度な使い方については、各ライブラリの`README.md`や`samples`フォルダの中のサンプルコードを参考にしてください。

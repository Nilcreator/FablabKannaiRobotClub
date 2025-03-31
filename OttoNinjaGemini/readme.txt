# 忍者 Gemini ロボット

## 1. 概要

このPythonスクリプト (`Ninja_Gemini_Movement_Optimized.py`) は、Raspberry Pi Zero、DFRobot IO Expansion HAT、超音波距離センサー、およびブザーを使用して構築された4サーボロボットを制御します。

このロボットは、歩行、走行、旋回、挨拶などの様々な定義済み動作を実行でき、ユーザーが入力した自然言語のテキストコマンドに基づいてサーボを特定の角度に動かすこともできます。Google Gemini Pro AIモデルがこれらのテキストコマンドの解釈に使用されます。

さらに、超音波センサーを使用して近くの障害物を検出し、物体が近すぎる場合（5cm以内）には特定の動作（歩行、走行など）を自動的に停止します。ブザーを使用して、さまざまなアクションやイベントに対する音声フィードバックを提供します。

## 2. 主な機能

-   テキストベース制御: 平易な英語のコマンドを受け付けます。
-   Gemini AI統合: GoogleのGemini Proモデルを使用してユーザーコマンドを理解し、目的のサーボ角度や動作修飾子（速度など）を抽出します。
-   定義済み動作: `walk`（歩行）、`run`（走行）、`turn left`（左旋回）、`turn right`（右旋回）、`rotate left`（左回転）、`rotate right`（右回転）、`step back`（後退ステップ）、`run back`（後退走行）、`hello`（挨拶）、`rest`（休憩）、`stop`（停止）などの特定のアクションに対応する関数が含まれています。
-   速度変更: `walk`や`run`などの連続動作に対して「fast」（速い）または「slow」（遅い）コマンドを指定できます。
-   超音波距離センシング: HC-SR04センサーを使用して距離を測定します。
-   障害物回避: 物体が5cm以内に検出された場合、前進する連続動作（歩行、走行など）を自動的に停止し、「danger」（危険）サウンドを再生します。
-   サウンドフィードバック: ブザー（`Ninja_Buzzer.py`によって制御）を使用して、起動、シャットダウン、特定の動作（挨拶、旋回）、障害物検出（危険）などの音声キューを提供します。
-   サーボ制御: DFRobot HATのPWM出力に接続された4つのサーボを管理します。サーボをデフォルト位置にリセットする機能が含まれています。
-   連続動作のためのスレッド: `walk`や`run`などの連続アクションを別々のスレッドで実行し、メインプログラムが「stop」のようなコマンドを受け付けられるようにします。
-   堅牢なクリーンアップ: プログラムが停止した際（エラー発生時も含む）に、GPIOリソースが適切に解放されることを保証します。

## 3. ハードウェア要件

-   Raspberry Pi Zero（またはZero W推奨）
-   DFRobot IO Expansion HAT for Raspberry Pi Zero
-   サーボ x 4（動作関数で指定されている180度/360度サーボの組み合わせ）
-   HC-SR04 超音波距離センサー
-   アクティブブザー
-   外部5V電源: サーボ用に必須（別電源推奨）。グランド（GND）を共通に接続してください。
-   ジャンパーワイヤー
-   MicroSDカード（8GB以上）とRaspberry Pi OS（Lite推奨）

## 4. ソフトウェア設定

-   Python 3
-   必要なライブラリ:
    -   `google-generativeai`: `pip install google-generativeai`でインストール
    -   `RPi.GPIO`: `pip install RPi.GPIO`でインストール（`sudo apt install python3-rpi.gpio`が必要な場合あり）
    -   `DFRobot_RaspberryPi_Expansion_Board`: DFRobotの指示に従ってインストール（通常、ライブラリディレクトリ内で`sudo python setup.py install`を実行）。スクリプトの場所からアクセス可能であることを確認してください。
    -   `Ninja_Buzzer.py`: `Ninja_Gemini_Movement_Optimized.py`と同じディレクトリにある必要があります。
-   Google Cloud設定:
    -   Vertex AI APIが有効化されたGoogle Cloudプロジェクト。
    -   認証: 以下のいずれかを設定：
        -   APIキー: スクリプト内の`GOOGLE_API_KEY`変数を設定。（キーは安全に保管してください！）
        -   ADC（推奨）: Pi Zeroで`gcloud auth application-default login`を実行し、正しいプロジェクトが選択されていることを確認。（`gcloud`のインストールが必要な場合があります）。

## 5. 動作の仕組み（コアロジック）

1.  初期化 (`if __name__ == "__main__":`):
    -   GPIOモードを設定 (`GPIO.BCM`)。
    -   `initialize_hardware()`を呼び出し:
        -   センサーとブザー用のGPIOピンを設定。
        -   ブザーPWMオブジェクトを初期化。
        -   DFRobot Board接続（I2C）を初期化。
        -   DFRobotサーボコントローラーを初期化。
        -   サーボを開始位置にリセット。
        -   「happy」（起動）サウンドを再生。
    -   `initialize_gemini()`を呼び出し:
        -   Google Cloudへの認証を設定。
        -   指定されたGemini AIモデル（`gemini-pro`）をロード。
2.  メインループ (`while True:`):
    -   障害物チェック: 連続動作が実行中の可能性がある場合（`not stop_movement`）、`measure_distance()`で距離を確認。5cm未満なら、「danger」サウンドを再生し、`stop()`を呼び出して動作を停止し、`continue`で次のループへ（ユーザー入力をスキップ）。
    -   ユーザー入力取得: ユーザーにテキストコマンドの入力を促す（例：「walk fast」、「hello」、「move servo 0 to 45」）。
    -   終了処理: 「quit」または「exit」をチェック。
    -   前の動作を停止: 新しいコマンドを処理する前に、`stop()`を無条件に呼び出して、以前の連続動作を停止し、サーボをリセット。
    -   コマンド処理:
        -   キーワード照合: ユーザー入力に`COMMAND_MAP`で定義された既知のキーワード（「walk」、「run」、「hello」、「stop」など）が含まれているか確認。単純な速度修飾子（「fast」、「slow」）も抽出。
        -   マップされたコマンド実行: キーワードが見つかった場合、`COMMAND_MAP`から対応する関数を実行。連続動作の場合は抽出された速度修飾子を渡す。
        -   Gemini解釈（フォールバック）: キーワードに一致しない場合、ユーザーの生コマンドを`get_gemini_command_details()`経由でGeminiに送信。
        -   Gemini応答解析: `extract_command_details_from_json()`を使用して、GeminiのJSON風応答から角度と潜在的な速度/スタイルを解析。
        -   直接角度コマンド実行: 有効な角度が解析された場合、`servo_controller.move()`を使用して各サーボを直接移動。
        -   無効なコマンド: キーワードに一致せず、Geminiの解析も失敗した場合、「Invalid command」と表示。
    -   ループ: サイクルを繰り返す。
3.  クリーンアップ (`finally:` ブロック):
    -   このブロックはプログラム終了時（通常終了、Ctrl+C、エラー）に常に実行される。
    -   `stop()`を呼び出して動作を停止し、サーボをリセット。
    -   ブザーPWMを停止。
    -   ブザーモジュールと`RPi.GPIO`のクリーンアップ関数を呼び出して、すべてのハードウェアリソースを適切に解放。
    -   最後のサウンドを再生（現在は「thanks」、必要なら専用の「sleepy」サウンドに変更可能）。

## 6. 詳細な関数説明

-   `initialize_hardware() / initialize_gemini()`: ハードウェアコンポーネントとAIモデルに必要な接続とオブジェクトを設定。スクリプト機能の基盤。
-   `print_board_status()`: DFRobot HAT通信のステータスを報告。
-   `get_sleep_time(speed)`: 速度修飾子に基づいて`time.sleep()`の持続時間を計算。
-   `measure_distance()`: 超音波センサーを使用して距離を計算。
-   `get_gemini_command_details(text_command)`: ユーザーコマンドをGeminiに送信し、AIの解釈を取得。
-   `extract_command_details_from_json(json_string)`: GeminiのJSON風応答を解析し、角度と修飾子を抽出。
-   `reset_servos()`: サーボを定義済みのデフォルト立ち位置角度に移動。
-   動作関数 (`hello`, `walk`, `run`, etc.): 特定のロボットアクションのロジックを含む。サーボ移動、遅延、サウンドトリガー、障害物チェック（連続動作）など。
-   `stop()`: 連続動作を停止し、`reset_servos()`を呼び出す。
-   `continuous_movement(movement_func, speed, style)`: `walk`や`run`のような長時間実行アクションを別スレッドで開始。
-   `cleanup()`: GPIOリソースを安全に解放。

## 7. コマンド例

-   `hello` - 挨拶シーケンス + サウンドを実行。
-   `walk` - 通常速度で前進歩行を開始。
-   `walk fast` - 高速で前進歩行を開始。
-   `run slow` - 低速で前進走行を開始 + excitingサウンド。
-   `turn left` - 1回の左旋回 + サウンドを実行。
-   `rotate right fast` - 高速で時計回りの回転を開始 + サウンド。
-   `step back` - 1回の後退ステップシーケンス + scaredサウンドを実行。
-   `move servo 1 to 120` - サーボ1（PWM1）を120度に移動。
-   `set servo 0 to 30 degrees and servo 3 to 150 degrees` - 特定のサーボを移動。
-   `stop` - 連続動作を停止し、サーボをリセット。
-   `rest` - サーボを定義済みの休憩位置に移動。
-   `quit` または `exit` - プログラムを停止 + 最後のサウンド。

## 8. 重要事項と設定

-   APIキー: キーを安全に保管してください。 `GOOGLE_API_KEY`を設定するか、ADCを使用してください。
-   ピン番号: 重要: スクリプト上部の`TRIG_PIN`、`ECHO_PIN`、`BUZZER_PIN`定数が、HATのGPIOへの実際の接続と一致していることを確認してください。
-   サーボPWMピン: サーボ0〜3がHATのPWM出力0〜3にマッピングされていると仮定。
-   外部電源: 必須: サーボには別途5V電源を使用してください。グランド（GND）を接続してください！
-   ライブラリパス: `DFRobot_...`ライブラリが正しくインストールされ、`Ninja_Buzzer.py`が同じディレクトリにあることを確認してください。
-   サーボキャリブレーション: 角度範囲、リセット/休憩位置、特に360度サーボの速度制御値（`run`, `rotateleft`など）を微調整する必要があるかもしれません。360度サーボでは通常`servo.move(90)`が停止です。
-   リソース制限: Pi Zeroは性能が限られています。遅延が発生する可能性があります。

## 9. 基本的なトラブルシューティング

-   動かない: 配線（電源、GND、信号）、コード内のピン番号、外部サーボ電源、DFRobotボードステータス（`i2cdetect -y 1`）を確認。GPIOパーミッションを確認（DFRobotライブラリ使用時は通常不要）。
-   ブザーが鳴らない: 配線、`BUZZER_PIN`、`Ninja_Buzzer.py`を確認。
-   超音波センサーの問題: 配線、`TRIG_PIN`/`ECHO_PIN`を確認。センサーの視界を確保。
-   Geminiエラー: APIキー/ADC設定、インターネット接続、Vertex AI API有効化を確認。Geminiのエラーメッセージを読む。
-   `ImportError`: DFRobotライブラリのインストールと`Ninja_Buzzer.py`の場所を確認。
-   一般的なエラー: Pythonのエラーメッセージを読む。`print()`文を追加してデバッグ。

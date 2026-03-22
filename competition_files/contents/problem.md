本コンペティションでは、ビーチの気象条件からその日のアイスクリーム売上個数を予測する回帰問題です。
気温・日照時間・湿度の3つの特徴量から、1日あたりの売上個数 ice_sales を予測してください。

- **入力**：
  - id, temperature, sunshine_h, humidity, ice_sales からなる訓練用データ（train.csv）
  - id, temperature, sunshine_h, humidity からなるテストデータ（test.csv）

- **出力**：
  - 各 id の売上個数の予測値 ice_sales（sample_submission.csv 形式）

- **評価指標**：
  - RMSE (Root Mean Square Error)

### :material/table_chart: 特徴量の説明

| 列名 | 説明 | 単位 |
|------|-----|------|
| id | 各行のユニークID | - |
| temperature | その日の最高気温 | °C |
| sunshine_h | その日の日照時間 | 時間 |
| humidity | その日の湿度 | % |
| ice_sales | アイスクリームの1日あたり売上個数（目的変数） | 個 |

## コンペ終了後公開ファイル

- **answer.csv**: 正解データ
- **generate_competition_data.py**: 問題データ作成ソース

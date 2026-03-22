import numpy as np
import pandas as pd

np.random.seed(42)


# ══════════════════════════════════════════════════════
# 真の関数（主催者のみ保持・コンペ終了後に公開）
# テーマ：ビーチのアイスクリーム売上個数予測
#   説明変数: temperature（最高気温°C）
#             sunshine_h（日照時間h）
#             humidity（湿度%）
#   目的変数: ice_sales（アイス売上個数/日）
# ══════════════════════════════════════════════════════
def true_function(temp, sunshine, humidity, noise_std=25):
    sales = (
        -400
        + 12   * temp           # 気温の線形効果
        + 0.4  * temp**2        # 気温の2次効果（高温ほど急増）
        + 30   * sunshine**1.3  # 日照時間の非線形効果
        - 1.8  * humidity       # 湿度が高いと売上DOWN
        + 0.5  * temp * sunshine  # 気温×日照の交互作用
        + np.random.normal(0, noise_std, size=len(temp))
    )
    return np.clip(sales, 0, None).round(0).astype(int)


# ─────────────────────────────────────────
# 1. train.csv
#    訓練データ（通常の夏日）
#    気温: 18〜32°C / 日照: 2〜8h / 湿度: 50〜85%
#    id: 1 〜 500
# ─────────────────────────────────────────
N_TRAIN = 500
temp_tr = np.random.uniform(18, 32, N_TRAIN)
sun_tr  = np.random.uniform(2,  8,  N_TRAIN)
hum_tr  = np.random.uniform(50, 85, N_TRAIN)
y_tr    = true_function(temp_tr, sun_tr, hum_tr)

train_ids = list(range(1, N_TRAIN + 1))

df_train = pd.DataFrame({
    "id":          train_ids,
    "temperature": temp_tr.round(1),
    "sunshine_h":  sun_tr.round(1),
    "humidity":    hum_tr.round(1),
    "ice_sales":   y_tr,
})
df_train.to_csv("train.csv", index=False)
print(f"train.csv             : {len(df_train)} 件 を出力しました")


# ─────────────────────────────────────────
# 2. テストデータ生成（内挿 + 外挿）
#    内挿: 訓練範囲内（20〜30°C）
#    外挿: 猛暑日（35〜40°C）← 訓練範囲外
#    id: 501 〜 800
# ─────────────────────────────────────────
N_INTER = 150
N_EXTRA = 150

# 内挿テストデータ（訓練範囲内）
temp_i = np.random.uniform(20, 30, N_INTER)
sun_i  = np.random.uniform(3,  7,  N_INTER)
hum_i  = np.random.uniform(55, 80, N_INTER)
y_i    = true_function(temp_i, sun_i, hum_i)

# 外挿テストデータ（猛暑：訓練範囲外）
temp_e = np.random.uniform(35, 40, N_EXTRA)
sun_e  = np.random.uniform(9,  12, N_EXTRA)
hum_e  = np.random.uniform(30, 50, N_EXTRA)
y_e    = true_function(temp_e, sun_e, hum_e)


# ─────────────────────────────────────────
# 3. Public / Private 割り当て
#
#   Public  (暫定順位): 内挿90% + 外挿10%
#   Private (最終順位): 外挿90% + 内挿10%
#   ※ 各行は Public か Private のどちらか一方
#
#   内挿150件 → Public 135件 / Private  15件
#   外挿150件 → Public  15件 / Private 135件
# ─────────────────────────────────────────
inter_idx = np.arange(N_INTER)
extra_idx = np.arange(N_EXTRA)
np.random.shuffle(inter_idx)
np.random.shuffle(extra_idx)

usage_i = np.empty(N_INTER, dtype=object)
usage_e = np.empty(N_EXTRA, dtype=object)

usage_i[inter_idx[:135]] = "Public"    # 内挿135件 → Public
usage_i[inter_idx[135:]] = "Private"   # 内挿 15件 → Private
usage_e[extra_idx[:15]]  = "Public"    # 外挿 15件 → Public
usage_e[extra_idx[15:]]  = "Private"   # 外挿135件 → Private


# ─────────────────────────────────────────
# 4. test.csv
#    参加者配布・ラベルなし・シャッフル済み
# ─────────────────────────────────────────
test_id_start = N_TRAIN + 1
inter_ids = list(range(test_id_start, test_id_start + N_INTER))
extra_ids = list(range(test_id_start + N_INTER, test_id_start + N_INTER + N_EXTRA))

df_test = pd.concat([
    pd.DataFrame({
        "id":          inter_ids,
        "temperature": temp_i.round(1),
        "sunshine_h":  sun_i.round(1),
        "humidity":    hum_i.round(1),
    }),
    pd.DataFrame({
        "id":          extra_ids,
        "temperature": temp_e.round(1),
        "sunshine_h":  sun_e.round(1),
        "humidity":    hum_e.round(1),
    }),
], ignore_index=True)

df_test = df_test.sample(frac=1, random_state=99).reset_index(drop=True)
df_test.to_csv("test.csv", index=False)
print(f"test.csv              : {len(df_test)} 件 を出力しました")


# ─────────────────────────────────────────
# 5. answer.csv（主催者保管）
#    列: id, ice_sales, Usage（"Public" or "Private"）
# ─────────────────────────────────────────
df_answer = pd.concat([
    pd.DataFrame({"id": inter_ids, "ice_sales": y_i, "Usage": usage_i}),
    pd.DataFrame({"id": extra_ids, "ice_sales": y_e, "Usage": usage_e}),
], ignore_index=True)

# test.csv のID順に並べ替え
df_answer = df_test[["id"]].merge(df_answer, on="id")
df_answer.to_csv("answer.csv", index=False)
print(f"answer.csv            : {len(df_answer)} 件 を出力しました")


# ─────────────────────────────────────────
# 6. sample_submission.csv
#    全予測値=0のサンプル提出ファイル
# ─────────────────────────────────────────
df_sample = pd.DataFrame({
    "id":        df_test["id"],
    "ice_sales": 0,
})
df_sample.to_csv("sample_submission.csv", index=False)
print(f"sample_submission.csv : {len(df_sample)} 件 を出力しました")


# ─────────────────────────────────────────
# 確認サマリ
# ─────────────────────────────────────────
pub  = df_answer[df_answer["Usage"] == "Public"]
priv = df_answer[df_answer["Usage"] == "Private"]
inter_ids_set = set(inter_ids)

pub_i  = pub["id"].isin(inter_ids_set).sum()
priv_i = priv["id"].isin(inter_ids_set).sum()

print()
print("=== Public / Private 内訳 ===")
print(f"Public  ({len(pub)} 件) : 内挿 {pub_i} 件 ({pub_i/len(pub)*100:.0f}%)  外挿 {len(pub)-pub_i} 件 ({(len(pub)-pub_i)/len(pub)*100:.0f}%)")
print(f"Private ({len(priv)} 件) : 内挿 {priv_i} 件 ({priv_i/len(priv)*100:.0f}%)  外挿 {len(priv)-priv_i} 件 ({(len(priv)-priv_i)/len(priv)*100:.0f}%)")

import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
import joblib

# تحميل البيانات
df = pd.read_csv("training_data.csv")

# تعديل اسم العمود
df.rename(columns={"close": "price"}, inplace=True)

# التحقق من الأعمدة
required_columns = ["price", "rsi", "macd", "decision"]
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"البيانات يجب أن تحتوي على الأعمدة: {required_columns}")

# تجهيز الميزات والهدف
X = df[["price", "rsi", "macd"]]
y = df["decision"]

# تحويل القرار إلى أرقام
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# تدريب النموذج
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    use_label_encoder=False,
    eval_metric="mlogloss"
)

model.fit(X, y_encoded)

# حفظ النموذج
joblib.dump(model, "xgb_model.pkl")
joblib.dump(le, "label_encoder.pkl")

print("✅ تم تدريب النموذج XGBoost وحفظه في xgb_model.pkl")

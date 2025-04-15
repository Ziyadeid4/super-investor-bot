import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# قراءة البيانات
df = pd.read_csv("training_data.csv")

# التأكد من الأعمدة الموجودة
print("📊 الأعمدة:", df.columns.tolist())

# اختيار الأعمدة المتوفرة فقط
X = df[["rsi", "macd", "signal"]]
y = df["decision"]

# تدريب النموذج
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# حفظ النموذج
joblib.dump(model, "model.pkl")
print("✅ تم حفظ النموذج في model.pkl")

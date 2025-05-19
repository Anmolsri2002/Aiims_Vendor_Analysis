import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Step 1: Raw data (replace with file read if needed)
data = [
    ["Vendor A", "X-Ray Machine", "Medical Machine", 974908, 1259967],
    ["Vendor A", "Surgical Kit", "Equipment", 158391, 197004],
    ["Vendor A", "Stretcher A", "Stretcher", 18624, 23930],
    ["Vendor B", "MRI Scanner", "Medical Machine", 2900225, 3694036],
    ["Vendor B", "Ventilator", "Equipment", 452058, 542232],
    ["Vendor B", "Medicine A", "Medicine", 5439, 6964],
    ["Vendor C", "Ventilator", "Equipment", 468340, 502118],
    ["Vendor C", "Stretcher B", "Stretcher", 27042, 29719],
    ["Vendor C", "Medicine B", "Medicine", 3067, 3255],
    ["Vendor C", "Medicine C", "Medicine", 2190, 2478],
    ["Vendor D", "X-Ray Machine", "Medical Machine", 1057035, 1212598],
    ["Vendor D", "MRI Scanner", "Medical Machine", 3289939, 3677616],
    ["Vendor D", "Surgical Kit", "Equipment", 153226, 192633],
    ["Vendor E", "Ventilator", "Equipment", 451326, 514145],
    ["Vendor E", "Stretcher A", "Stretcher", 21234, 23787],
    ["Vendor E", "Medicine A", "Medicine", 4731, 5609],
    ["Vendor E", "Medicine C", "Medicine", 1849, 2007],
    ["Vendor F", "Surgical Kit", "Equipment", 140201, 175328],
    ["Vendor F", "Stretcher B", "Stretcher", 30975, 33101],
    ["Vendor F", "Medicine B", "Medicine", 2825, 3663],
]

df_items = pd.DataFrame(data, columns=["Vendor", "Item", "Category", "Hist_Unit_Price", "Curr_Unit_Price"])
df_items["Increase (%)"] = ((df_items["Curr_Unit_Price"] - df_items["Hist_Unit_Price"]) / df_items["Hist_Unit_Price"]) * 100

# Save item-wise purchase data
df_items.to_csv("itemwise_purchase_data.csv", index=False)

# Step 2: Vendor Summary
df_summary = df_items.groupby("Vendor").agg({
    "Hist_Unit_Price": "sum",
    "Curr_Unit_Price": "sum"
}).reset_index()

df_summary.rename(columns={
    "Hist_Unit_Price": "Total_Hist_Spend",
    "Curr_Unit_Price": "Total_Curr_Spend"
}, inplace=True)

df_summary["Profit_Margin (%)"] = ((df_summary["Total_Curr_Spend"] - df_summary["Total_Hist_Spend"]) / df_summary["Total_Hist_Spend"]) * 100
df_summary["Rule_Trusted"] = df_summary["Profit_Margin (%)"].apply(lambda x: "Trusted" if x <= 15 else "Not Trusted")

# Step 3: Decision Tree Classifier
df_summary["Label"] = df_summary["Profit_Margin (%)"].apply(lambda x: 1 if x <= 15 else 0)
X = df_summary[["Profit_Margin (%)"]]
y = df_summary["Label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
clf = DecisionTreeClassifier(max_depth=3, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print("Decision Tree Report:\n", classification_report(y_test, y_pred))
print("Accuracy:", accuracy_score(y_test, y_pred))

df_summary["DT_Label"] = clf.predict(X)
df_summary["DT_Trusted"] = df_summary["DT_Label"].map({1: "Trusted", 0: "Not Trusted"})

# Step 4: Anomaly Detection
iso = IsolationForest(contamination=0.2, random_state=42)
df_summary["Anomaly_Flag"] = iso.fit_predict(df_summary[["Profit_Margin (%)"]])
df_summary["Anomaly"] = df_summary["Anomaly_Flag"].map({1: "Normal", -1: "Anomaly"})

# Final trust decision (combine both methods)
df_summary["Final_Trusted"] = df_summary.apply(
    lambda row: "Trusted" if row["DT_Trusted"] == "Trusted" and row["Anomaly"] == "Normal" else "Not Trusted",
    axis=1
)

# Save summary
df_summary.to_csv("vendor_summary_final.csv", index=False)

# Step 5: Visualizations
sns.set(style="whitegrid")

# Plot 1: Item price increases
plt.figure(figsize=(14, 6))
sns.barplot(data=df_items, x="Item", y="Increase (%)", hue="Category", dodge=False)
plt.title("Item-wise Price Increase (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("static/plot_itemwise_increase.png")
plt.close()

# Plot 2: Vendor profit margins and final trust
plt.figure(figsize=(10, 6))
sns.barplot(data=df_summary, x="Vendor", y="Profit_Margin (%)", hue="Final_Trusted")
plt.axhline(15, color="red", linestyle="-", label="15% Threshold")
plt.title("Vendor Profit Margins with Final Trust Status")
plt.legend()
plt.tight_layout()
plt.savefig("static/plot_vendor_trust.png")
plt.close()

# Plot 3: Anomaly detection
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_summary, x="Vendor", y="Profit_Margin (%)", hue="Anomaly", s=100)
plt.title("Anomaly Detection in Vendor Profit Margins")
plt.axhline(15, color="gray", linestyle="--")
plt.tight_layout()
plt.savefig("static/plot_anomalies.png")
plt.close()

# Plot 4: Decision Tree visualization
plt.figure(figsize=(10, 6))
plot_tree(clf, feature_names=["Profit_Margin (%)"], class_names=["Not Trusted", "Trusted"], filled=True)
plt.title("Decision Tree for Trust Classification")
plt.savefig("static/decision_tree_structure.png")
plt.close()

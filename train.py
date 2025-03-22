# PySpark Notebook for Demand Forecasting

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, mean, when
from pyspark.ml.feature import VectorAssembler, StandardScaler, StringIndexer
from pyspark.ml.regression import GBTRegressor
from pyspark.ml.evaluation import RegressionEvaluator

# Initialize Spark Session
spark = SparkSession.builder.appName("DemandForecasting").getOrCreate()

# Load dataset
data_path = "dbfs:/mnt/data/smart_supply_dataset_with_predictions.csv"  # Adjust for Databricks
raw_df = spark.read.csv(data_path, header=True, inferSchema=True)

# Handle missing values (impute with mean for numerical columns)
for column in raw_df.columns:
    if raw_df.select(column).dtypes[0][1] in ['int', 'double']:
        mean_value = raw_df.select(mean(col(column))).collect()[0][0]
        raw_df = raw_df.fillna({column: mean_value})

# Encode categorical columns (if any)
categorical_columns = [col for col in raw_df.columns if raw_df.select(col).dtypes[0][1] == 'string']
for cat_col in categorical_columns:
    indexer = StringIndexer(inputCol=cat_col, outputCol=cat_col + "_index")
    raw_df = indexer.fit(raw_df).transform(raw_df)
    raw_df = raw_df.drop(cat_col)

# Drop unnecessary columns and define feature columns
target_column = "predicted_demand"
feature_columns = [col for col in raw_df.columns if col not in [target_column, "recommended_stock", "risk_alert"]]

# Assemble features
assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
data = assembler.transform(raw_df)

# Standardize features
scaler = StandardScaler(inputCol="features", outputCol="scaledFeatures")
data = scaler.fit(data).transform(data)

# Split data into training and testing sets
train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)

# Train Gradient Boosted Trees (GBT) model
gbt = GBTRegressor(featuresCol="scaledFeatures", labelCol=target_column, maxIter=50)
model = gbt.fit(train_data)

# Make predictions
predictions = model.transform(test_data)

# Evaluate model
evaluator = RegressionEvaluator(labelCol=target_column, predictionCol="prediction", metricName="rmse")
rmse = evaluator.evaluate(predictions)
print(f"Root Mean Squared Error (RMSE): {rmse}")

# Show sample predictions
predictions.select("prediction", target_column).show(10)

# Save model
model.write().overwrite().save("dbfs:/mnt/models/demand_forecast_model")

# Save predictions
dest_path = "dbfs:/mnt/data/demand_forecast_predictions.csv"
predictions.select("prediction", target_column).write.mode("overwrite").csv(dest_path, header=True)

print(f"Predictions saved to {dest_path}")

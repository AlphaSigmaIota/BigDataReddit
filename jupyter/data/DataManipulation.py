# Autoren AS & HS

from pyspark.sql import SparkSession
import datetime

# AS
TOPIC = "reddit_messages"
APP_NAME = "KafkaDataFetch"

# Spark Session aufbauen (Netzwerk: local)
spark = SparkSession.builder \
    .master("local[*]") \
    .appName(APP_NAME) \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1") \
    .getOrCreate()


# HS
# Code für die Datenverarbeitung bevor es ins HDFS gespeichert wird...
def data_manipulation(df, epoch_id):
    pass


# AS - Methode zum Schreiben der gelesenen Daten in das Hadoop-Verzeichnis "redidits"
def write_to_hadoop(df, epoch_id):
    data_manipulation(df, epoch_id)
    # Speichern Sie das DataFrame als CSV in Hadoop.
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"hdfs://namenode:9000/reddits/data_{date_str}.csv"

    # Speichern Sie das DataFrame als CSV in Hadoop.
    df.write.csv(filename, mode="append")

# Verbindung zum Kafka Topic für das Lesen der Daten:
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafkaConsumer.pollTimeoutMs", 60*60*1000) \
    .option("kafka.bootstrap.servers", "kafka-broker:9092") \
    .option("startingOffsets", "earliest") \
    .option("subscribe", TOPIC) \
    .load()

# Konvertierung der Ausagabe aus Kafka in einen String
df = df.selectExpr("CAST(value AS STRING)")
# Verarbeitungsquery aufbauen und für jeden eingelesenen "batch" Kafka-Messages die Methode "write_to_hadoop" aufrufen
query = df.writeStream.foreachBatch(write_to_hadoop).start()
# Solange auf Kafka hören, bis der Abbruch kommt.
query.awaitTermination()

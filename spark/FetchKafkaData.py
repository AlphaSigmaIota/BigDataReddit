# Autor: AS

PATH_OFFSETS = "hdfs://localhost:9000/path/to/save/offsets"
PATH_MODEL = "hdfs://localhost:9000/path/to/save/model"
APP_NAME = "KafkaDataFetch"
TOPIC = "twitter_messages"

from pyspark.sql import SparkSession
from pyspark.ml.feature import CountVectorizer, Tokenizer
from pyspark.ml.clustering import LDA


def load_offsets_from_storage(spark):
    # Laden der Offsets
    offsets_df = spark.read \
        .format("parquet") \
        .load(PATH_OFFSETS)

    # Konvertieren Sie das DataFrame in ein Format, das von Spark Streaming akzeptiert wird
    offsets = {}
    for row in offsets_df.collect():
        topic_partition = {"topic": row.topic, "partition": row.partition}
        if topic_partition not in offsets:
            offsets[topic_partition] = row.offset
        else:
            # Höchsten Offset für jedes Topic ermitteln
            offsets[topic_partition] = max(offsets[topic_partition], row.offset)

    # Dictionary zu String
    offsets_str = str(offsets).replace("'", '"')

    return offsets_str


def save_offsets_to_storage(df):
    # Konvertierung des DataFrames in HDFS Format
    offsets_df = df.selectExpr("CAST(topic AS STRING)", "CAST(partition AS INT)", "CAST(offset AS LONG)")

    # Schreibe Daten ins HDFS
    offsets_df.write \
        .format("parquet") \
        .mode("overwrite") \
        .save(PATH_OFFSETS)


def fetch_kafka_data():
    # SparkSession
    spark = SparkSession \
        .builder \
        .appName(APP_NAME) \
        .getOrCreate()

    # Laden Sie den gespeicherten Offset
    startingOffsets = load_offsets_from_storage(spark)

    # Definieren Sie den Kafka-Stream
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", TOPIC) \
        .option("startingOffsets", startingOffsets) \
        .load()

    # Speichern des Offsets nach dem Lesen
    df.writeStream \
        .outputMode("append") \
        .foreachBatch(save_offsets_to_storage) \
        .start() \
        .awaitTermination()

    # Konvertierung der Nachricht
    df = df.selectExpr("CAST(value AS STRING)")

    # Tokenisieren Sie die Nachrichten
    tokenizer = Tokenizer(inputCol="value", outputCol="words")
    wordsData = tokenizer.transform(df)

    # Wenden Sie CountVectorizer an, um die Token zu Feature Vektoren zu machen
    cv = CountVectorizer(inputCol="words", outputCol="features")
    model = cv.fit(wordsData)
    result = model.transform(wordsData)

    # Wenden Sie LDA an
    lda = LDA(k=10, maxIter=10)
    ldaModel = lda.fit(result)

    # Schreiben Sie das Modell nach Hadoop
    ldaModel.write().overwrite().save(PATH_MODEL)


if __name__ == "__main__":
    while True:
        fetch_kafka_data()

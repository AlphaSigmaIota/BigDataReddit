# Autor AS
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StringType
from pyspark.sql.functions import udf

import datetime
import json
import re
import nltk
from nltk.corpus import stopwords

# Laden der Ressourcen
nltk.download('punkt')
nltk.download('stopwords')

# Konvertieren der Stoppwörter in eine Liste
stopWords = list(stopwords.words('english'))

# Konstanten
TOPIC = "reddit_messages"
APP_NAME = "KafkaDataFetch"
DATA_ATTRIBUTES_FOR_CLEANUP = ["Titel", "Inhalt"]

# Spark Session aufbauen (Netzwerk: local)
spark = SparkSession.builder \
    .master("local[*]") \
    .appName(APP_NAME) \
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1") \
    .getOrCreate()


# Datenmanipulationen vor dem Speichern
def data_manipulation(df, epoch_id):
    new_df = df

    # neues Dataframe mit den Werten erstellen und zurück liefern
    # für die Persistierung
    manipulate_text_udf = udf(manipulate_text, StringType())
    new_df = new_df.withColumn("value", manipulate_text_udf(col("value")))

    return new_df


# Textmanipulation für die Werte "Titel" und "Inhalt"
def manipulate_text(value):
    data = json.loads(value)

    for data_attr in DATA_ATTRIBUTES_FOR_CLEANUP:
        text = data[data_attr]
        text = remove_whitespace(text)
        text = remove_special_characters(text)
        text = lower_case(text)
        text = remove_links(text)
        text = tokenize(text)
        data[data_attr] = remove_stopwords(text)
    return json.dumps(data)


# Entfernen unnötiger Leerzeichen
def remove_whitespace(text):
    text = text.replace('\r', ' ')
    return text.replace('\n', ' ')


# Entfernen von Sonderzeichen
def remove_special_characters(text):
    return re.sub('[^a-zA-z0-9\s]', '', text)


# Entfernen der Links
def remove_links(text):
    pattern = r"http\S+|www\S+"
    return re.sub(pattern, "", text)


# Alles in Kleinschreibung umwandeln
def lower_case(text):
    return text.lower()


# ggf. tokenizen, aber nur wenn topic modelling etc. gemacht wird,
# nicht wenn Q&A bestehen bleibt
def tokenize(text):
    wordTokens = nltk.word_tokenize(text)
    return " ".join([token for token in wordTokens])


# Stoppwörter entferenn
def remove_stopwords(text):
    wordTokens = nltk.word_tokenize(text)
    return " ".join([word for word in wordTokens if word not in stopWords])


# Methode zum Schreiben der gelesenen Daten in die Hadoop-Verzeichnisse
# "redidits" und "reddits_manipulated"
def write_to_hadoop(df, epoch_id):
    df_raw = df
    df_mani = data_manipulation(df, epoch_id)

    # Datumsstring für heutiges Datum (Start Datum des Jobs)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    # Speicherorte für raw Data und manipulierte Daten
    fn_raw = f"hdfs://namenode:9000/reddits/data_{date_str}.csv"
    fn_mani = f"hdfs://namenode:9000/reddits_manipulated/data_{date_str}.csv"

    # Speichern der DataFrame als CSV in Hadoop.
    df_raw.write.csv(fn_raw, mode="append")
    df_mani.write.csv(fn_mani, mode="append")


if __name__ == "__main__":
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
    # Verarbeitungsquery aufbauen und für jeden eingelesenen "batch"
    # Kafka-Messages die Methode "write_to_hadoop" aufrufen
    query = df.writeStream.foreachBatch(write_to_hadoop).start()
    # Solange auf Kafka hören, bis der Abbruch kommt.
    query.awaitTermination()

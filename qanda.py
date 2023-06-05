from confluent_kafka import Consumer

# Kafka-Verbindungskonfiguration
bootstrap_servers = 'localhost:9092'
topic = 'reddit_messages'

# Kafka Consumer-Konfiguration
consumer_config = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': 'project_dml93',
    'auto.offset.reset': 'earliest'
}

# Erstelle den Kafka Consumer
consumer = Consumer(consumer_config)

# Abonniere das Topic
consumer.subscribe([topic])

messages = []

# Verarbeite die Nachrichten
while True:
    msg = consumer.poll(1.0)  # Warte auf neue Nachrichten für 1 Sekunde

    if msg is None:
        continue
    if msg.error():
        print(f'Kafka Fehler: {msg.error()}')
        continue

    # Verarbeite die empfangene Nachricht
    message_value = msg.value().decode('utf-8')
    messages.append(message_value)
    print(f'Empfangene Nachricht: {message_value}')
    print(len(messages))
    if len(messages) > 50:
        break

joined_messages = "".join(messages)

from transformers import pipeline
oracle = pipeline("question-answering")

print(oracle(question="What sports event is happening right now?", context=joined_messages))


# Schließe den Kafka Consumer
consumer.close()
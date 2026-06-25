This package contains the Solace Messaging API for Python.

The Solace Messaging API for Python is developed and supported by the Solace Corporation.

The API provides access to Solace Messaging Service, supporting a variety of Message Exchange Patterns.

# Installation

Install the API using pip: ```pip install solace-pubsubplus```

# Dependencies

Solace Messaging API for Python requires Python 3.6 or greater.

# Documentation

An online reference for the API is available at [docs.solace.com](https://docs.solace.com/API/Messaging-APIs/Python-API/python-home.htm).

# Introduction

There are four primary objects in the Solace Messaging API for Python that applications can use, which
are as follows:

## MessagingService

```from solace.messaging.messaging_service import MessagingService```
The starting point for all client-broker connections.  `MessagingService` defines and controls the connection to the Solace Event Broker.

A `MessagingService` object is created by the `MessagingServiceBuilder`.

## MessagePublisher
```from solace.messaging.publisher.message_publisher import MessagePublisher```
The abstract base class for a Message Publisher (`MessagePublisher`).  Applications do not build `MessagePublisher` objects directly, rather an application will invoke a builder.
for one of two derived objects:
1. `DirectMessagePublisher`:  Created by a `DirectMessagePublisherBuilder`.  `DirectMessagePublisher` send messages that are not acknowledged and are not stored on the Solace Event Broker. This is the fastest delivery path because messages are never queued and therefore cannot be delivered to offline `MessageReceiver` at a later time.  Messages published by `DirectMessagePublisher` are eligible for discard when network congestion occurs.
2. `PersistentMessagePublisher`:  Created by a `PersistentMessagePublisherBuilder`.  `PersistentMessagePublisher` sends messages that are guaranteed to be delivered to `MessageReceiver`, even if the `MessageReceiver` object is offline. Solace Event Broker stores the messages until they are delivered
    and consumed by all subscribing receivers.

## MessageReceiver
```from solace.messaging.receiver.message_receiver import MessageReceiver```
The abstract base class for a Message Receiver (`Message Receiver`).  Applications do not build `MessageReceiver` objects directly, rather an application will invoke a builder for one of two derived objects:
1. `DirectMessageReceiver`: Created by a `DirectMessageReceiverBuilder`.  `DirectMessgeReceiver` consumes messages as they are published. `DirectMessageReceiver` will not receive messages published before the receiver is created or while the receiver is offline.  `DirectMessageReceiver` is not required to acknowledge received messages.
`DirectMessageReceiver` may receive messages from any publisher (persistent or direct), but only while the `DirectMessageReceiver` is online.
2. `PersistentMessageReceiver`: Created by a `PersistentMessageReceiverBuilder`.  `PersistentMessageReceiver` consume messages from a queue created on the Solace Event broker.
When the queue is created and subscriptions applied, it will begin storing messages, even if `PersistentMessageReceiver` is offline. Messages are stored until delivered
to the `PersistentMessageReceiver` and the `PersistentMessageReceiver` acknowledges the message. `PersistentMessageReceiver`  is responsible for acknowledging messages received to
remove them from the Solace Event Broker Queue.
## Message
```from solace.messaging.core.message import Message```
The abstract base class for a `Message`.  Applications do not build a `Message` object directly, rather an application will invoke a builder for an `OutboundMessage` (for publish) or
receive an `InboundMessage` (from a `MessageReceiver`).

# Samples

Sample applications are available at the [Solace Developer Community](https://github.com/SolaceSamples/solace-samples-python)

# multiprocessing

Solace Messaging API for Python cannot be used in applications that use the Python multiprocessing module.

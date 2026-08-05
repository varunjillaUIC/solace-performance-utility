
# # # # # # import time
# # # # # # import threading
# # # # # # import random
# # # # # # import string
# # # # # # from solace.messaging.resources.topic import Topic
# # # # # # from solace.messaging.resources.topic_subscription import TopicSubscription
# # # # # # from solace.messaging.resources.queue import Queue


# # # # # # def build_message(template: str, index: int, size: int) -> str:
# # # # # #     if not template.strip():
# # # # # #         return "X" * size
# # # # # #     msg = template
# # # # # #     msg = msg.replace("{{index}}", str(index))
# # # # # #     msg = msg.replace("{{timestamp}}", str(round(time.time() * 1000)))
# # # # # #     msg = msg.replace("{{random}}", ''.join(random.choices(string.ascii_letters, k=8)))
# # # # # #     return msg


# # # # # # class PerfTester:

# # # # # #     def __init__(self, service):
# # # # # #         self.service = service
# # # # # #         self.results = {}
# # # # # #         self._stop = False

# # # # # #     def stop(self):
# # # # # #         self._stop = True

# # # # # #     def run(
# # # # # #         self,
# # # # # #         target: str,
# # # # # #         target_type: str,            # "topic" or "queue"
# # # # # #         message_count: int,
# # # # # #         message_size: int,
# # # # # #         message_template: str,
# # # # # #         delivery_mode: str = "direct",   # "direct" or "persistent"
# # # # # #         rate_limit: int = 0,             # msgs/sec, 0 = unlimited
# # # # # #         window_size: int = 50,           # only used for persistent mode
# # # # # #         on_progress=None
# # # # # #     ):
# # # # # #         self._stop = False
# # # # # #         latencies = []
# # # # # #         received_count = [0]
# # # # # #         errors = [0]
# # # # # #         throughput_samples = []

# # # # # #         # --- Build publisher based on delivery mode ---
# # # # # #         if delivery_mode == "persistent":
# # # # # #             try:
# # # # # #                 from solace.messaging.config.solace_properties.publisher_properties import (
# # # # # #                     PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE
# # # # # #                 )
# # # # # #                 pub_builder = self.service.create_persistent_message_publisher_builder()
# # # # # #                 pub_builder = pub_builder.from_properties({
# # # # # #                     PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE: window_size
# # # # # #                 })
# # # # # #                 publisher = pub_builder.build()
# # # # # #             except Exception:
# # # # # #                 # Fallback if window size property import fails on this SDK version
# # # # # #                 publisher = self.service.create_persistent_message_publisher_builder().build()
# # # # # #         else:
# # # # # #             publisher = self.service.create_direct_message_publisher_builder().build()

# # # # # #         publisher.start()

# # # # # #         # --- Build receiver based on target type ---
# # # # # #         if target_type == "topic":
# # # # # #             receiver = self.service.create_direct_message_receiver_builder() \
# # # # # #                 .with_subscriptions([TopicSubscription.of(target)]) \
# # # # # #                 .build()
# # # # # #             receiver.start()
# # # # # #             is_persistent_receiver = False
# # # # # #         else:
# # # # # #             queue = Queue.durable_exclusive_queue(target)
# # # # # #             receiver = self.service.create_persistent_message_receiver_builder() \
# # # # # #                 .build(queue)
# # # # # #             receiver.start()
# # # # # #             is_persistent_receiver = True

# # # # # #         start_time = time.time()
# # # # # #         last_sample_time = start_time
# # # # # #         last_sample_count = 0

# # # # # #         # --- Publish in background thread, with optional rate limiting ---
# # # # # #         def publish_messages():
# # # # # #             topic_obj = Topic.of(target)
# # # # # #             delay = (1.0 / rate_limit) if rate_limit > 0 else 0
# # # # # #             for i in range(message_count):
# # # # # #                 if self._stop:
# # # # # #                     break
# # # # # #                 try:
# # # # # #                     payload = build_message(message_template, i, message_size)
# # # # # #                     stamped = f"{time.time()}||{payload}"
# # # # # #                     msg = self.service.message_builder().build(stamped)
# # # # # #                     publisher.publish(msg, topic_obj)
# # # # # #                 except Exception:
# # # # # #                     errors[0] += 1
# # # # # #                 if delay > 0:
# # # # # #                     time.sleep(delay)

# # # # # #         pub_thread = threading.Thread(target=publish_messages)
# # # # # #         pub_thread.start()

# # # # # #         # --- Receive loop ---
# # # # # #         deadline = time.time() + 90
# # # # # #         while received_count[0] < message_count and time.time() < deadline and not self._stop:
# # # # # #             try:
# # # # # #                 msg = receiver.receive_message(timeout=2000)
# # # # # #                 if msg:
# # # # # #                     raw = msg.get_payload_as_string() or ""
# # # # # #                     if is_persistent_receiver:
# # # # # #                         receiver.ack(msg)
# # # # # #                     try:
# # # # # #                         sent_time = float(raw.split("||")[0])
# # # # # #                         latency_ms = (time.time() - sent_time) * 1000
# # # # # #                         latencies.append(latency_ms)
# # # # # #                     except Exception:
# # # # # #                         pass
# # # # # #                     received_count[0] += 1

# # # # # #                     now = time.time()
# # # # # #                     if now - last_sample_time >= 1.0:
# # # # # #                         sample_tps = (received_count[0] - last_sample_count) / (now - last_sample_time)
# # # # # #                         throughput_samples.append(round(sample_tps, 1))
# # # # # #                         last_sample_time = now
# # # # # #                         last_sample_count = received_count[0]

# # # # # #                     if on_progress:
# # # # # #                         elapsed = time.time() - start_time
# # # # # #                         tps = received_count[0] / elapsed if elapsed > 0 else 0
# # # # # #                         on_progress(
# # # # # #                             received_count[0], message_count,
# # # # # #                             round(elapsed, 1), round(tps, 1)
# # # # # #                         )
# # # # # #             except Exception:
# # # # # #                 pass

# # # # # #         pub_thread.join()

# # # # # #         try:
# # # # # #             publisher.terminate()
# # # # # #         except Exception:
# # # # # #             pass
# # # # # #         try:
# # # # # #             receiver.terminate()
# # # # # #         except Exception:
# # # # # #             pass

# # # # # #         total_time = time.time() - start_time
# # # # # #         sorted_lat = sorted(latencies)

# # # # # #         self.results = {
# # # # # #             "target": target,
# # # # # #             "target_type": target_type,
# # # # # #             "delivery_mode": delivery_mode,
# # # # # #             "rate_limit": rate_limit,
# # # # # #             "window_size": window_size if delivery_mode == "persistent" else None,
# # # # # #             "message_count": message_count,
# # # # # #             "message_size_bytes": message_size,
# # # # # #             "sent": message_count - errors[0],
# # # # # #             "received": received_count[0],
# # # # # #             "errors": errors[0],
# # # # # #             "total_time_sec": round(total_time, 2),
# # # # # #             "throughput_msg_per_sec": round(
# # # # # #                 received_count[0] / total_time if total_time > 0 else 0, 2
# # # # # #             ),
# # # # # #             "avg_latency_ms": round(
# # # # # #                 sum(latencies) / len(latencies), 2
# # # # # #             ) if latencies else 0,
# # # # # #             "min_latency_ms": round(min(latencies), 2) if latencies else 0,
# # # # # #             "max_latency_ms": round(max(latencies), 2) if latencies else 0,
# # # # # #             "p95_latency_ms": round(
# # # # # #                 sorted_lat[int(len(sorted_lat) * 0.95)], 2
# # # # # #             ) if sorted_lat else 0,
# # # # # #             "p99_latency_ms": round(
# # # # # #                 sorted_lat[int(len(sorted_lat) * 0.99)], 2
# # # # # #             ) if sorted_lat else 0,
# # # # # #             "throughput_samples": throughput_samples,
# # # # # #         }

# # # # # #         return self.results


# # # # # # import time
# # # # # # import threading
# # # # # # import random
# # # # # # import string
# # # # # # from solace.messaging.resources.topic import Topic
# # # # # # from solace.messaging.resources.topic_subscription import TopicSubscription
# # # # # # from solace.messaging.resources.queue import Queue


# # # # # # def build_message(template: str, index: int, size: int) -> str:
# # # # # #     if template.startswith("__fixed__"):
# # # # # #         return template[len("__fixed__"):]
# # # # # #     if not template.strip():
# # # # # #         return "X" * size
# # # # # #     msg = template
# # # # # #     msg = msg.replace("{{index}}", str(index))
# # # # # #     msg = msg.replace("{{timestamp}}", str(round(time.time() * 1000)))
# # # # # #     msg = msg.replace("{{random}}", ''.join(random.choices(string.ascii_letters, k=8)))
# # # # # #     return msg


# # # # # # class PerfTester:

# # # # # #     def __init__(self, service):
# # # # # #         self.service = service
# # # # # #         self.results = {}
# # # # # #         self._stop = False

# # # # # #     def stop(self):
# # # # # #         self._stop = True

# # # # # #     def run(
# # # # # #         self,
# # # # # #         target: str,
# # # # # #         target_type: str,
# # # # # #         message_count: int,
# # # # # #         message_size: int,
# # # # # #         message_template: str,
# # # # # #         delivery_mode: str = "direct",
# # # # # #         rate_limit: int = 0,
# # # # # #         window_size: int = 50,
# # # # # #         queue_type: str = "exclusive",
# # # # # #         warmup_count: int = 0,
# # # # # #         consumer_count: int = 1,        # ← NEW
# # # # # #         on_progress=None
# # # # # #     ):
# # # # # #         self._stop = False
# # # # # #         latencies = []
# # # # # #         received_count = [0]
# # # # # #         errors = [0]
# # # # # #         throughput_samples = []
# # # # # #         warmup_latencies = []
# # # # # #         lock = threading.Lock()         # ← thread-safe counter for multi-consumer

# # # # # #         # --- Build publisher ---
# # # # # #         if delivery_mode == "persistent":
# # # # # #             try:
# # # # # #                 from solace.messaging.config.solace_properties.publisher_properties import (
# # # # # #                     PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE
# # # # # #                 )
# # # # # #                 pub_builder = self.service \
# # # # # #                     .create_persistent_message_publisher_builder()
# # # # # #                 pub_builder = pub_builder.from_properties({
# # # # # #                     PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE: window_size
# # # # # #                 })
# # # # # #                 publisher = pub_builder.build()
# # # # # #             except Exception:
# # # # # #                 publisher = self.service \
# # # # # #                     .create_persistent_message_publisher_builder().build()
# # # # # #         else:
# # # # # #             publisher = self.service \
# # # # # #                 .create_direct_message_publisher_builder().build()

# # # # # #         publisher.start()

# # # # # #         # --- Build receivers ---
# # # # # #         # For topic: always 1 receiver (direct messaging)
# # # # # #         # For exclusive queue: always 1 receiver (only 1 allowed active)
# # # # # #         # For non-exclusive queue: consumer_count receivers (round-robin)

# # # # # #         receivers = []

# # # # # #         if target_type == "topic":
# # # # # #             receiver = self.service \
# # # # # #                 .create_direct_message_receiver_builder() \
# # # # # #                 .with_subscriptions([TopicSubscription.of(target)]) \
# # # # # #                 .build()
# # # # # #             receiver.start()
# # # # # #             receivers = [receiver]
# # # # # #             is_persistent_receiver = False

# # # # # #         else:
# # # # # #             # Exclusive always gets 1 consumer regardless of consumer_count setting
# # # # # #             actual_consumer_count = 1 if queue_type == "exclusive" else max(1, consumer_count)

# # # # # #             if queue_type == "non_exclusive":
# # # # # #                 queue = Queue.durable_non_exclusive_queue(target)
# # # # # #             else:
# # # # # #                 queue = Queue.durable_exclusive_queue(target)

# # # # # #             for _ in range(actual_consumer_count):
# # # # # #                 r = self.service \
# # # # # #                     .create_persistent_message_receiver_builder() \
# # # # # #                     .build(queue)
# # # # # #                 r.start()
# # # # # #                 receivers.append(r)

# # # # # #             is_persistent_receiver = True

# # # # # #         start_time = time.time()
# # # # # #         last_sample_time = start_time
# # # # # #         last_sample_count = 0

# # # # # #         # --- Publish thread ---
# # # # # #         def publish_messages():
# # # # # #             topic_obj = Topic.of(target)
# # # # # #             delay = (1.0 / rate_limit) if rate_limit > 0 else 0
# # # # # #             for i in range(message_count):
# # # # # #                 if self._stop:
# # # # # #                     break
# # # # # #                 try:
# # # # # #                     payload = build_message(message_template, i, message_size)
# # # # # #                     stamped = f"{time.time()}||{payload}"
# # # # # #                     msg = self.service.message_builder().build(stamped)
# # # # # #                     publisher.publish(msg, topic_obj)
# # # # # #                 except Exception:
# # # # # #                     errors[0] += 1
# # # # # #                 if delay > 0:
# # # # # #                     time.sleep(delay)

# # # # # #         pub_thread = threading.Thread(target=publish_messages, daemon=True)
# # # # # #         pub_thread.start()

# # # # # #         # --- Per-receiver threads for non-exclusive multi-consumer ---
# # # # # #         def receive_loop(receiver):
# # # # # #             while (
# # # # # #                 received_count[0] < message_count
# # # # # #                 and time.time() < deadline
# # # # # #                 and not self._stop
# # # # # #             ):
# # # # # #                 try:
# # # # # #                     msg = receiver.receive_message(timeout=2000)
# # # # # #                     if msg:
# # # # # #                         raw = msg.get_payload_as_string() or ""
# # # # # #                         if is_persistent_receiver:
# # # # # #                             receiver.ack(msg)

# # # # # #                         try:
# # # # # #                             sent_time = float(raw.split("||")[0])
# # # # # #                             latency_ms = (time.time() - sent_time) * 1000

# # # # # #                             with lock:
# # # # # #                                 if received_count[0] < warmup_count:
# # # # # #                                     warmup_latencies.append(latency_ms)
# # # # # #                                 else:
# # # # # #                                     latencies.append(latency_ms)
# # # # # #                                 received_count[0] += 1

# # # # # #                                 # Throughput sample every second
# # # # # #                                 now = time.time()
# # # # # #                                 if now - last_sample_time >= 1.0:
# # # # # #                                     pass  # handled in main thread

# # # # # #                         except Exception:
# # # # # #                             pass
# # # # # #                 except Exception:
# # # # # #                     pass

# # # # # #         deadline = time.time() + 90

# # # # # #         if len(receivers) == 1:
# # # # # #             # Single receiver — run in main thread (original behavior)
# # # # # #             while (
# # # # # #                 received_count[0] < message_count
# # # # # #                 and time.time() < deadline
# # # # # #                 and not self._stop
# # # # # #             ):
# # # # # #                 try:
# # # # # #                     msg = receivers[0].receive_message(timeout=2000)
# # # # # #                     if msg:
# # # # # #                         raw = msg.get_payload_as_string() or ""
# # # # # #                         if is_persistent_receiver:
# # # # # #                             receivers[0].ack(msg)
# # # # # #                         try:
# # # # # #                             sent_time = float(raw.split("||")[0])
# # # # # #                             latency_ms = (time.time() - sent_time) * 1000
# # # # # #                             if received_count[0] < warmup_count:
# # # # # #                                 warmup_latencies.append(latency_ms)
# # # # # #                             else:
# # # # # #                                 latencies.append(latency_ms)
# # # # # #                         except Exception:
# # # # # #                             pass
# # # # # #                         received_count[0] += 1

# # # # # #                         now = time.time()
# # # # # #                         if now - last_sample_time >= 1.0:
# # # # # #                             sample_tps = (
# # # # # #                                 (received_count[0] - last_sample_count)
# # # # # #                                 / (now - last_sample_time)
# # # # # #                             )
# # # # # #                             throughput_samples.append(round(sample_tps, 1))
# # # # # #                             last_sample_time = now
# # # # # #                             last_sample_count = received_count[0]

# # # # # #                         if on_progress:
# # # # # #                             elapsed = time.time() - start_time
# # # # # #                             tps = received_count[0] / elapsed if elapsed > 0 else 0
# # # # # #                             on_progress(
# # # # # #                                 received_count[0], message_count,
# # # # # #                                 round(elapsed, 1), round(tps, 1)
# # # # # #                             )
# # # # # #                 except Exception:
# # # # # #                     pass

# # # # # #         else:
# # # # # #             # Multiple receivers — each in its own thread
# # # # # #             recv_threads = []
# # # # # #             for r in receivers:
# # # # # #                 t = threading.Thread(target=receive_loop, args=(r,), daemon=True)
# # # # # #                 t.start()
# # # # # #                 recv_threads.append(t)

# # # # # #             # Progress reporting in main thread
# # # # # #             while (
# # # # # #                 received_count[0] < message_count
# # # # # #                 and time.time() < deadline
# # # # # #                 and not self._stop
# # # # # #             ):
# # # # # #                 time.sleep(0.1)

# # # # # #                 now = time.time()
# # # # # #                 if now - last_sample_time >= 1.0:
# # # # # #                     with lock:
# # # # # #                         sample_tps = (
# # # # # #                             (received_count[0] - last_sample_count)
# # # # # #                             / (now - last_sample_time)
# # # # # #                         )
# # # # # #                         throughput_samples.append(round(sample_tps, 1))
# # # # # #                         last_sample_time = now
# # # # # #                         last_sample_count = received_count[0]

# # # # # #                 if on_progress:
# # # # # #                     elapsed = time.time() - start_time
# # # # # #                     tps = received_count[0] / elapsed if elapsed > 0 else 0
# # # # # #                     on_progress(
# # # # # #                         received_count[0], message_count,
# # # # # #                         round(elapsed, 1), round(tps, 1)
# # # # # #                     )

# # # # # #             for t in recv_threads:
# # # # # #                 t.join(timeout=5)

# # # # # #         pub_thread.join(timeout=10)

# # # # # #         # --- Cleanup ---
# # # # # #         try:
# # # # # #             publisher.terminate()
# # # # # #         except Exception:
# # # # # #             pass
# # # # # #         for r in receivers:
# # # # # #             try:
# # # # # #                 r.terminate()
# # # # # #             except Exception:
# # # # # #                 pass

# # # # # #         total_time = time.time() - start_time
# # # # # #         sorted_lat = sorted(latencies)

# # # # # #         self.results = {
# # # # # #             "target": target,
# # # # # #             "target_type": target_type,
# # # # # #             "queue_type": queue_type if target_type == "queue" else None,
# # # # # #             "consumer_count": len(receivers) if target_type == "queue" else 1,
# # # # # #             "delivery_mode": delivery_mode,
# # # # # #             "rate_limit": rate_limit,
# # # # # #             "window_size": window_size if delivery_mode == "persistent" else None,
# # # # # #             "message_count": message_count,
# # # # # #             "message_size_bytes": message_size,
# # # # # #             "warmup_count": warmup_count,
# # # # # #             "sent": message_count - errors[0],
# # # # # #             "received": received_count[0],
# # # # # #             "errors": errors[0],
# # # # # #             "total_time_sec": round(total_time, 2),
# # # # # #             "throughput_msg_per_sec": round(
# # # # # #                 received_count[0] / total_time if total_time > 0 else 0, 2
# # # # # #             ),
# # # # # #             "avg_latency_ms": round(
# # # # # #                 sum(latencies) / len(latencies), 2
# # # # # #             ) if latencies else 0,
# # # # # #             "min_latency_ms": round(min(latencies), 2) if latencies else 0,
# # # # # #             "max_latency_ms": round(max(latencies), 2) if latencies else 0,
# # # # # #             "p95_latency_ms": round(
# # # # # #                 sorted_lat[int(len(sorted_lat) * 0.95)], 2
# # # # # #             ) if sorted_lat else 0,
# # # # # #             "p99_latency_ms": round(
# # # # # #                 sorted_lat[int(len(sorted_lat) * 0.99)], 2
# # # # # #             ) if sorted_lat else 0,
# # # # # #             "warmup_avg_ms": round(
# # # # # #                 sum(warmup_latencies) / len(warmup_latencies), 2
# # # # # #             ) if warmup_latencies else None,
# # # # # #             "warmup_max_ms": round(
# # # # # #                 max(warmup_latencies), 2
# # # # # #             ) if warmup_latencies else None,
# # # # # #             "throughput_samples": throughput_samples,
# # # # # #         }

# # # # # #         return self.results



# # # # # import time
# # # # # import threading
# # # # # import random
# # # # # import string
# # # # # from solace.messaging.resources.topic import Topic
# # # # # from solace.messaging.resources.topic_subscription import TopicSubscription
# # # # # from solace.messaging.resources.queue import Queue


# # # # # def build_message(template: str, index: int, size: int) -> str:
# # # # #     if template.startswith("__fixed__"):
# # # # #         return template[len("__fixed__"):]
# # # # #     if not template.strip():
# # # # #         return "X" * size
# # # # #     msg = template
# # # # #     msg = msg.replace("{{index}}", str(index))
# # # # #     msg = msg.replace("{{timestamp}}", str(round(time.time() * 1000)))
# # # # #     msg = msg.replace("{{random}}", ''.join(random.choices(string.ascii_letters, k=8)))
# # # # #     return msg


# # # # # class PerfTester:

# # # # #     def __init__(self, service):
# # # # #         self.service = service
# # # # #         self.results = {}
# # # # #         self._stop = False

# # # # #     def stop(self):
# # # # #         self._stop = True

# # # # #     def run(
# # # # #         self,
# # # # #         target: str,
# # # # #         target_type: str,
# # # # #         message_count: int,
# # # # #         message_size: int,
# # # # #         message_template: str,
# # # # #         delivery_mode: str = "direct",
# # # # #         rate_limit: int = 0,
# # # # #         window_size: int = 50,
# # # # #         queue_type: str = "exclusive",
# # # # #         warmup_count: int = 0,
# # # # #         consumer_count: int = 1,
# # # # #         on_progress=None
# # # # #     ):
# # # # #         self._stop = False
# # # # #         latencies = []
# # # # #         received_count = [0]
# # # # #         published_count = [0]
# # # # #         errors = [0]
# # # # #         throughput_samples = []
# # # # #         ingress_samples = []
# # # # #         warmup_latencies = []
# # # # #         lock = threading.Lock()

# # # # #         # Mutable time trackers (use lists so nested functions can mutate)
# # # # #         last_egress_time = [time.time()]
# # # # #         last_egress_count = [0]
# # # # #         last_ingress_time = [time.time()]
# # # # #         last_ingress_count = [0]
# # # # #         last_progress_time = [time.time()]

# # # # #         # --- Build publisher ---
# # # # #         if delivery_mode == "persistent":
# # # # #             try:
# # # # #                 from solace.messaging.config.solace_properties.publisher_properties import (
# # # # #                     PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE
# # # # #                 )
# # # # #                 pub_builder = self.service \
# # # # #                     .create_persistent_message_publisher_builder()
# # # # #                 pub_builder = pub_builder.from_properties({
# # # # #                     PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE: window_size
# # # # #                 })
# # # # #                 publisher = pub_builder.build()
# # # # #             except Exception:
# # # # #                 publisher = self.service \
# # # # #                     .create_persistent_message_publisher_builder().build()
# # # # #         else:
# # # # #             publisher = self.service \
# # # # #                 .create_direct_message_publisher_builder().build()

# # # # #         publisher.start()

# # # # #         # --- Build receivers ---
# # # # #         receivers = []

# # # # #         if target_type == "topic":
# # # # #             receiver = self.service \
# # # # #                 .create_direct_message_receiver_builder() \
# # # # #                 .with_subscriptions([TopicSubscription.of(target)]) \
# # # # #                 .build()
# # # # #             receiver.start()
# # # # #             receivers = [receiver]
# # # # #             is_persistent_receiver = False

# # # # #         else:
# # # # #             actual_count = 1 if queue_type == "exclusive" else max(1, consumer_count)

# # # # #             if queue_type == "non_exclusive":
# # # # #                 queue = Queue.durable_non_exclusive_queue(target)
# # # # #             else:
# # # # #                 queue = Queue.durable_exclusive_queue(target)

# # # # #             for _ in range(actual_count):
# # # # #                 r = self.service \
# # # # #                     .create_persistent_message_receiver_builder() \
# # # # #                     .build(queue)
# # # # #                 r.start()
# # # # #                 receivers.append(r)

# # # # #             is_persistent_receiver = True

# # # # #         start_time = time.time()
# # # # #         deadline = start_time + 120

# # # # #         # --- Publish thread ---
# # # # #         def publish_messages():
# # # # #             # For queue: publish to a topic that the queue subscribes to.
# # # # #             # Use the target name directly as topic — broker must have
# # # # #             # a subscription on the queue matching this topic.
# # # # #             topic_obj = Topic.of(target)
# # # # #             delay = (1.0 / rate_limit) if rate_limit > 0 else 0

# # # # #             for i in range(message_count):
# # # # #                 if self._stop:
# # # # #                     break
# # # # #                 try:
# # # # #                     payload = build_message(message_template, i, message_size)
# # # # #                     stamped = f"{time.time()}||{payload}"
# # # # #                     msg = self.service.message_builder().build(stamped)
# # # # #                     publisher.publish(msg, topic_obj)
# # # # #                     published_count[0] += 1

# # # # #                     # Sample ingress every second
# # # # #                     now = time.time()
# # # # #                     if now - last_ingress_time[0] >= 1.0:
# # # # #                         elapsed = now - last_ingress_time[0]
# # # # #                         delta = published_count[0] - last_ingress_count[0]
# # # # #                         sample = round(delta / elapsed, 1)
# # # # #                         ingress_samples.append(sample)
# # # # #                         last_ingress_time[0] = now
# # # # #                         last_ingress_count[0] = published_count[0]

# # # # #                 except Exception:
# # # # #                     errors[0] += 1

# # # # #                 if delay > 0:
# # # # #                     time.sleep(delay)

# # # # #         pub_thread = threading.Thread(target=publish_messages, daemon=True)
# # # # #         pub_thread.start()

# # # # #         # --- Per-receiver thread for multi-consumer ---
# # # # #         def receive_loop(receiver):
# # # # #             while (
# # # # #                 received_count[0] < message_count
# # # # #                 and time.time() < deadline
# # # # #                 and not self._stop
# # # # #             ):
# # # # #                 try:
# # # # #                     msg = receiver.receive_message(timeout=500)  # short timeout for responsiveness
# # # # #                     if msg:
# # # # #                         raw = msg.get_payload_as_string() or ""
# # # # #                         if is_persistent_receiver:
# # # # #                             receiver.ack(msg)
# # # # #                         try:
# # # # #                             sent_time = float(raw.split("||")[0])
# # # # #                             latency_ms = (time.time() - sent_time) * 1000
# # # # #                             with lock:
# # # # #                                 if received_count[0] < warmup_count:
# # # # #                                     warmup_latencies.append(latency_ms)
# # # # #                                 else:
# # # # #                                     latencies.append(latency_ms)
# # # # #                                 received_count[0] += 1
# # # # #                         except Exception:
# # # # #                             pass
# # # # #                 except Exception:
# # # # #                     pass

# # # # #         # --- Main receive + progress loop ---
# # # # #         def main_receive_loop():
# # # # #             while (
# # # # #                 received_count[0] < message_count
# # # # #                 and time.time() < deadline
# # # # #                 and not self._stop
# # # # #             ):
# # # # #                 try:
# # # # #                     msg = receivers[0].receive_message(timeout=500)  # short timeout!
# # # # #                     if msg:
# # # # #                         raw = msg.get_payload_as_string() or ""
# # # # #                         if is_persistent_receiver:
# # # # #                             receivers[0].ack(msg)
# # # # #                         try:
# # # # #                             sent_time = float(raw.split("||")[0])
# # # # #                             latency_ms = (time.time() - sent_time) * 1000
# # # # #                             if received_count[0] < warmup_count:
# # # # #                                 warmup_latencies.append(latency_ms)
# # # # #                             else:
# # # # #                                 latencies.append(latency_ms)
# # # # #                         except Exception:
# # # # #                             pass
# # # # #                         received_count[0] += 1

# # # # #                         # Sample egress every second
# # # # #                         now = time.time()
# # # # #                         if now - last_egress_time[0] >= 1.0:
# # # # #                             elapsed = now - last_egress_time[0]
# # # # #                             delta = received_count[0] - last_egress_count[0]
# # # # #                             sample = round(delta / elapsed, 1)
# # # # #                             throughput_samples.append(sample)
# # # # #                             last_egress_time[0] = now
# # # # #                             last_egress_count[0] = received_count[0]

# # # # #                 except Exception:
# # # # #                     pass

# # # # #                 # Fire progress every 0.3s regardless of messages
# # # # #                 now = time.time()
# # # # #                 if on_progress and now - last_progress_time[0] >= 0.3:
# # # # #                     elapsed = now - start_time
# # # # #                     egress_tps = round(
# # # # #                         received_count[0] / elapsed if elapsed > 0 else 0, 1
# # # # #                     )
# # # # #                     ingress_tps = ingress_samples[-1] if ingress_samples else round(
# # # # #                         published_count[0] / elapsed if elapsed > 0 else 0, 1
# # # # #                     )
# # # # #                     # Live P99 from current latencies
# # # # #                     live_p99 = 0.0
# # # # #                     if latencies:
# # # # #                         sl = sorted(latencies)
# # # # #                         live_p99 = round(sl[int(len(sl) * 0.99)], 2)

# # # # #                     on_progress(
# # # # #                         received_count[0],
# # # # #                         message_count,
# # # # #                         round(elapsed, 1),
# # # # #                         egress_tps,
# # # # #                         ingress_tps,
# # # # #                         live_p99
# # # # #                     )
# # # # #                     last_progress_time[0] = now

# # # # #         if len(receivers) == 1:
# # # # #             main_receive_loop()
# # # # #         else:
# # # # #             # Multi-receiver — each in own thread
# # # # #             recv_threads = []
# # # # #             for r in receivers:
# # # # #                 t = threading.Thread(target=receive_loop, args=(r,), daemon=True)
# # # # #                 t.start()
# # # # #                 recv_threads.append(t)

# # # # #             # Progress reporting in main thread
# # # # #             while (
# # # # #                 received_count[0] < message_count
# # # # #                 and time.time() < deadline
# # # # #                 and not self._stop
# # # # #             ):
# # # # #                 time.sleep(0.3)
# # # # #                 if on_progress:
# # # # #                     now = time.time()
# # # # #                     elapsed = now - start_time
# # # # #                     egress_tps = round(
# # # # #                         received_count[0] / elapsed if elapsed > 0 else 0, 1
# # # # #                     )
# # # # #                     ingress_tps = ingress_samples[-1] if ingress_samples else round(
# # # # #                         published_count[0] / elapsed if elapsed > 0 else 0, 1
# # # # #                     )
# # # # #                     live_p99 = 0.0
# # # # #                     if latencies:
# # # # #                         sl = sorted(latencies)
# # # # #                         live_p99 = round(sl[int(len(sl) * 0.99)], 2)

# # # # #                     on_progress(
# # # # #                         received_count[0], message_count,
# # # # #                         round(elapsed, 1), egress_tps,
# # # # #                         ingress_tps, live_p99
# # # # #                     )

# # # # #                     now2 = time.time()
# # # # #                     if now2 - last_egress_time[0] >= 1.0:
# # # # #                         with lock:
# # # # #                             elapsed2 = now2 - last_egress_time[0]
# # # # #                             delta = received_count[0] - last_egress_count[0]
# # # # #                             throughput_samples.append(round(delta / elapsed2, 1))
# # # # #                             last_egress_time[0] = now2
# # # # #                             last_egress_count[0] = received_count[0]

# # # # #             for t in recv_threads:
# # # # #                 t.join(timeout=5)

# # # # #         pub_thread.join(timeout=15)

# # # # #         # --- Cleanup ---
# # # # #         try:
# # # # #             publisher.terminate()
# # # # #         except Exception:
# # # # #             pass
# # # # #         for r in receivers:
# # # # #             try:
# # # # #                 r.terminate()
# # # # #             except Exception:
# # # # #                 pass

# # # # #         total_time = time.time() - start_time
# # # # #         sorted_lat = sorted(latencies)

# # # # #         self.results = {
# # # # #             "target": target,
# # # # #             "target_type": target_type,
# # # # #             "queue_type": queue_type if target_type == "queue" else None,
# # # # #             "consumer_count": len(receivers) if target_type == "queue" else 1,
# # # # #             "delivery_mode": delivery_mode,
# # # # #             "rate_limit": rate_limit,
# # # # #             "window_size": window_size if delivery_mode == "persistent" else None,
# # # # #             "message_count": message_count,
# # # # #             "message_size_bytes": message_size,
# # # # #             "warmup_count": warmup_count,
# # # # #             "sent": published_count[0],
# # # # #             "received": received_count[0],
# # # # #             "errors": errors[0],
# # # # #             "total_time_sec": round(total_time, 2),
# # # # #             "throughput_msg_per_sec": round(
# # # # #                 received_count[0] / total_time if total_time > 0 else 0, 2
# # # # #             ),
# # # # #             "avg_latency_ms": round(
# # # # #                 sum(latencies) / len(latencies), 2
# # # # #             ) if latencies else 0,
# # # # #             "min_latency_ms": round(min(latencies), 2) if latencies else 0,
# # # # #             "max_latency_ms": round(max(latencies), 2) if latencies else 0,
# # # # #             "p95_latency_ms": round(
# # # # #                 sorted_lat[int(len(sorted_lat) * 0.95)], 2
# # # # #             ) if sorted_lat else 0,
# # # # #             "p99_latency_ms": round(
# # # # #                 sorted_lat[int(len(sorted_lat) * 0.99)], 2
# # # # #             ) if sorted_lat else 0,
# # # # #             "warmup_avg_ms": round(
# # # # #                 sum(warmup_latencies) / len(warmup_latencies), 2
# # # # #             ) if warmup_latencies else None,
# # # # #             "warmup_max_ms": round(
# # # # #                 max(warmup_latencies), 2
# # # # #             ) if warmup_latencies else None,
# # # # #             "ingress_samples": ingress_samples,
# # # # #             "throughput_samples": throughput_samples,
# # # # #         }

# # # # #         return self.results



# # # # import time
# # # # import threading
# # # # import random
# # # # import string
# # # # from solace.messaging.resources.topic import Topic
# # # # from solace.messaging.resources.topic_subscription import TopicSubscription
# # # # from solace.messaging.resources.queue import Queue


# # # # def build_message(template: str, index: int, size: int) -> str:
# # # #     if template.startswith("__fixed__"):
# # # #         return template[len("__fixed__"):]
# # # #     if not template.strip():
# # # #         return "X" * size
# # # #     msg = template
# # # #     msg = msg.replace("{{index}}", str(index))
# # # #     msg = msg.replace("{{timestamp}}", str(round(time.time() * 1000)))
# # # #     msg = msg.replace("{{random}}", ''.join(random.choices(string.ascii_letters, k=8)))
# # # #     return msg


# # # # class PerfTester:

# # # #     def __init__(self, service):
# # # #         self.service = service
# # # #         self.results = {}
# # # #         self._stop = False

# # # #     def stop(self):
# # # #         self._stop = True

# # # #     def run(
# # # #         self,
# # # #         target: str,
# # # #         target_type: str,
# # # #         message_count: int,
# # # #         message_size: int,
# # # #         message_template: str,
# # # #         delivery_mode: str = "direct",
# # # #         rate_limit: int = 0,
# # # #         window_size: int = 50,
# # # #         queue_type: str = "exclusive",
# # # #         warmup_count: int = 0,
# # # #         consumer_count: int = 1,
# # # #         on_progress=None
# # # #     ):
# # # #         self._stop = False
# # # #         latencies = []
# # # #         received_count = [0]
# # # #         published_count = [0]
# # # #         errors = [0]
# # # #         throughput_samples = []     # egress per-second
# # # #         ingress_samples = []        # ingress per-second
# # # #         warmup_latencies = []
# # # #         lock = threading.Lock()

# # # #         # Mutable time trackers
# # # #         last_egress_time  = [time.time()]
# # # #         last_egress_count = [0]
# # # #         last_ingress_time  = [time.time()]
# # # #         last_ingress_count = [0]
# # # #         last_progress_time = [time.time()]

# # # #         # ── Build publisher ──────────────────────────────────────────────────
# # # #         if delivery_mode == "persistent":
# # # #             try:
# # # #                 from solace.messaging.config.solace_properties.publisher_properties import (
# # # #                     PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE
# # # #                 )
# # # #                 pub_builder = self.service \
# # # #                     .create_persistent_message_publisher_builder()
# # # #                 pub_builder = pub_builder.from_properties({
# # # #                     PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE: window_size
# # # #                 })
# # # #                 publisher = pub_builder.build()
# # # #             except Exception:
# # # #                 publisher = self.service \
# # # #                     .create_persistent_message_publisher_builder().build()
# # # #         else:
# # # #             publisher = self.service \
# # # #                 .create_direct_message_publisher_builder().build()

# # # #         publisher.start()

# # # #         # ── Build receivers ──────────────────────────────────────────────────
# # # #         receivers = []

# # # #         if target_type == "topic":
# # # #             receiver = self.service \
# # # #                 .create_direct_message_receiver_builder() \
# # # #                 .with_subscriptions([TopicSubscription.of(target)]) \
# # # #                 .build()
# # # #             receiver.start()
# # # #             receivers = [receiver]
# # # #             is_persistent_receiver = False
# # # #         else:
# # # #             actual_count = 1 if queue_type == "exclusive" else max(1, consumer_count)
# # # #             if queue_type == "non_exclusive":
# # # #                 queue_obj = Queue.durable_non_exclusive_queue(target)
# # # #             else:
# # # #                 queue_obj = Queue.durable_exclusive_queue(target)

# # # #             for _ in range(actual_count):
# # # #                 r = self.service \
# # # #                     .create_persistent_message_receiver_builder() \
# # # #                     .build(queue_obj)
# # # #                 r.start()
# # # #                 receivers.append(r)
# # # #             is_persistent_receiver = True

# # # #         start_time = time.time()
# # # #         deadline   = start_time + 120

# # # #         # ── Publish thread ───────────────────────────────────────────────────
# # # #         # NOTE: for queues, we publish to a topic with the same name as the
# # # #         # queue. The broker must have a topic subscription on the queue that
# # # #         # matches this topic. If the queue has no subscription, messages won't
# # # #         # be delivered.
# # # #         def publish_messages():
# # # #             topic_obj = Topic.of(target)
# # # #             delay = (1.0 / rate_limit) if rate_limit > 0 else 0

# # # #             for i in range(message_count):
# # # #                 if self._stop:
# # # #                     break
# # # #                 try:
# # # #                     payload = build_message(message_template, i, message_size)
# # # #                     stamped = f"{time.time()}||{payload}"
# # # #                     msg = self.service.message_builder().build(stamped)
# # # #                     publisher.publish(msg, topic_obj)
# # # #                     published_count[0] += 1

# # # #                     # Sample ingress every second
# # # #                     now = time.time()
# # # #                     if now - last_ingress_time[0] >= 1.0:
# # # #                         elapsed_s = now - last_ingress_time[0]
# # # #                         delta     = published_count[0] - last_ingress_count[0]
# # # #                         sample    = round(delta / elapsed_s, 1)
# # # #                         ingress_samples.append(sample)
# # # #                         last_ingress_time[0]  = now
# # # #                         last_ingress_count[0] = published_count[0]

# # # #                 except Exception:
# # # #                     errors[0] += 1

# # # #                 if delay > 0:
# # # #                     time.sleep(delay)

# # # #         pub_thread = threading.Thread(target=publish_messages, daemon=True)
# # # #         pub_thread.start()

# # # #         # ── Helper: current live P99 ─────────────────────────────────────────
# # # #         def live_p99():
# # # #             if not latencies:
# # # #                 return 0.0
# # # #             sl = sorted(latencies)
# # # #             return round(sl[int(len(sl) * 0.99)], 2)

# # # #         # ── Helper: fire progress ────────────────────────────────────────────
# # # #         def fire_progress():
# # # #             if not on_progress:
# # # #                 return
# # # #             now     = time.time()
# # # #             elapsed = now - start_time
# # # #             e_tps   = round(received_count[0]  / elapsed, 1) if elapsed > 0 else 0.0
# # # #             i_tps   = round(published_count[0] / elapsed, 1) if elapsed > 0 else 0.0
# # # #             # Use latest sample if available (more accurate per-second rate)
# # # #             if ingress_samples:
# # # #                 i_tps = ingress_samples[-1]
# # # #             if throughput_samples:
# # # #                 e_tps = throughput_samples[-1]

# # # #             on_progress(
# # # #                 received_count[0],
# # # #                 message_count,
# # # #                 round(elapsed, 1),
# # # #                 e_tps,
# # # #                 i_tps,
# # # #                 live_p99()
# # # #             )
# # # #             last_progress_time[0] = now

# # # #         # ── Single receiver loop (main thread) ───────────────────────────────
# # # #         def main_receive_loop():
# # # #             while (
# # # #                 received_count[0] < message_count
# # # #                 and time.time() < deadline
# # # #                 and not self._stop
# # # #             ):
# # # #                 try:
# # # #                     msg = receivers[0].receive_message(timeout=500)
# # # #                     if msg:
# # # #                         raw = msg.get_payload_as_string() or ""
# # # #                         if is_persistent_receiver:
# # # #                             receivers[0].ack(msg)
# # # #                         try:
# # # #                             sent_time  = float(raw.split("||")[0])
# # # #                             latency_ms = (time.time() - sent_time) * 1000
# # # #                             if received_count[0] < warmup_count:
# # # #                                 warmup_latencies.append(latency_ms)
# # # #                             else:
# # # #                                 latencies.append(latency_ms)
# # # #                         except Exception:
# # # #                             pass
# # # #                         received_count[0] += 1

# # # #                         # Sample egress every second
# # # #                         now = time.time()
# # # #                         if now - last_egress_time[0] >= 1.0:
# # # #                             elapsed_s = now - last_egress_time[0]
# # # #                             delta     = received_count[0] - last_egress_count[0]
# # # #                             throughput_samples.append(round(delta / elapsed_s, 1))
# # # #                             last_egress_time[0]  = now
# # # #                             last_egress_count[0] = received_count[0]

# # # #                 except Exception:
# # # #                     pass

# # # #                 # Fire progress every 300ms regardless of message arrival
# # # #                 if time.time() - last_progress_time[0] >= 0.3:
# # # #                     fire_progress()

# # # #         # ── Multi-receiver loop (each in thread) ─────────────────────────────
# # # #         def receive_loop(receiver):
# # # #             while (
# # # #                 received_count[0] < message_count
# # # #                 and time.time() < deadline
# # # #                 and not self._stop
# # # #             ):
# # # #                 try:
# # # #                     msg = receiver.receive_message(timeout=500)
# # # #                     if msg:
# # # #                         raw = msg.get_payload_as_string() or ""
# # # #                         if is_persistent_receiver:
# # # #                             receiver.ack(msg)
# # # #                         try:
# # # #                             sent_time  = float(raw.split("||")[0])
# # # #                             latency_ms = (time.time() - sent_time) * 1000
# # # #                             with lock:
# # # #                                 if received_count[0] < warmup_count:
# # # #                                     warmup_latencies.append(latency_ms)
# # # #                                 else:
# # # #                                     latencies.append(latency_ms)
# # # #                                 received_count[0] += 1

# # # #                                 # Sample egress every second
# # # #                                 now = time.time()
# # # #                                 if now - last_egress_time[0] >= 1.0:
# # # #                                     elapsed_s = now - last_egress_time[0]
# # # #                                     delta     = received_count[0] - last_egress_count[0]
# # # #                                     throughput_samples.append(round(delta / elapsed_s, 1))
# # # #                                     last_egress_time[0]  = now
# # # #                                     last_egress_count[0] = received_count[0]
# # # #                         except Exception:
# # # #                             pass
# # # #                 except Exception:
# # # #                     pass

# # # #         # ── Run ──────────────────────────────────────────────────────────────
# # # #         if len(receivers) == 1:
# # # #             main_receive_loop()
# # # #         else:
# # # #             recv_threads = [
# # # #                 threading.Thread(target=receive_loop, args=(r,), daemon=True)
# # # #                 for r in receivers
# # # #             ]
# # # #             for t in recv_threads:
# # # #                 t.start()

# # # #             while (
# # # #                 received_count[0] < message_count
# # # #                 and time.time() < deadline
# # # #                 and not self._stop
# # # #             ):
# # # #                 time.sleep(0.3)
# # # #                 fire_progress()

# # # #             for t in recv_threads:
# # # #                 t.join(timeout=5)

# # # #         pub_thread.join(timeout=15)

# # # #         # ── Cleanup ──────────────────────────────────────────────────────────
# # # #         for obj in [publisher] + receivers:
# # # #             try:
# # # #                 obj.terminate()
# # # #             except Exception:
# # # #                 pass

# # # #         total_time = time.time() - start_time
# # # #         sorted_lat = sorted(latencies)

# # # #         self.results = {
# # # #             "target":               target,
# # # #             "target_type":          target_type,
# # # #             "queue_type":           queue_type if target_type == "queue" else None,
# # # #             "consumer_count":       len(receivers) if target_type == "queue" else 1,
# # # #             "delivery_mode":        delivery_mode,
# # # #             "rate_limit":           rate_limit,
# # # #             "window_size":          window_size if delivery_mode == "persistent" else None,
# # # #             "message_count":        message_count,
# # # #             "message_size_bytes":   message_size,
# # # #             "warmup_count":         warmup_count,
# # # #             "sent":                 published_count[0],
# # # #             "received":             received_count[0],
# # # #             "errors":               errors[0],
# # # #             "total_time_sec":       round(total_time, 2),
# # # #             "throughput_msg_per_sec": round(
# # # #                 received_count[0] / total_time if total_time > 0 else 0, 2
# # # #             ),
# # # #             "avg_latency_ms":   round(sum(latencies) / len(latencies), 2) if latencies else 0,
# # # #             "min_latency_ms":   round(min(latencies), 2) if latencies else 0,
# # # #             "max_latency_ms":   round(max(latencies), 2) if latencies else 0,
# # # #             "p95_latency_ms":   round(sorted_lat[int(len(sorted_lat) * 0.95)], 2) if sorted_lat else 0,
# # # #             "p99_latency_ms":   round(sorted_lat[int(len(sorted_lat) * 0.99)], 2) if sorted_lat else 0,
# # # #             "warmup_avg_ms":    round(sum(warmup_latencies) / len(warmup_latencies), 2) if warmup_latencies else None,
# # # #             "warmup_max_ms":    round(max(warmup_latencies), 2) if warmup_latencies else None,
# # # #             "ingress_samples":      ingress_samples,
# # # #             "throughput_samples":   throughput_samples,
# # # #         }

# # # #         return self.results


# # # from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
# # # from fastapi.responses import StreamingResponse
# # # from pydantic import BaseModel
# # # from solengineer.api import state
# # # from solengineer.perf.perf_tester import PerfTester
# # # import asyncio
# # # import threading
# # # import json
# # # import io
# # # import openpyxl
# # # from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
# # # from openpyxl.chart import LineChart, Reference
# # # from datetime import datetime

# # # router = APIRouter()

# # # _current_tester: PerfTester | None = None


# # # class PerfRequest(BaseModel):
# # #     target: str
# # #     target_type: str = "topic"
# # #     message_count: int = 1000
# # #     message_size: int = 256
# # #     message_template: str = ""
# # #     delivery_mode: str = "direct"
# # #     rate_limit: int = 0
# # #     window_size: int = 50
# # #     queue_type: str = "exclusive"
# # #     warmup_count: int = 0
# # #     consumer_count: int = 1


# # # @router.post("/api/perf")
# # # def run_perf(req: PerfRequest):
# # #     service = state.get_service()
# # #     if not service:
# # #         raise HTTPException(status_code=400, detail="Not connected to broker")
# # #     tester = PerfTester(service)
# # #     results = tester.run(
# # #         target=req.target,
# # #         target_type=req.target_type,
# # #         message_count=req.message_count,
# # #         message_size=req.message_size,
# # #         message_template=req.message_template,
# # #         delivery_mode=req.delivery_mode,
# # #         rate_limit=req.rate_limit,
# # #         window_size=req.window_size,
# # #         queue_type=req.queue_type,
# # #         warmup_count=req.warmup_count,
# # #         consumer_count=req.consumer_count
# # #     )
# # #     return results


# # # @router.post("/api/perf/stop")
# # # def stop_perf():
# # #     global _current_tester
# # #     if _current_tester:
# # #         _current_tester.stop()
# # #     return {"status": "stopped"}


# # # # ─── Excel Export ─────────────────────────────────────────────────────────────

# # # @router.post("/api/perf/export/excel")
# # # def export_perf_excel(results: dict):
# # #     wb = openpyxl.Workbook()

# # #     header_font  = Font(bold=True, color="FFFFFF", size=11)
# # #     header_fill  = PatternFill("solid", fgColor="1A73E8")
# # #     label_font   = Font(bold=True, color="5A6675", size=10)
# # #     value_font   = Font(color="1A2733", size=10)
# # #     title_font   = Font(bold=True, color="1A2733", size=13)
# # #     center       = Alignment(horizontal="center", vertical="center")
# # #     left         = Alignment(horizontal="left", vertical="center")
# # #     thin         = Side(style="thin", color="D4DAE0")
# # #     border       = Border(left=thin, right=thin, top=thin, bottom=thin)

# # #     ws = wb.active
# # #     ws.title = "Summary"
# # #     ws.sheet_view.showGridLines = False
# # #     ws.column_dimensions["A"].width = 32
# # #     ws.column_dimensions["B"].width = 32

# # #     ws.merge_cells("A1:B1")
# # #     ws["A1"] = "SolEngineer — Performance Test Results"
# # #     ws["A1"].font = title_font
# # #     ws["A1"].alignment = center
# # #     ws["A1"].fill = PatternFill("solid", fgColor="F5F7FA")
# # #     ws.row_dimensions[1].height = 32

# # #     ws.merge_cells("A2:B2")
# # #     ws["A2"] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
# # #     ws["A2"].font = Font(color="8A96A3", size=9, italic=True)
# # #     ws["A2"].alignment = center
# # #     ws.row_dimensions[2].height = 18

# # #     def write_section(start_row, title, rows):
# # #         ws.merge_cells(f"A{start_row}:B{start_row}")
# # #         ws[f"A{start_row}"] = title
# # #         ws[f"A{start_row}"].font = header_font
# # #         ws[f"A{start_row}"].fill = header_fill
# # #         ws[f"A{start_row}"].alignment = center
# # #         ws[f"B{start_row}"].fill = header_fill
# # #         ws.row_dimensions[start_row].height = 22
# # #         r = start_row + 1
# # #         for label, value in rows:
# # #             ws.cell(r, 1, label).font = label_font
# # #             ws.cell(r, 1).alignment = left
# # #             ws.cell(r, 1).border = border
# # #             ws.cell(r, 2, value).font = value_font
# # #             ws.cell(r, 2).alignment = left
# # #             ws.cell(r, 2).border = border
# # #             ws.row_dimensions[r].height = 20
# # #             r += 1
# # #         return r

# # #     next_row = write_section(4, "Configuration", [
# # #         ("Target",               results.get("target", "")),
# # #         ("Target Type",          results.get("target_type", "").capitalize()),
# # #         ("Queue Type",           results.get("queue_type") or "N/A"),
# # #         ("Consumer Count",       results.get("consumer_count", 1)),
# # #         ("Delivery Mode",        results.get("delivery_mode", "").capitalize()),
# # #         ("Message Count",        results.get("message_count", "")),
# # #         ("Message Size (bytes)", results.get("message_size_bytes", "")),
# # #         ("Rate Limit (msg/s)",   results.get("rate_limit", 0) or "Unlimited"),
# # #         ("Window Size",          results.get("window_size") or "N/A (Direct)"),
# # #         ("Warmup Messages",      results.get("warmup_count", 0)),
# # #     ])

# # #     next_row += 1
# # #     write_section(next_row, "Results", [
# # #         ("Throughput (msg/s)",  results.get("throughput_msg_per_sec", "")),
# # #         ("Avg Latency (ms)",    results.get("avg_latency_ms", "")),
# # #         ("P95 Latency (ms)",    results.get("p95_latency_ms", "")),
# # #         ("P99 Latency (ms)",    results.get("p99_latency_ms", "")),
# # #         ("Min Latency (ms)",    results.get("min_latency_ms", "")),
# # #         ("Max Latency (ms)",    results.get("max_latency_ms", "")),
# # #         ("Warmup Avg (ms)",     results.get("warmup_avg_ms") or "N/A"),
# # #         ("Warmup Max (ms)",     results.get("warmup_max_ms") or "N/A"),
# # #         ("Messages Sent",       results.get("sent", "")),
# # #         ("Messages Received",   results.get("received", "")),
# # #         ("Errors",              results.get("errors", "")),
# # #         ("Total Time (sec)",    results.get("total_time_sec", "")),
# # #     ])

# # #     # Sheet 2 — Egress (receive rate)
# # #     egress = results.get("throughput_samples", [])
# # #     if egress:
# # #         ws2 = wb.create_sheet("Egress (Receive Rate)")
# # #         ws2.sheet_view.showGridLines = False
# # #         ws2.column_dimensions["A"].width = 15
# # #         ws2.column_dimensions["B"].width = 25
# # #         for col, text in [(1, "Second"), (2, "Egress (msg/s)")]:
# # #             cell = ws2.cell(1, col, text)
# # #             cell.font = header_font
# # #             cell.fill = header_fill
# # #             cell.alignment = center
# # #             cell.border = border
# # #         ws2.row_dimensions[1].height = 22
# # #         for i, v in enumerate(egress, start=2):
# # #             ws2.cell(i, 1, i - 1).alignment = center
# # #             ws2.cell(i, 1).border = border
# # #             ws2.cell(i, 2, v).alignment = center
# # #             ws2.cell(i, 2).border = border
# # #         chart2 = LineChart()
# # #         chart2.title = "Egress — Receive Rate"
# # #         chart2.style = 10
# # #         chart2.y_axis.title = "msg/s"
# # #         chart2.x_axis.title = "Second"
# # #         chart2.width = 22
# # #         chart2.height = 14
# # #         data2 = Reference(ws2, min_col=2, min_row=1, max_row=len(egress) + 1)
# # #         chart2.add_data(data2, titles_from_data=True)
# # #         ws2.add_chart(chart2, "D2")

# # #     # Sheet 3 — Ingress (publish rate)
# # #     ingress = results.get("ingress_samples", [])
# # #     if ingress:
# # #         ws3 = wb.create_sheet("Ingress (Publish Rate)")
# # #         ws3.sheet_view.showGridLines = False
# # #         ws3.column_dimensions["A"].width = 15
# # #         ws3.column_dimensions["B"].width = 25
# # #         for col, text in [(1, "Second"), (2, "Ingress (msg/s)")]:
# # #             cell = ws3.cell(1, col, text)
# # #             cell.font = header_font
# # #             cell.fill = PatternFill("solid", fgColor="00874A")
# # #             cell.alignment = center
# # #             cell.border = border
# # #         ws3.row_dimensions[1].height = 22
# # #         for i, v in enumerate(ingress, start=2):
# # #             ws3.cell(i, 1, i - 1).alignment = center
# # #             ws3.cell(i, 1).border = border
# # #             ws3.cell(i, 2, v).alignment = center
# # #             ws3.cell(i, 2).border = border
# # #         chart3 = LineChart()
# # #         chart3.title = "Ingress — Publish Rate"
# # #         chart3.style = 10
# # #         chart3.y_axis.title = "msg/s"
# # #         chart3.x_axis.title = "Second"
# # #         chart3.width = 22
# # #         chart3.height = 14
# # #         data3 = Reference(ws3, min_col=2, min_row=1, max_row=len(ingress) + 1)
# # #         chart3.add_data(data3, titles_from_data=True)
# # #         ws3.add_chart(chart3, "D2")

# # #     output = io.BytesIO()
# # #     wb.save(output)
# # #     output.seek(0)

# # #     filename = f"solengineer-perf-{results.get('target','test').replace('/','_')}.xlsx"
# # #     return StreamingResponse(
# # #         output,
# # #         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
# # #         headers={"Content-Disposition": f"attachment; filename={filename}"}
# # #     )


# # # # ─── WebSocket Perf ───────────────────────────────────────────────────────────

# # # @router.websocket("/ws/perf")
# # # async def perf_ws(websocket: WebSocket):
# # #     global _current_tester
# # #     await websocket.accept()

# # #     service = state.get_service()
# # #     if not service:
# # #         await websocket.send_json({"error": "Not connected to broker"})
# # #         await websocket.close()
# # #         return

# # #     try:
# # #         config = await asyncio.wait_for(websocket.receive_text(), timeout=10)
# # #         req = json.loads(config)
# # #     except Exception:
# # #         await websocket.close()
# # #         return

# # #     tester = PerfTester(service)
# # #     _current_tester = tester
# # #     results_holder = {}
# # #     loop = asyncio.get_event_loop()

# # #     def on_progress(received, total, elapsed, tps, ingress_tps=0):
# # #         asyncio.run_coroutine_threadsafe(
# # #             websocket.send_json({
# # #                 "type":        "progress",
# # #                 "received":    received,
# # #                 "total":       total,
# # #                 "elapsed":     elapsed,
# # #                 "tps":         tps,
# # #                 "ingress_tps": ingress_tps,
# # #                 "percent":     round(received / total * 100, 1)
# # #             }),
# # #             loop
# # #         )

# # #     def run_test():
# # #         try:
# # #             results_holder["data"] = tester.run(
# # #                 target=req.get("target", "perf/test"),
# # #                 target_type=req.get("target_type", "topic"),
# # #                 message_count=req.get("message_count", 1000),
# # #                 message_size=req.get("message_size", 256),
# # #                 message_template=req.get("message_template", ""),
# # #                 delivery_mode=req.get("delivery_mode", "direct"),
# # #                 rate_limit=req.get("rate_limit", 0),
# # #                 window_size=req.get("window_size", 50),
# # #                 queue_type=req.get("queue_type", "exclusive"),
# # #                 warmup_count=req.get("warmup_count", 0),
# # #                 consumer_count=req.get("consumer_count", 1),
# # #                 on_progress=on_progress
# # #             )
# # #         except Exception as e:
# # #             results_holder["error"] = str(e)

# # #     thread = threading.Thread(target=run_test)
# # #     thread.start()

# # #     try:
# # #         while thread.is_alive():
# # #             await asyncio.sleep(0.3)
# # #         thread.join()

# # #         if "error" in results_holder:
# # #             await websocket.send_json({
# # #                 "type": "error",
# # #                 "error": results_holder["error"]
# # #             })
# # #         elif "data" in results_holder:
# # #             await websocket.send_json({
# # #                 "type":      "complete",
# # #                 "results":   results_holder["data"],
# # #                 "timestamp": datetime.now().isoformat()
# # #             })
# # #     except WebSocketDisconnect:
# # #         tester.stop()
# # #     finally:
# # #         try:
# # #             await websocket.close()
# # #         except Exception:
# # #             pass


# # import time
# # import threading
# # import random
# # import string
# # from solace.messaging.resources.topic import Topic
# # from solace.messaging.resources.topic_subscription import TopicSubscription
# # from solace.messaging.resources.queue import Queue


# # def build_message(template: str, index: int, size: int) -> str:
# #     if template.startswith("__fixed__"):
# #         return template[len("__fixed__"):]
# #     if not template.strip():
# #         return "X" * size
# #     msg = template
# #     msg = msg.replace("{{index}}", str(index))
# #     msg = msg.replace("{{timestamp}}", str(round(time.time() * 1000)))
# #     msg = msg.replace("{{random}}", ''.join(random.choices(string.ascii_letters, k=8)))
# #     return msg


# # class PerfTester:

# #     def __init__(self, service):
# #         self.service = service
# #         self.results = {}
# #         self._stop = False

# #     def stop(self):
# #         self._stop = True

# #     def run(
# #         self,
# #         target: str,
# #         target_type: str,
# #         message_count: int,
# #         message_size: int,
# #         message_template: str,
# #         delivery_mode: str = "direct",
# #         rate_limit: int = 0,
# #         window_size: int = 50,
# #         queue_type: str = "exclusive",
# #         warmup_count: int = 0,
# #         consumer_count: int = 1,
# #         on_progress=None
# #     ):
# #         self._stop = False
# #         latencies = []
# #         received_count = [0]
# #         errors = [0]
# #         throughput_samples = []     # egress — receive rate per second
# #         ingress_samples = []        # ingress — publish rate per second
# #         warmup_latencies = []
# #         lock = threading.Lock()

# #         # --- Build publisher ---
# #         if delivery_mode == "persistent":
# #             try:
# #                 from solace.messaging.config.solace_properties.publisher_properties import (
# #                     PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE
# #                 )
# #                 pub_builder = self.service \
# #                     .create_persistent_message_publisher_builder()
# #                 pub_builder = pub_builder.from_properties({
# #                     PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE: window_size
# #                 })
# #                 publisher = pub_builder.build()
# #             except Exception:
# #                 publisher = self.service \
# #                     .create_persistent_message_publisher_builder().build()
# #         else:
# #             publisher = self.service \
# #                 .create_direct_message_publisher_builder().build()

# #         publisher.start()

# #         # --- Build receivers ---
# #         receivers = []

# #         if target_type == "topic":
# #             receiver = self.service \
# #                 .create_direct_message_receiver_builder() \
# #                 .with_subscriptions([TopicSubscription.of(target)]) \
# #                 .build()
# #             receiver.start()
# #             receivers = [receiver]
# #             is_persistent_receiver = False
# #         else:
# #             actual_consumer_count = 1 if queue_type == "exclusive" else max(1, consumer_count)

# #             if queue_type == "non_exclusive":
# #                 queue = Queue.durable_non_exclusive_queue(target)
# #             else:
# #                 queue = Queue.durable_exclusive_queue(target)

# #             for _ in range(actual_consumer_count):
# #                 r = self.service \
# #                     .create_persistent_message_receiver_builder() \
# #                     .build(queue)
# #                 r.start()
# #                 receivers.append(r)

# #             is_persistent_receiver = True

# #         start_time = time.time()
# #         last_egress_time = [start_time]
# #         last_egress_count = [0]
# #         last_ingress_time = [start_time]
# #         last_ingress_count = [0]

# #         # --- Publish thread — tracks ingress rate ---
# #         def publish_messages():
# #             topic_obj = Topic.of(target)
# #             delay = (1.0 / rate_limit) if rate_limit > 0 else 0
# #             published = [0]

# #             for i in range(message_count):
# #                 if self._stop:
# #                     break
# #                 try:
# #                     payload = build_message(message_template, i, message_size)
# #                     stamped = f"{time.time()}||{payload}"
# #                     msg = self.service.message_builder().build(stamped)
# #                     publisher.publish(msg, topic_obj)
# #                     published[0] += 1

# #                     # Sample ingress every second
# #                     now = time.time()
# #                     if now - last_ingress_time[0] >= 1.0:
# #                         sample = (
# #                             (published[0] - last_ingress_count[0])
# #                             / (now - last_ingress_time[0])
# #                         )
# #                         ingress_samples.append(round(sample, 1))
# #                         last_ingress_time[0] = now
# #                         last_ingress_count[0] = published[0]

# #                 except Exception:
# #                     errors[0] += 1

# #                 if delay > 0:
# #                     time.sleep(delay)

# #         pub_thread = threading.Thread(target=publish_messages, daemon=True)
# #         pub_thread.start()

# #         # --- Per-receiver thread for multi-consumer ---
# #         def receive_loop(receiver):
# #             while (
# #                 received_count[0] < message_count
# #                 and time.time() < deadline
# #                 and not self._stop
# #             ):
# #                 try:
# #                     msg = receiver.receive_message(timeout=2000)
# #                     if msg:
# #                         raw = msg.get_payload_as_string() or ""
# #                         if is_persistent_receiver:
# #                             receiver.ack(msg)
# #                         try:
# #                             sent_time = float(raw.split("||")[0])
# #                             latency_ms = (time.time() - sent_time) * 1000
# #                             with lock:
# #                                 if received_count[0] < warmup_count:
# #                                     warmup_latencies.append(latency_ms)
# #                                 else:
# #                                     latencies.append(latency_ms)
# #                                 received_count[0] += 1
# #                         except Exception:
# #                             pass
# #                 except Exception:
# #                     pass

# #         deadline = time.time() + 90

# #         if len(receivers) == 1:
# #             # Single receiver — main thread
# #             while (
# #                 received_count[0] < message_count
# #                 and time.time() < deadline
# #                 and not self._stop
# #             ):
# #                 try:
# #                     msg = receivers[0].receive_message(timeout=2000)
# #                     if msg:
# #                         raw = msg.get_payload_as_string() or ""
# #                         if is_persistent_receiver:
# #                             receivers[0].ack(msg)
# #                         try:
# #                             sent_time = float(raw.split("||")[0])
# #                             latency_ms = (time.time() - sent_time) * 1000
# #                             if received_count[0] < warmup_count:
# #                                 warmup_latencies.append(latency_ms)
# #                             else:
# #                                 latencies.append(latency_ms)
# #                         except Exception:
# #                             pass
# #                         received_count[0] += 1

# #                         # Sample egress every second
# #                         now = time.time()
# #                         if now - last_egress_time[0] >= 1.0:
# #                             sample_tps = (
# #                                 (received_count[0] - last_egress_count[0])
# #                                 / (now - last_egress_time[0])
# #                             )
# #                             throughput_samples.append(round(sample_tps, 1))
# #                             last_egress_time[0] = now
# #                             last_egress_count[0] = received_count[0]

# #                         if on_progress:
# #                             elapsed = time.time() - start_time
# #                             tps = received_count[0] / elapsed if elapsed > 0 else 0
# #                             # Latest ingress sample
# #                             ingress_tps = ingress_samples[-1] if ingress_samples else 0
# #                             on_progress(
# #                                 received_count[0], message_count,
# #                                 round(elapsed, 1), round(tps, 1),
# #                                 round(ingress_tps, 1)
# #                             )
# #                 except Exception:
# #                     pass

# #         else:
# #             # Multiple receivers — each in own thread
# #             recv_threads = []
# #             for r in receivers:
# #                 t = threading.Thread(target=receive_loop, args=(r,), daemon=True)
# #                 t.start()
# #                 recv_threads.append(t)

# #             # Progress + egress sampling in main thread
# #             while (
# #                 received_count[0] < message_count
# #                 and time.time() < deadline
# #                 and not self._stop
# #             ):
# #                 time.sleep(0.1)
# #                 now = time.time()
# #                 if now - last_egress_time[0] >= 1.0:
# #                     with lock:
# #                         sample_tps = (
# #                             (received_count[0] - last_egress_count[0])
# #                             / (now - last_egress_time[0])
# #                         )
# #                         throughput_samples.append(round(sample_tps, 1))
# #                         last_egress_time[0] = now
# #                         last_egress_count[0] = received_count[0]

# #                 if on_progress:
# #                     elapsed = time.time() - start_time
# #                     tps = received_count[0] / elapsed if elapsed > 0 else 0
# #                     ingress_tps = ingress_samples[-1] if ingress_samples else 0
# #                     on_progress(
# #                         received_count[0], message_count,
# #                         round(elapsed, 1), round(tps, 1),
# #                         round(ingress_tps, 1)
# #                     )

# #             for t in recv_threads:
# #                 t.join(timeout=5)

# #         pub_thread.join(timeout=10)

# #         # --- Cleanup ---
# #         try:
# #             publisher.terminate()
# #         except Exception:
# #             pass
# #         for r in receivers:
# #             try:
# #                 r.terminate()
# #             except Exception:
# #                 pass

# #         total_time = time.time() - start_time
# #         sorted_lat = sorted(latencies)

# #         self.results = {
# #             "target": target,
# #             "target_type": target_type,
# #             "queue_type": queue_type if target_type == "queue" else None,
# #             "consumer_count": len(receivers) if target_type == "queue" else 1,
# #             "delivery_mode": delivery_mode,
# #             "rate_limit": rate_limit,
# #             "window_size": window_size if delivery_mode == "persistent" else None,
# #             "message_count": message_count,
# #             "message_size_bytes": message_size,
# #             "warmup_count": warmup_count,
# #             "sent": message_count - errors[0],
# #             "received": received_count[0],
# #             "errors": errors[0],
# #             "total_time_sec": round(total_time, 2),
# #             "throughput_msg_per_sec": round(
# #                 received_count[0] / total_time if total_time > 0 else 0, 2
# #             ),
# #             "avg_latency_ms": round(
# #                 sum(latencies) / len(latencies), 2
# #             ) if latencies else 0,
# #             "min_latency_ms": round(min(latencies), 2) if latencies else 0,
# #             "max_latency_ms": round(max(latencies), 2) if latencies else 0,
# #             "p95_latency_ms": round(
# #                 sorted_lat[int(len(sorted_lat) * 0.95)], 2
# #             ) if sorted_lat else 0,
# #             "p99_latency_ms": round(
# #                 sorted_lat[int(len(sorted_lat) * 0.99)], 2
# #             ) if sorted_lat else 0,
# #             "warmup_avg_ms": round(
# #                 sum(warmup_latencies) / len(warmup_latencies), 2
# #             ) if warmup_latencies else None,
# #             "warmup_max_ms": round(
# #                 max(warmup_latencies), 2
# #             ) if warmup_latencies else None,
# #             "ingress_samples": ingress_samples,     # ← NEW publish rate/sec
# #             "throughput_samples": throughput_samples,  # egress receive rate/sec
# #         }

# #         return self.results


# import time
# import threading
# import random
# import string
# from solace.messaging.resources.topic import Topic
# from solace.messaging.resources.topic_subscription import TopicSubscription
# from solace.messaging.resources.queue import Queue


# def build_message(template: str, index: int, size: int) -> str:
#     if template.startswith("__fixed__"):
#         return template[len("__fixed__"):]
#     if not template.strip():
#         return "X" * size
#     msg = template
#     msg = msg.replace("{{index}}", str(index))
#     msg = msg.replace("{{timestamp}}", str(round(time.time() * 1000)))
#     msg = msg.replace("{{random}}", ''.join(random.choices(string.ascii_letters, k=8)))
#     return msg


# class PerfTester:

#     def __init__(self, service):
#         self.service = service
#         self.results = {}
#         self._stop = False

#     def stop(self):
#         self._stop = True

#     def run(
#         self,
#         target: str,
#         target_type: str,
#         message_count: int,
#         message_size: int,
#         message_template: str,
#         delivery_mode: str = "direct",
#         rate_limit: int = 0,
#         window_size: int = 50,
#         queue_type: str = "exclusive",
#         warmup_count: int = 0,
#         consumer_count: int = 1,
#         on_progress=None
#     ):
#         self._stop = False
#         latencies = []
#         received_count = [0]
#         errors = [0]
#         throughput_samples = []     # egress — receive rate per second
#         ingress_samples = []        # ingress — publish rate per second
#         warmup_latencies = []
#         lock = threading.Lock()

#         # --- Build publisher ---
#         if delivery_mode == "persistent":
#             try:
#                 from solace.messaging.config.solace_properties.publisher_properties import (
#                     PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE
#                 )
#                 pub_builder = self.service \
#                     .create_persistent_message_publisher_builder()
#                 pub_builder = pub_builder.from_properties({
#                     PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE: window_size
#                 })
#                 publisher = pub_builder.build()
#             except Exception:
#                 publisher = self.service \
#                     .create_persistent_message_publisher_builder().build()
#         else:
#             publisher = self.service \
#                 .create_direct_message_publisher_builder().build()

#         publisher.start()

#         # --- Build receivers ---
#         receivers = []

#         if target_type == "topic":
#             receiver = self.service \
#                 .create_direct_message_receiver_builder() \
#                 .with_subscriptions([TopicSubscription.of(target)]) \
#                 .build()
#             receiver.start()
#             receivers = [receiver]
#             is_persistent_receiver = False
#         else:
#             actual_consumer_count = 1 if queue_type == "exclusive" else max(1, consumer_count)

#             if queue_type == "non_exclusive":
#                 queue = Queue.durable_non_exclusive_queue(target)
#             else:
#                 queue = Queue.durable_exclusive_queue(target)

#             for _ in range(actual_consumer_count):
#                 r = self.service \
#                     .create_persistent_message_receiver_builder() \
#                     .build(queue)
#                 r.start()
#                 receivers.append(r)

#             is_persistent_receiver = True

#         start_time = time.time()
#         last_egress_time = [start_time]
#         last_egress_count = [0]
#         last_ingress_time = [start_time]
#         last_ingress_count = [0]

#         # --- Publish thread — tracks ingress rate ---
#         def publish_messages():
#             topic_obj = Topic.of(target)
#             delay = (1.0 / rate_limit) if rate_limit > 0 else 0
#             published = [0]

#             for i in range(message_count):
#                 if self._stop:
#                     break
#                 try:
#                     payload = build_message(message_template, i, message_size)
#                     stamped = f"{time.time()}||{payload}"
#                     msg = self.service.message_builder().build(stamped)
#                     publisher.publish(msg, topic_obj)
#                     published[0] += 1

#                     # Sample ingress every second
#                     now = time.time()
#                     if now - last_ingress_time[0] >= 1.0:
#                         sample = (
#                             (published[0] - last_ingress_count[0])
#                             / (now - last_ingress_time[0])
#                         )
#                         ingress_samples.append(round(sample, 1))
#                         last_ingress_time[0] = now
#                         last_ingress_count[0] = published[0]

#                 except Exception:
#                     errors[0] += 1

#                 if delay > 0:
#                     time.sleep(delay)

#         pub_thread = threading.Thread(target=publish_messages, daemon=True)
#         pub_thread.start()

#         # --- Per-receiver thread for multi-consumer ---
#         def receive_loop(receiver):
#             while (
#                 received_count[0] < message_count
#                 and time.time() < deadline
#                 and not self._stop
#             ):
#                 try:
#                     msg = receiver.receive_message(timeout=2000)
#                     if msg:
#                         raw = msg.get_payload_as_string() or ""
#                         if is_persistent_receiver:
#                             receiver.ack(msg)
#                         try:
#                             sent_time = float(raw.split("||")[0])
#                             latency_ms = (time.time() - sent_time) * 1000
#                             with lock:
#                                 if received_count[0] < warmup_count:
#                                     warmup_latencies.append(latency_ms)
#                                 else:
#                                     latencies.append(latency_ms)
#                                 received_count[0] += 1
#                         except Exception:
#                             pass
#                 except Exception:
#                     pass

#         deadline = time.time() + 90

#         if len(receivers) == 1:
#             # Single receiver — main thread
#             while (
#                 received_count[0] < message_count
#                 and time.time() < deadline
#                 and not self._stop
#             ):
#                 try:
#                     msg = receivers[0].receive_message(timeout=2000)
#                     if msg:
#                         raw = msg.get_payload_as_string() or ""
#                         if is_persistent_receiver:
#                             receivers[0].ack(msg)
#                         try:
#                             sent_time = float(raw.split("||")[0])
#                             latency_ms = (time.time() - sent_time) * 1000
#                             if received_count[0] < warmup_count:
#                                 warmup_latencies.append(latency_ms)
#                             else:
#                                 latencies.append(latency_ms)
#                         except Exception:
#                             pass
#                         received_count[0] += 1

#                         # Sample egress every second
#                         now = time.time()
#                         if now - last_egress_time[0] >= 1.0:
#                             sample_tps = (
#                                 (received_count[0] - last_egress_count[0])
#                                 / (now - last_egress_time[0])
#                             )
#                             throughput_samples.append(round(sample_tps, 1))
#                             last_egress_time[0] = now
#                             last_egress_count[0] = received_count[0]

#                         if on_progress:
#                             elapsed = time.time() - start_time
#                             tps = received_count[0] / elapsed if elapsed > 0 else 0
#                             # Latest ingress sample
#                             ingress_tps = ingress_samples[-1] if ingress_samples else 0
#                             on_progress(
#                                 received_count[0], message_count,
#                                 round(elapsed, 1), round(tps, 1),
#                                 round(ingress_tps, 1)
#                             )
#                 except Exception:
#                     pass

#         else:
#             # Multiple receivers — each in own thread
#             recv_threads = []
#             for r in receivers:
#                 t = threading.Thread(target=receive_loop, args=(r,), daemon=True)
#                 t.start()
#                 recv_threads.append(t)

#             # Progress + egress sampling in main thread
#             while (
#                 received_count[0] < message_count
#                 and time.time() < deadline
#                 and not self._stop
#             ):
#                 time.sleep(0.1)
#                 now = time.time()
#                 if now - last_egress_time[0] >= 1.0:
#                     with lock:
#                         sample_tps = (
#                             (received_count[0] - last_egress_count[0])
#                             / (now - last_egress_time[0])
#                         )
#                         throughput_samples.append(round(sample_tps, 1))
#                         last_egress_time[0] = now
#                         last_egress_count[0] = received_count[0]

#                 if on_progress:
#                     elapsed = time.time() - start_time
#                     tps = received_count[0] / elapsed if elapsed > 0 else 0
#                     ingress_tps = ingress_samples[-1] if ingress_samples else 0
#                     on_progress(
#                         received_count[0], message_count,
#                         round(elapsed, 1), round(tps, 1),
#                         round(ingress_tps, 1)
#                     )

#             for t in recv_threads:
#                 t.join(timeout=5)

#         pub_thread.join(timeout=10)

#         # --- Cleanup ---
#         try:
#             publisher.terminate()
#         except Exception:
#             pass
#         for r in receivers:
#             try:
#                 r.terminate()
#             except Exception:
#                 pass

#         total_time = time.time() - start_time
#         sorted_lat = sorted(latencies)

#         self.results = {
#             "target": target,
#             "target_type": target_type,
#             "queue_type": queue_type if target_type == "queue" else None,
#             "consumer_count": len(receivers) if target_type == "queue" else 1,
#             "delivery_mode": delivery_mode,
#             "rate_limit": rate_limit,
#             "window_size": window_size if delivery_mode == "persistent" else None,
#             "message_count": message_count,
#             "message_size_bytes": message_size,
#             "warmup_count": warmup_count,
#             "sent": message_count - errors[0],
#             "received": received_count[0],
#             "errors": errors[0],
#             "total_time_sec": round(total_time, 2),
#             "throughput_msg_per_sec": round(
#                 received_count[0] / total_time if total_time > 0 else 0, 2
#             ),
#             "avg_latency_ms": round(
#                 sum(latencies) / len(latencies), 2
#             ) if latencies else 0,
#             "min_latency_ms": round(min(latencies), 2) if latencies else 0,
#             "max_latency_ms": round(max(latencies), 2) if latencies else 0,
#             "p95_latency_ms": round(
#                 sorted_lat[int(len(sorted_lat) * 0.95)], 2
#             ) if sorted_lat else 0,
#             "p99_latency_ms": round(
#                 sorted_lat[int(len(sorted_lat) * 0.99)], 2
#             ) if sorted_lat else 0,
#             "warmup_avg_ms": round(
#                 sum(warmup_latencies) / len(warmup_latencies), 2
#             ) if warmup_latencies else None,
#             "warmup_max_ms": round(
#                 max(warmup_latencies), 2
#             ) if warmup_latencies else None,
#             "ingress_samples": ingress_samples,     # ← NEW publish rate/sec
#             "throughput_samples": throughput_samples,  # egress receive rate/sec
#         }

#         return self.results



import time
import threading
import random
import string
from solace.messaging.resources.topic import Topic
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.resources.queue import Queue


def build_message(template: str, index: int, size: int) -> str:
    if template.startswith("__fixed__"):
        return template[len("__fixed__"):]
    if not template.strip():
        return "X" * size
    msg = template
    msg = msg.replace("{{index}}", str(index))
    msg = msg.replace("{{timestamp}}", str(round(time.time() * 1000)))
    msg = msg.replace("{{random}}", ''.join(random.choices(string.ascii_letters, k=8)))
    return msg


class PerfTester:

    def __init__(self, service):
        self.service = service
        self.results = {}
        self._stop = False

    def stop(self):
        self._stop = True

    def run(
        self,
        target: str,                    # topic name OR queue name
        target_type: str,               # "topic" or "queue"
        publish_topic: str = "",        # ← NEW: topic to publish to (queue mode only)
        message_count: int = 1000,
        message_size: int = 256,
        message_template: str = "",
        delivery_mode: str = "direct",
        rate_limit: int = 0,
        window_size: int = 50,
        queue_type: str = "exclusive",
        warmup_count: int = 0,
        consumer_count: int = 1,
        on_progress=None
    ):
        self._stop = False
        latencies = []
        received_count = [0]
        errors = [0]
        throughput_samples = []
        ingress_samples = []
        warmup_latencies = []
        lock = threading.Lock()

        # ── Resolve publish topic ────────────────────────────────────────────
        # Topic mode: publish to the topic directly
        # Queue mode: publish to publish_topic (which broker routes to queue)
        #             if publish_topic is empty, fall back to target name
        if target_type == "topic":
            effective_publish_topic = target
        else:
            effective_publish_topic = publish_topic.strip() if publish_topic.strip() else target

        # ── Build publisher ──────────────────────────────────────────────────
        if delivery_mode == "persistent":
            try:
                from solace.messaging.config.solace_properties.publisher_properties import (
                    PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE
                )
                pub_builder = self.service \
                    .create_persistent_message_publisher_builder()
                pub_builder = pub_builder.from_properties({
                    PERSISTENT_MESSAGE_PUBLISH_WINDOW_SIZE: window_size
                })
                publisher = pub_builder.build()
            except Exception:
                publisher = self.service \
                    .create_persistent_message_publisher_builder().build()
        else:
            publisher = self.service \
                .create_direct_message_publisher_builder().build()

        publisher.start()

        # ── Build receivers ──────────────────────────────────────────────────
        receivers = []

        if target_type == "topic":
            # Direct topic subscription
            receiver = self.service \
                .create_direct_message_receiver_builder() \
                .with_subscriptions([TopicSubscription.of(target)]) \
                .build()
            receiver.start()
            receivers = [receiver]
            is_persistent_receiver = False

        else:
            # Queue consumer — reads from queue
            # Broker must have subscription on queue matching publish_topic
            actual_consumer_count = 1 if queue_type == "exclusive" else max(1, consumer_count)

            if queue_type == "non_exclusive":
                queue = Queue.durable_non_exclusive_queue(target)
            else:
                queue = Queue.durable_exclusive_queue(target)

            for _ in range(actual_consumer_count):
                r = self.service \
                    .create_persistent_message_receiver_builder() \
                    .build(queue)
                r.start()
                receivers.append(r)

            is_persistent_receiver = True

        start_time = time.time()
        last_egress_time = [start_time]
        last_egress_count = [0]
        last_ingress_time = [start_time]
        last_ingress_count = [0]

        # ── Publish thread ───────────────────────────────────────────────────
        def publish_messages():
            topic_obj = Topic.of(effective_publish_topic)
            delay = (1.0 / rate_limit) if rate_limit > 0 else 0
            published = [0]

            for i in range(message_count):
                if self._stop:
                    break
                try:
                    payload = build_message(message_template, i, message_size)
                    stamped = f"{time.time()}||{payload}"
                    msg = self.service.message_builder().build(stamped)
                    publisher.publish(msg, topic_obj)
                    published[0] += 1

                    now = time.time()
                    if now - last_ingress_time[0] >= 1.0:
                        sample = (
                            (published[0] - last_ingress_count[0])
                            / (now - last_ingress_time[0])
                        )
                        ingress_samples.append(round(sample, 1))
                        last_ingress_time[0] = now
                        last_ingress_count[0] = published[0]

                except Exception:
                    errors[0] += 1

                if delay > 0:
                    time.sleep(delay)

        pub_thread = threading.Thread(target=publish_messages, daemon=True)
        pub_thread.start()

        # ── Per-receiver thread (multi-consumer) ─────────────────────────────
        def receive_loop(receiver):
            while (
                received_count[0] < message_count
                and time.time() < deadline
                and not self._stop
            ):
                try:
                    msg = receiver.receive_message(timeout=2000)
                    if msg:
                        raw = msg.get_payload_as_string() or ""
                        if is_persistent_receiver:
                            receiver.ack(msg)
                        try:
                            sent_time = float(raw.split("||")[0])
                            latency_ms = (time.time() - sent_time) * 1000
                            with lock:
                                if received_count[0] < warmup_count:
                                    warmup_latencies.append(latency_ms)
                                else:
                                    latencies.append(latency_ms)
                                received_count[0] += 1
                        except Exception:
                            pass
                except Exception:
                    pass

        deadline = time.time() + 90

        if len(receivers) == 1:
            # Single receiver — main thread
            while (
                received_count[0] < message_count
                and time.time() < deadline
                and not self._stop
            ):
                try:
                    msg = receivers[0].receive_message(timeout=2000)
                    if msg:
                        raw = msg.get_payload_as_string() or ""
                        if is_persistent_receiver:
                            receivers[0].ack(msg)
                        try:
                            sent_time = float(raw.split("||")[0])
                            latency_ms = (time.time() - sent_time) * 1000
                            if received_count[0] < warmup_count:
                                warmup_latencies.append(latency_ms)
                            else:
                                latencies.append(latency_ms)
                        except Exception:
                            pass
                        received_count[0] += 1

                        now = time.time()
                        if now - last_egress_time[0] >= 1.0:
                            sample_tps = (
                                (received_count[0] - last_egress_count[0])
                                / (now - last_egress_time[0])
                            )
                            throughput_samples.append(round(sample_tps, 1))
                            last_egress_time[0] = now
                            last_egress_count[0] = received_count[0]

                        if on_progress:
                            elapsed = time.time() - start_time
                            tps = received_count[0] / elapsed if elapsed > 0 else 0
                            ingress_tps = ingress_samples[-1] if ingress_samples else 0
                            on_progress(
                                received_count[0], message_count,
                                round(elapsed, 1), round(tps, 1),
                                round(ingress_tps, 1)
                            )
                except Exception:
                    pass

        else:
            # Multiple receivers — each in own thread
            recv_threads = []
            for r in receivers:
                t = threading.Thread(target=receive_loop, args=(r,), daemon=True)
                t.start()
                recv_threads.append(t)

            while (
                received_count[0] < message_count
                and time.time() < deadline
                and not self._stop
            ):
                time.sleep(0.1)
                now = time.time()
                if now - last_egress_time[0] >= 1.0:
                    with lock:
                        sample_tps = (
                            (received_count[0] - last_egress_count[0])
                            / (now - last_egress_time[0])
                        )
                        throughput_samples.append(round(sample_tps, 1))
                        last_egress_time[0] = now
                        last_egress_count[0] = received_count[0]

                if on_progress:
                    elapsed = time.time() - start_time
                    tps = received_count[0] / elapsed if elapsed > 0 else 0
                    ingress_tps = ingress_samples[-1] if ingress_samples else 0
                    on_progress(
                        received_count[0], message_count,
                        round(elapsed, 1), round(tps, 1),
                        round(ingress_tps, 1)
                    )

            for t in recv_threads:
                t.join(timeout=5)

        pub_thread.join(timeout=10)

        # ── Cleanup ──────────────────────────────────────────────────────────
        try:
            publisher.terminate()
        except Exception:
            pass
        for r in receivers:
            try:
                r.terminate()
            except Exception:
                pass

        total_time = time.time() - start_time
        sorted_lat = sorted(latencies)

        self.results = {
            "target": target,
            "target_type": target_type,
            "publish_topic": effective_publish_topic,   # ← NEW
            "queue_type": queue_type if target_type == "queue" else None,
            "consumer_count": len(receivers) if target_type == "queue" else 1,
            "delivery_mode": delivery_mode,
            "rate_limit": rate_limit,
            "window_size": window_size if delivery_mode == "persistent" else None,
            "message_count": message_count,
            "message_size_bytes": message_size,
            "warmup_count": warmup_count,
            "sent": message_count - errors[0],
            "received": received_count[0],
            "errors": errors[0],
            "total_time_sec": round(total_time, 2),
            "throughput_msg_per_sec": round(
                received_count[0] / total_time if total_time > 0 else 0, 2
            ),
            "avg_latency_ms": round(
                sum(latencies) / len(latencies), 2
            ) if latencies else 0,
            "min_latency_ms": round(min(latencies), 2) if latencies else 0,
            "max_latency_ms": round(max(latencies), 2) if latencies else 0,
            "p95_latency_ms": round(
                sorted_lat[int(len(sorted_lat) * 0.95)], 2
            ) if sorted_lat else 0,
            "p99_latency_ms": round(
                sorted_lat[int(len(sorted_lat) * 0.99)], 2
            ) if sorted_lat else 0,
            "warmup_avg_ms": round(
                sum(warmup_latencies) / len(warmup_latencies), 2
            ) if warmup_latencies else None,
            "warmup_max_ms": round(
                max(warmup_latencies), 2
            ) if warmup_latencies else None,
            "ingress_samples": ingress_samples,
            "throughput_samples": throughput_samples,
        }

        return self.results
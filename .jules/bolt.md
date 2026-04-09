## 2025-05-15 - Smart Sync for Session Synchronization
**Learning:** Database synchronization from filesystem sources often contains duplicate unique IDs in the same source batch. Relying on a static batch-fetched map of existing records can lead to `IntegrityError` if the same ID appears twice for a new record.
**Action:** Always update the local lookup map with newly created records within the synchronization loop to ensure subsequent duplicates in the same batch are treated as updates rather than inserts.

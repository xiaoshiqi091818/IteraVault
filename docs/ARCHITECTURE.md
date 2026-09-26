# Architecture note

The first slice intentionally stops at an append-only event store. A task event has an ID, task ID, kind, JSON payload, source, UTC observation time, and schema version. Later classifiers and experience rules consume these events without changing the original evidence.

The current CLI writes the database locally and is not an automatic host observer. Adapters must declare what a host makes observable. Changes to the event schema require a migration and a fixture-based compatibility test. Cost and privacy controls are required before any automatic background collection is introduced.

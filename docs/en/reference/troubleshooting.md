# Troubleshooting

## Embedding Provider Not Found

Check AstrBot provider settings and make sure at least one Embedding Provider is available. Mnemosyne needs embeddings to convert text into vectors.

## Memories Are Not Summarized

Common causes:

- The conversation has not reached `num_pairs`.
- The LLM Provider is missing or failing.
- The platform is listed in `platform_blacklist`.
- The current session does not contain enough useful messages to summarize.

Temporarily lower `num_pairs` and inspect AstrBot logs for Mnemosyne messages.

## Retrieval Misses Relevant Memories

Check these settings:

- `top_k` may be too low.
- `score_threshold` may be too high.
- `use_session_filtering` may limit retrieval to the current session.
- `use_personality_filtering` may exclude memories from a different persona.
- The Embedding model may have changed without reinitializing the collection.

## Where Is Chroma Data Stored

If `chroma_config.persist_directory` is empty, Mnemosyne creates a Chroma persistence directory under the default plugin data path. Stop AstrBot before copying that directory to another machine.

## Milvus Connection Fails

Check `address`, `db_name`, and authentication settings. For standard Milvus, confirm the service port is reachable:

```bash
nc -vz localhost 19530
```

For Milvus Lite, make sure `milvus_lite_path` points to a writable path.

## Memories Disappear After Switching Databases

Different vector backends do not share data automatically. After switching, initialize the new backend and rebuild memories over time, or export records from the old backend and import them into the new one.

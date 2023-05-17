CREATE DATABASE IF NOT EXISTS shard;
CREATE DATABASE IF NOT EXISTS replica;

CREATE TABLE IF NOT EXISTS shard.view(
    user_id String,
    film_id String,
    start_time UInt16,
    end_time UInt16,
    event_time DateTime DEFAULT now()
)
Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/view', 'replica_1') PARTITION BY toYYYYMMDD(event_time) ORDER BY event_time;

CREATE TABLE IF NOT EXISTS replica.view(
    user_id String,
    film_id String,
    start_time UInt16,
    end_time UInt16,
    event_time DateTime DEFAULT now()
)
Engine=ReplicatedMergeTree('/clickhouse/tables/shard2/view', 'replica_2') PARTITION BY toYYYYMMDD(event_time) ORDER BY event_time;

CREATE TABLE IF NOT EXISTS default.view(
    user_id String,
    film_id String,
    start_time UInt16,
    end_time UInt16,
    event_time DateTime DEFAULT now()
)
Engine=Distributed('company_cluster', '', view, rand());
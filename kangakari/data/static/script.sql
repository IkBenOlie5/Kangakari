CREATE TABLE IF NOT EXISTS prefixes(
    guildid BIGINT NOT NULL,
    prefix TEXT DEFAULT '{}',
    PRIMARY KEY(guildid, prefix)
);

CREATE TABLE IF NOT EXISTS users (
    userid BIGINT NOT NULL PRIMARY KEY
);
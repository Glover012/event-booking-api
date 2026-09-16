-- Minimal dataset, applied only by `builder <env> up --seed admin` and only when
-- no database volumes are already present
--
-- Load only one admin account and nothing else. Username: admin1, password: test.
--
-- This is NOT the bootstrap admin. The bootstrap password is generated on every
-- boot and written to a secret file, so it can never be used in a test
-- collection. This account exists precisely to be predictable in tests.
\set password '$argon2id$v=19$m=65536,t=3,p=4$CmVj2EaMGV9QU/k27yk3Kw$cGQjzDiUHb+Tn+4GZcYrjggBwIBHW3psCozrfxM35wo'

INSERT INTO users (username, email, first_name, last_name, hashed_password, role) VALUES
    ('admin1', 'admin1@example.com', 'admin1_first_name', 'admin1_last_name', :'password', 'admin');

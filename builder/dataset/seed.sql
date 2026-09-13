-- Seed data, applied only by `builder <env> up --seed` and only when
-- no databse volumes are already present
--
-- Raw SQL on purpose, to avoid using the code that is frequently being refactored at the moment
--
-- Every value follows one pattern, to simplify testing:
--     users: user1, organizer1, admin1, user1@example.com, user1_first_name, user1_last_name
--     events: event1_organizer1, event1_organizer1_description, event1_organizer1_location
--
-- Ids aren't provided and left for SERIAL sequences, then subqueries extract them.
-- If IDs are added manually postgres don't see the sequence and when api insert record
-- to the table afterwards error will occur
--
-- The password of every seeded user is 'test'. 
-- HashedPasswordType is a barrier that raw SQL bypasses, but value has to be a real Argon2
-- hash, since the application load this value back into HashedPassword class, 
-- which rejects anything that its hasher does not recognise as one of its own hashes.
\set password '$argon2id$v=19$m=65536,t=3,p=4$CmVj2EaMGV9QU/k27yk3Kw$cGQjzDiUHb+Tn+4GZcYrjggBwIBHW3psCozrfxM35wo'

INSERT INTO users (username, email, first_name, last_name, hashed_password, role) VALUES
    ('admin1',     'admin1@example.com',     'admin1_first_name',     'admin1_last_name',     :'password', 'admin'),
    ('organizer1', 'organizer1@example.com', 'organizer1_first_name', 'organizer1_last_name', :'password', 'organizer'),
    ('organizer2', 'organizer2@example.com', 'organizer2_first_name', 'organizer2_last_name', :'password', 'organizer'),
    ('user1',      'user1@example.com',      'user1_first_name',      'user1_last_name',      :'password', 'user'),
    ('user2',      'user2@example.com',      'user2_first_name',      'user2_last_name',      :'password', 'user'),
    ('user3',      'user3@example.com',      'user3_first_name',      'user3_last_name',      :'password', 'user'),
    ('user4',      'user4@example.com',      'user4_first_name',      'user4_last_name',      :'password', 'user'),
    ('user5',      'user5@example.com',      'user5_first_name',      'user5_last_name',      :'password', 'user');

-- Both organizers hold four events each, in different states and each organizer have 3 events in future and 1 in the past.
INSERT INTO events (name, description, location, capacity, public, status, starts_at, ends_at, owner_id) VALUES
    ('event1_organizer1', 'event1_organizer1_description', 'event1_organizer1_location', 10, true,  'active',    now() + interval '7 days',  now() + interval '7 days'  + interval '4 hours', (SELECT id FROM users WHERE username = 'organizer1')),
    ('event2_organizer1', 'event2_organizer1_description', 'event2_organizer1_location',  3, true,  'active',    now() + interval '14 days', now() + interval '14 days' + interval '4 hours', (SELECT id FROM users WHERE username = 'organizer1')),
    ('event3_organizer1', 'event3_organizer1_description', 'event3_organizer1_location', 10, false, 'draft',     now() + interval '21 days', now() + interval '21 days' + interval '4 hours', (SELECT id FROM users WHERE username = 'organizer1')),
    ('event4_organizer1', 'event4_organizer1_description', 'event4_organizer1_location', 10, true,  'finished',  now() - interval '30 days', now() - interval '30 days' + interval '4 hours', (SELECT id FROM users WHERE username = 'organizer1')),
    ('event5_organizer2', 'event5_organizer2_description', 'event5_organizer2_location', 10, false, 'active',    now() + interval '10 days', now() + interval '10 days' + interval '4 hours', (SELECT id FROM users WHERE username = 'organizer2')),
    ('event6_organizer2', 'event6_organizer2_description', 'event6_organizer2_location', 10, true,  'locked',    now() + interval '28 days', now() + interval '28 days' + interval '4 hours', (SELECT id FROM users WHERE username = 'organizer2')),
    ('event7_organizer2', 'event7_organizer2_description', 'event7_organizer2_location', 10, true,  'cancelled', now() + interval '42 days', now() + interval '42 days' + interval '4 hours', (SELECT id FROM users WHERE username = 'organizer2')),
    ('event8_organizer2', 'event8_organizer2_description', 'event8_organizer2_location', 10, true,  'finished',  now() - interval '60 days', now() - interval '60 days' + interval '4 hours', (SELECT id FROM users WHERE username = 'organizer2'));

-- One statement per event, so the participant list of each one is readable in a one place
-- The pair (user_id, event_id) is unique only among 'confirmed' rows, because a user may hold a 
-- 'cancelled' and a 'confirmed' booking for the same event, but never two 'confirmed' for the same event

-- event1_organizer1
-- 6 of 10 tickets taken
INSERT INTO bookings (status, ticket_amount, user_id, event_id)
SELECT 'confirmed', 2, users.id, (SELECT id FROM events WHERE name = 'event1_organizer1') FROM users WHERE username IN
    ('user1', 'user2', 'user3');

-- event2_organizer1
-- Sold out, 3 of 3
INSERT INTO bookings (status, ticket_amount, user_id, event_id)
SELECT 'confirmed', 1, users.id, (SELECT id FROM events WHERE name = 'event2_organizer1') FROM users WHERE username IN
    ('user1', 'user2', 'user3');

-- event4_organizer1
-- Past event, 5 of 10
INSERT INTO bookings (status, ticket_amount, user_id, event_id)
SELECT 'confirmed', 1, users.id, (SELECT id FROM events WHERE name = 'event4_organizer1') FROM users WHERE username IN
    ('user1', 'user2', 'user3', 'user4', 'user5');

-- event5_organizer2
-- Private event, 2 of 10
INSERT INTO bookings (status, ticket_amount, user_id, event_id)
SELECT 'confirmed', 1, users.id, (SELECT id FROM events WHERE name = 'event5_organizer2') FROM users WHERE username IN
    ('user1', 'user2');

-- event6_organizer2
-- Booked while the event was still active, 2 of 10
INSERT INTO bookings (status, ticket_amount, user_id, event_id)
SELECT 'confirmed', 1, users.id, (SELECT id FROM events WHERE name = 'event6_organizer2') FROM users WHERE username IN
    ('user4', 'user5');

-- event8_organizer2 confirmed
-- Past event, 6 of 10
INSERT INTO bookings (status, ticket_amount, user_id, event_id)
SELECT 'confirmed', 2, users.id, (SELECT id FROM events WHERE name = 'event8_organizer2') FROM users WHERE username IN
    ('user3', 'user4', 'user5');

-- event1_organizer1
-- Cancelled by two of its current guests
INSERT INTO bookings (status, ticket_amount, user_id, event_id)
SELECT 'cancelled', 1, users.id, (SELECT id FROM events WHERE name = 'event1_organizer1') FROM users WHERE username IN
    ('user1', 'user2');

-- event7_organizer2
-- Cancelled event, so every booking on it was cancelled as well
INSERT INTO bookings (status, ticket_amount, user_id, event_id)
SELECT 'cancelled', 1, users.id, (SELECT id FROM events WHERE name = 'event7_organizer2') FROM users WHERE username IN
    ('user1', 'user2');

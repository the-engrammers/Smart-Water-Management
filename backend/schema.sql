-- Notification preferences table
CREATE TABLE IF NOT EXISTS notification_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    sms_enabled BOOLEAN DEFAULT 0,
    email_enabled BOOLEAN DEFAULT 1,
    sms_number TEXT,
    email_address TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE TABLE control_commands (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    device TEXT,

    command TEXT,

    status TEXT,

    timestamp TEXT

);
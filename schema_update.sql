-- ============================================================
-- BusRes Schema Update Script v2
-- Run in SQL Server Management Studio on bus_reservation DB
-- ============================================================

USE bus_reservation;
GO

-- 1. Add price column to buses
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME='buses' AND COLUMN_NAME='price'
)
BEGIN
    ALTER TABLE buses ADD price INT NULL;
    PRINT 'Added price column to buses.';
END
GO

-- Update price to 1500 where null (separate batch after column exists)
UPDATE buses SET price = 1500 WHERE price IS NULL;
GO

-- 2. Add status column to bookings
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME='bookings' AND COLUMN_NAME='status'
)
BEGIN
    ALTER TABLE bookings ADD status VARCHAR(20) DEFAULT 'confirmed';
    PRINT 'Added status column to bookings.';
END
GO

-- 3. Add bus_id_override column to bookings
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME='bookings' AND COLUMN_NAME='bus_id_override'
)
BEGIN
    ALTER TABLE bookings ADD bus_id_override INT NULL;
    PRINT 'Added bus_id_override column to bookings.';
END
GO

-- 4. Users table
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='users')
BEGIN
    CREATE TABLE users (
        id         INT IDENTITY(1,1) PRIMARY KEY,
        username   VARCHAR(50)  NOT NULL UNIQUE,
        password   VARCHAR(100) NOT NULL,
        role       VARCHAR(20)  NOT NULL CHECK (role IN ('admin','manager','passenger')),
        email      VARCHAR(100),
        created_at DATETIME DEFAULT GETDATE()
    );
    PRINT 'Created users table.';
END
GO

-- Insert hardcoded admin record as reference (login still hardcoded in code)
IF NOT EXISTS (SELECT 1 FROM users WHERE username='admin')
BEGIN
    INSERT INTO users (username, password, role, email)
    VALUES ('admin', 'admin123', 'admin', 'admin@busres.com');
END
GO

-- 5. Promo codes table
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='promo_codes')
BEGIN
    CREATE TABLE promo_codes (
        id           INT IDENTITY(1,1) PRIMARY KEY,
        code         VARCHAR(20)  NOT NULL UNIQUE,
        discount_pct INT          NOT NULL CHECK (discount_pct BETWEEN 1 AND 100),
        max_uses     INT          NOT NULL DEFAULT 100,
        used         INT          NOT NULL DEFAULT 0,
        active       BIT          NOT NULL DEFAULT 1
    );
    PRINT 'Created promo_codes table.';
END
GO

IF NOT EXISTS (SELECT 1 FROM promo_codes WHERE code='SAVE20')
BEGIN
    INSERT INTO promo_codes (code, discount_pct, max_uses, used, active) VALUES
    ('SAVE20',    20, 100,  3, 1),
    ('HALF50',    50,  50,  0, 1),
    ('VIP30',     30, 200,  0, 1),
    ('WELCOME10', 10, 500, 12, 1),
    ('STUDENT25', 25, 200,  8, 1),
    ('FLASH40',   40,  30,  0, 1);
    PRINT 'Seeded promo codes.';
END
GO

-- 6. Payment methods table
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='payment_methods')
BEGIN
    CREATE TABLE payment_methods (
        id      INT IDENTITY(1,1) PRIMARY KEY,
        name    VARCHAR(60) NOT NULL UNIQUE,
        enabled BIT NOT NULL DEFAULT 1
    );
    PRINT 'Created payment_methods table.';
END
GO

IF NOT EXISTS (SELECT 1 FROM payment_methods WHERE name='Credit / Debit Card')
BEGIN
    INSERT INTO payment_methods (name, enabled) VALUES
    ('Credit / Debit Card',              1),
    ('Online Banking',                   1),
    ('Mobile Wallet (JazzCash/EasyPaisa)',1),
    ('Bank Transfer',                    1);
    PRINT 'Seeded payment methods.';
END
GO

-- 7. Payments table
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='payments')
BEGIN
    CREATE TABLE payments (
        id             INT IDENTITY(1,1) PRIMARY KEY,
        booking_id     INT          NOT NULL REFERENCES bookings(id),
        amount_paid    FLOAT        NOT NULL,
        original_price FLOAT        NOT NULL DEFAULT 1500,
        promo_code     VARCHAR(20)  NULL,
        discount_amt   FLOAT        NOT NULL DEFAULT 0,
        method         VARCHAR(60)  NOT NULL,
        method_detail  VARCHAR(100) NULL,
        ticket_no      VARCHAR(20)  NOT NULL,
        invoice_no     VARCHAR(30)  NOT NULL,
        txn_ref        VARCHAR(20)  NOT NULL,
        created_at     DATETIME     DEFAULT GETDATE()
    );
    PRINT 'Created payments table.';
END
GO

-- 8. Feedback table
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='feedback')
BEGIN
    CREATE TABLE feedback (
        id           INT IDENTITY(1,1) PRIMARY KEY,
        passenger_id INT          NOT NULL REFERENCES passengers(id),
        bus_id       INT          NOT NULL REFERENCES buses(id),
        booking_id   INT          NULL     REFERENCES bookings(id),
        rating       INT          NOT NULL CHECK (rating BETWEEN 1 AND 5),
        comment      VARCHAR(500) NULL,
        created_at   DATETIME     DEFAULT GETDATE()
    );
    PRINT 'Created feedback table.';
END
GO

PRINT '================================================';
PRINT 'Schema update complete. All tables created.';
PRINT '================================================';
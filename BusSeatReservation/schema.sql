CREATE DATABASE bus_reservation;
GO

USE bus_reservation;
GO

CREATE TABLE passengers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    cnic VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(15)
);
GO

CREATE TABLE buses (
    id INT IDENTITY(1,1) PRIMARY KEY,
    bus_number VARCHAR(20) NOT NULL,
    route VARCHAR(100),
    total_seats INT DEFAULT 40,
    departure_time DATETIME
);
GO

CREATE TABLE seats (
    id INT IDENTITY(1,1) PRIMARY KEY,
    bus_id INT,
    seat_number INT,
    is_booked BIT DEFAULT 0,
    FOREIGN KEY (bus_id) REFERENCES buses(id)
);
GO

CREATE TABLE bookings (
    id INT IDENTITY(1,1) PRIMARY KEY,
    passenger_id INT,
    seat_id INT,
    booking_date DATETIME DEFAULT GETDATE(),
    status VARCHAR(20) DEFAULT 'confirmed',
    FOREIGN KEY (passenger_id) REFERENCES passengers(id),
    FOREIGN KEY (seat_id) REFERENCES seats(id)
);
GO

CREATE TABLE routes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    from_stop VARCHAR(100),
    to_stop VARCHAR(100),
    distance_km FLOAT
);
GO
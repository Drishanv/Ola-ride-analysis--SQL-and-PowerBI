-- 1. Retrieve all successful bookings
CREATE VIEW successful_bookings AS
SELECT * 
FROM bookings
WHERE booking_status = 'Success';

SELECT * FROM successful_bookings;


-- 2. Find the average ride distance for each vehicle type
CREATE VIEW avg_vehicle_types AS
SELECT vehicle_type, AVG(ride_distance) AS avg_distance
FROM bookings
GROUP BY vehicle_type;

SELECT * FROM avg_vehicle_types;


-- 3. Get the total number of cancelled rides by customers
CREATE VIEW count_cancelled_ride_by_customers AS
SELECT COUNT(*) AS total_cancelled_by_customers
FROM bookings
WHERE booking_status = 'Canceled_Rides_by_Customer';

SELECT * FROM count_cancelled_ride_by_customers;


-- 4. List the top 5 customers who booked the highest number of rides
CREATE VIEW Top_5_customers AS
SELECT customer_id, COUNT(booking_id) AS total_rides
FROM bookings
GROUP BY customer_id
ORDER BY total_rides DESC
LIMIT 5;

SELECT * FROM Top_5_customers;


-- 5. Get the number of rides cancelled by drivers due to personal and car-related issues
CREATE VIEW cancelled_by_drivers AS
SELECT COUNT(*) AS driver_cancel_personal_car
FROM bookings
WHERE Canceled_Rides_by_Driver = 'Personal & Car releated issue';

SELECT * FROM cancelled_by_drivers;


-- 6. Find the maximum and minimum driver ratings for Prime Sedan bookings
CREATE VIEW min_max_driver_ratings AS
SELECT MAX(driver_ratings) AS max_rating,
       MIN(driver_ratings) AS min_rating
FROM bookings
WHERE vehicle_type = 'Prime Sedan';

SELECT * FROM min_max_driver_ratings;


-- 7. Retrieve all rides where payment was made using UPI
CREATE VIEW Pay_UPI AS
SELECT * 
FROM bookings
WHERE payment_method = 'UPI';

SELECT * FROM Pay_UPI;


-- 8. Find the average customer rating per vehicle type
CREATE VIEW Avg_Customer_Rating AS
SELECT vehicle_type, AVG(customer_rating) AS Avg_Cust_Rating
FROM bookings
GROUP BY vehicle_type;

SELECT * FROM Avg_Customer_Rating;


-- 9. Calculate the total booking value of rides completed successfully
CREATE VIEW Total_values AS
SELECT SUM(booking_value) AS total_success_value
FROM bookings
WHERE booking_status = 'Success';

SELECT * FROM Total_values;


-- 10. List all incomplete rides along with the reason
CREATE VIEW incomplete_rides AS
SELECT booking_id, Incomplete_Rides_Reason
FROM bookings
WHERE Incomplete_Rides = 'Yes';

SELECT * FROM incomplete_rides;

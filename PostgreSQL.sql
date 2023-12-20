-- Создание таблицы user
CREATE TABLE user (
    user_id INT PRIMARY KEY,
    locale VARCHAR(50),
    tl TINYINT,
    country VARCHAR(50),
    registered_time TIMESTAMP
);

-- Добавление записей в таблицу user
INSERT INTO user (user_id, locale, tl, country, registered_time)
VALUES (1, 'en_US', 3, 'US', '2023-11-01 00:00:00'),
       (2, 'ru_RU', 4, 'RU', '2023-11-02 00:00:00'),
       (3, 'fr_FR', 5, 'FR', '2023-11-03 00:00:00');

-- Создание таблицы purchase
CREATE TABLE purchase (
    user_id INT,
    cart_id INT PRIMARY KEY,
    create_time TIMESTAMP,
    purchase_time TIMESTAMP,
    subscription BOOLEAN,
    price INT,
    billing_method INT
);

-- Добавление записей в таблицу purchase
INSERT INTO purchase (user_id, cart_id, create_time, purchase_time, subscription, price, billing_method)
VALUES (1, 101, '2023-11-01 00:00:00', '2023-11-01 00:50:00', false, 10, 1),
       (1, 102, '2023-11-01 01:00:00', '2023-11-01 01:50:00', true, 20, 2),
       (2, 201, '2023-11-02 00:00:00', '2023-11-02 00:50:00', false, 30, 3),
       (3, 301, '2023-11-03 00:00:00', '2023-11-03 00:50:00', true, 40, 4);

-- Проверим правильность таблиц
SELECT * from user;
SELECT * from purchase;


-- 1. Посчитать nDAU (New Daily Active Users) по языковым локалям для возрастов от 3 до 5:
SELECT locale, COUNT(DISTINCT user_id) AS nDAU
FROM user
WHERE tl BETWEEN 3 AND 5
GROUP BY locale;

-- 2. Вывести среднее и медианное количество пользователей в день по странам для пользователей, которые зарегистрировались в ноябре 2023 года:
-- Среднее количество пользователей в день
SELECT country, AVG(count) AS average_users
FROM (
    SELECT country, DATE(registered_time) AS date, COUNT(user_id) AS count
    FROM user
    WHERE strftime('%Y', registered_time) = '2023' AND strftime('%m', registered_time) = '11'
    GROUP BY country, date
) AS subquery
GROUP BY country;

-- Медианное количество пользователей в день
-- PostgreSQL не имеет встроенной функции для медианы, поэтому воспользуемся агрегатной функция percentile_cont
SELECT country, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY count) AS median_users
FROM (
    SELECT country, DATE(registered_time) AS date, COUNT(user_id) AS count
    FROM user
    WHERE EXTRACT('year' FROM registered_time) = 2023 AND EXTRACT('month' FROM registered_time) = 11
    GROUP BY country, date
) AS subquery
GROUP BY country;

-- 3. Вывести средний чек (средняя стоимость корзины) по странам регистраций пользователей:
SELECT u.country, AVG(p.price) AS average_receipt
FROM user AS u
JOIN purchase AS p ON u.user_id = p.user_id
GROUP BY u.country;

-- 4. Вывести время в минутах между каждыми двумя последовательными оплаченными корзинами для пользователя:
SELECT user_id, cart_id, EXTRACT(EPOCH FROM (purchase_time - LAG(purchase_time) OVER (PARTITION BY user_id ORDER BY purchase_time))) / 60 AS minutes_between_purchases
FROM purchase
ORDER BY user_id, purchase_time;

FLUSH PRIVILEGES;
DROP DATABASE `dbfb`;

CREATE DATABASE IF NOT EXISTS dbfb;
USE dbfb;

CREATE TABLE IF NOT EXISTS admins (
    admin_username VARCHAR(20) NOT NULL,
    admin_password VARCHAR(20) NOT NULL,
    PRIMARY KEY (admin_username)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS publishers (
    publisher_username VARCHAR(20) NOT NULL,
    publisher_password VARCHAR(20) NOT NULL,
    publisher_sales INT DEFAULT 0,
    PRIMARY KEY (publisher_username)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS authors (
    author_username VARCHAR(20) NOT NULL,
    author_password VARCHAR(20) NOT NULL,
    author_sales INT DEFAULT 0,
    PRIMARY KEY (author_username)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS users (
    user_username VARCHAR(20) NOT NULL,
    user_password VARCHAR(20) NOT NULL,
    PRIMARY KEY (user_username)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS books (
    book_id INT NOT NULL AUTO_INCREMENT,
    book_title VARCHAR(20) NOT NULL,
    author_username VARCHAR(20) NOT NULL,
    publisher_username VARCHAR(20) NOT NULL,
    price INT DEFAULT 699,
    book_sales INT DEFAULT 0,
    PRIMARY KEY (book_id),
    KEY author_username (author_username),
    KEY publisher_username (publisher_username),
    CONSTRAINT books_ibfk_1 FOREIGN KEY (author_username) REFERENCES authors (author_username) ON DELETE CASCADE,
    CONSTRAINT books_ibfk_2 FOREIGN KEY (publisher_username) REFERENCES publishers (publisher_username) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS keywords (
    book_id INT NOT NULL,
    keyword VARCHAR(20) NOT NULL,
    PRIMARY KEY (book_id, keyword),
    KEY book_id (book_id),
    CONSTRAINT keywords_ibfk_1 FOREIGN KEY (book_id) REFERENCES books (book_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sales (
    sale_id INT NOT NULL AUTO_INCREMENT,
    user_username VARCHAR(20) NOT NULL, 
    book_id INT NOT NULL,
    order_status VARCHAR(10) DEFAULT 'pending',
    PRIMARY KEY (sale_id),
    KEY user_username (user_username),
    KEY book_id (book_id),
    CONSTRAINT sales_ibfk_1 FOREIGN KEY (user_username) REFERENCES users (user_username) ON DELETE CASCADE,
    CONSTRAINT sales_ibfk_2 FOREIGN KEY (book_id) REFERENCES books (book_id) ON DELETE CASCADE,
    CHECK (order_status IN ('pending', 'delivered'))
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS requests (
    book_title varchar(20) NOT NULL,
    author_username VARCHAR(20) NOT NULL,
    publisher_username VARCHAR(20) NOT NULL,
    request_status VARCHAR(10) DEFAULT 'pending',
    PRIMARY KEY ( book_title, author_username, publisher_username),
    KEY author_username (author_username),
    KEY publisher_username (publisher_username),
    CONSTRAINT requests_ibfk_1 FOREIGN KEY (author_username) REFERENCES authors (author_username) ON DELETE CASCADE,
    CONSTRAINT requests_ibfk_2 FOREIGN KEY (publisher_username) REFERENCES publishers (publisher_username) ON DELETE CASCADE,
    CHECK (request_status IN ('pending', 'approved', 'rejected'))
) ENGINE=InnoDB;



-- ===============================================================================================
DELIMITER //
CREATE FUNCTION is_admin(username VARCHAR(20)) RETURNS BOOLEAN deterministic
    BEGIN
        DECLARE admin_count INT;
        SELECT COUNT(*) INTO admin_count FROM admins WHERE admin_username = username;
        RETURN (admin_count > 0);
END //

CREATE FUNCTION is_author(username VARCHAR(20)) RETURNS BOOLEAN deterministic
    BEGIN
        DECLARE author_count INT;
        SELECT COUNT(*) INTO author_count FROM authors WHERE author_username = username;
        RETURN (author_count > 0);
END //

CREATE FUNCTION is_book(id int) RETURNS BOOLEAN deterministic
    BEGIN
        DECLARE book_count INT;
        SELECT COUNT(*) INTO book_count FROM books WHERE book_id = id;
        RETURN (book_count > 0);
END //

CREATE FUNCTION bid_to_pub(id int) RETURNS varchar(20) deterministic
    BEGIN
        DECLARE pub varchar(20);
        SELECT publisher_username INTO pub FROM books WHERE book_id = id;
        return pub;
END //

CREATE FUNCTION bid_to_auth(id int) RETURNS varchar(20) deterministic
    BEGIN
        DECLARE auth varchar(20);
        SELECT author_username INTO auth FROM books WHERE book_id = id;
        return auth;
END //


DELIMITER ;
-- ===============================================================================================

DELIMITER //

CREATE PROCEDURE make_publisher(IN admin_username VARCHAR(20), IN target_username VARCHAR(20))
    BEGIN
    IF is_admin(admin_username) THEN
        INSERT INTO publishers (username, password) VALUES (target_username, 'default_password');
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You do not have the privilege to make someone a publisher.';
    END IF;
END //

CREATE PROCEDURE fill_keyword(IN book_id int, IN keyword VARCHAR(20))
    BEGIN
    IF is_book(book_id) THEN
        INSERT INTO keywords (book_id, keyword) VALUES (book_id, keyword);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Book does not exist';
    END IF;
END //

DELIMITER ;
-- ===============================================================================================
USE dbfb;

DELIMITER //

CREATE TRIGGER handle_book_request AFTER update ON requests FOR EACH ROW
    BEGIN
    DECLARE rstatus VARCHAR(10);
    SELECT request_status INTO rstatus FROM requests WHERE book_title = NEW.book_title AND author_username = NEW.author_username AND publisher_username = NEW.publisher_username;

    IF rstatus = 'approved' THEN
        INSERT INTO books (book_title, author_username, publisher_username)
        VALUES (NEW.book_title, NEW.author_username, NEW.publisher_username);
    END IF;
END //

CREATE TRIGGER handle_order AFTER update ON sales FOR EACH ROW
    BEGIN
    DECLARE rstatus VARCHAR(10);
    SELECT order_status INTO rstatus FROM sales WHERE sale_id = NEW.sale_id;

    IF rstatus = 'delivered' THEN
        UPDATE publishers SET publisher_sales = publisher_sales + 1
        WHERE publisher_username = bid_to_pub(NEW.book_id);

        UPDATE authors SET author_sales = author_sales + 1
        WHERE author_username =  bid_to_auth(NEW.book_id);

        UPDATE books SET book_sales = book_sales + 1
        WHERE book_id = NEW.book_id;
    END IF;
END //


DELIMITER ;

-- ===============================================================================================
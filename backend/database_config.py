# Database Settings
HOST = 'localhost'
#USER = 'debian-sys-maint'
#PASSWORD = 'FLOWzE9D0rM3WpT0'
USER = 'root'
PASSWORD = None
DATABASE = 'db'

# Tables
TABLES = {}
TABLES['manufacturers'] = (
    "CREATE TABLE manufacturers ("
    " manufacturer_id INT NOT NULL AUTO_INCREMENT,"
    " manufacturer_name VARCHAR(256) NOT NULL,"

    " CONSTRAINT manufacturers_pk PRIMARY KEY (manufacturer_id)"
    ")"
)

TABLES['products'] = (
    "CREATE TABLE products ("
    " product_id INT NOT NULL AUTO_INCREMENT,"
    " product_name VARCHAR(256) NOT NULL,"
    " product_brand VARCHAR(256) NOT NULL,"
    " product_category TEXT NOT NULL,"
    " manufacturer_id INT NOT NULL,"

    " CONSTRAINT products_pk PRIMARY KEY (product_id)"
    ")"
)

TABLES['users'] = (
    "CREATE TABLE users ("
    " user_id INT NOT NULL AUTO_INCREMENT,"
    " username VARCHAR(256),"
    " phone_number VARCHAR(256),"

    " CONSTRAINT users_pk PRIMARY KEY (user_id)"
    ")"
)

TABLES['reviews'] = (
    "CREATE TABLE reviews ("
    " id INT NOT NULL AUTO_INCREMENT,"
    " title TEXT,"
    " text TEXT,"
    " rating INT,"
    " num_helpful INT,"
    " recommend INT,"
    " date_added DATETIME,"
    " date_updated DATETIME,"
    " product_id INT NOT NULL,"
    " user_id INT NOT NULL,"

    " CONSTRAINT reviews_pk PRIMARY KEY (id)," 
    " CONSTRAINT product_fk FOREIGN KEY (product_id) REFERENCES products(product_id)"
    ")"
)

### Summary Tables ###
TABLES['summary_ratings'] = (
    "CREATE TABLE summary_ratings ("
    " product_id INT NOT NULL,"
    " product_name VARCHAR(256) NOT NULL,"
    " cnt INT,"
    " sum_ratings INT,"
    
    " CONSTRAINT summary_rating_pk PRIMARY KEY (product_id)"
    ")"
)

TABLES['summary_recommended'] = (
    "CREATE TABLE summary_recommended ("
    " product_id INT NOT NULL,"
    " product_name VARCHAR(256) NOT NULL,"
    " num_recommended INT,"
    
    " CONSTRAINT summary_recommended_pk PRIMARY KEY (product_id)"
    ")"
)

# Triggers
TRIGGERS = {}
TRIGGERS['insert_review_summary_ratings'] = (
    "CREATE TRIGGER insert_review_summary_ratings AFTER INSERT ON reviews "
    "FOR EACH ROW "
    "BEGIN "
    " INSERT INTO summary_ratings (product_id, product_name, cnt, sum_ratings) VALUES (NEW.product_id, (SELECT product_name FROM products WHERE NEW.product_id = products.product_id), 1, NEW.rating) "
    " ON DUPLICATE KEY UPDATE cnt = cnt + 1, sum_ratings = sum_ratings + NEW.rating; "
    "END"
)

TRIGGERS['insert_review_summary_recommended'] = (
    "CREATE TRIGGER insert_review_summary_recommended AFTER INSERT ON reviews "
    "FOR EACH ROW "
    "BEGIN "
    " INSERT INTO summary_recommended (product_id, product_name, num_recommended) VALUES(NEW.product_id, (SELECT product_name FROM products WHERE NEW.product_id = products.product_id), NEW.recommend) "
    " ON DUPLICATE KEY UPDATE num_recommended = num_recommended + NEW.recommend;"
    "END"
)

TRIGGERS['update_review_summary_ratings'] = (
    "CREATE TRIGGER update_review_summary_ratings AFTER UPDATE ON reviews "
    "FOR EACH ROW "
    "BEGIN "
    " UPDATE summary_ratings SET sum_ratings = sum_ratings+(NEW.rating-OLD.rating) WHERE product_id=NEW.product_id;"
    "END"
)

TRIGGERS['update_review_summary_recommended'] = (
    "CREATE TRIGGER update_review_summary_recommended AFTER UPDATE ON reviews "
    "FOR EACH ROW "
    "BEGIN "
    " UPDATE summary_recommended SET num_recommended = num_recommended+(NEW.recommend-OLD.recommend) WHERE product_id=NEW.product_id;"
    "END"
)
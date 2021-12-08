from collections import defaultdict
from mysql.connector import pooling
import mysql.connector
import time

from database_config import *

# Database
class DB:
    def __init__(self, reset, ivm, ivm_cache):
        self.cnx_pool = None
        self.optimizations = {
            "ivm": ivm, # Incremental View Maintenance
            "ivm_cache": ivm_cache, # IVM Summary Tables Cache
        }
        
        # Setup
        self.setup(reset=reset)

    # Create Database & Tables
    def setup(self, reset=False):
        # Database
        cnx = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database='mysql')
        cursor = cnx.cursor(prepared=True)

        if reset:
            cursor.execute("DROP DATABASE IF EXISTS {}".format(DATABASE))
        cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(DATABASE))

        cnx.commit()
        cnx.close()

        # SQL Pool
        self.cnx_pool = mysql.connector.pooling.MySQLConnectionPool(
            host=HOST, user=USER, password=PASSWORD, database=DATABASE, 
            pool_name = "mypool", pool_size = mysql.connector.pooling.CNX_POOL_MAXSIZE
        )

        # Tables
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor()

        for name, ddl in TABLES.items():
            print("Creating table {}: ".format(name), end='')
            try:
                cursor.execute(ddl)
            except mysql.connector.Error as err:
                if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
                    print("Table already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")

        cnx.commit()
        cnx.close()

        # Cache
        if self.optimizations["ivm"] and self.optimizations["ivm_cache"]:
            self.summary_tables = {
                "summary_ratings": defaultdict(lambda: defaultdict(int)),
                "summary_recommended": defaultdict(lambda: defaultdict(int)),
            }

        # Cache
        if self.optimizations["ivm"]:
            if self.optimizations["ivm_cache"]:
                self.disk_to_cache()
            else:
                for name, ddl in TRIGGERS.items():
                    cursor.execute(ddl)


    # Shutdown
    def shutdown(self):
        if self.optimizations["ivm"] and self.optimizations["ivm_cache"]:
            self.cache_to_disk()

    # Cache
    def disk_to_cache(self):
        if self.optimizations["ivm"] and self.optimizations["ivm_cache"]:
            cnx = self.cnx_pool.get_connection()
            cursor = cnx.cursor(prepared=True)

            # Summmary Tables Cache
            cursor.execute("SELECT * FROM summary_ratings")
            results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
            for product in results:
                self.summary_tables["summary_ratings"][product["product_id"]]["product_id"] = product["product_id"]
                self.summary_tables["summary_ratings"][product["product_id"]]["product_name"] = product["product_name"]
                self.summary_tables["summary_ratings"][product["product_id"]]["cnt"] = product["cnt"]
                self.summary_tables["summary_ratings"][product["product_id"]]["sum_ratings"] = product["sum_ratings"]
                self.summary_tables["summary_ratings"][product["product_id"]]["avg_rating"] = product["sum_ratings"] / product["cnt"]

            cursor.execute("SELECT * FROM summary_recommended")
            results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
            for product in results:
                self.summary_tables["summary_recommended"][product["product_id"]]["product_id"] = product["product_id"]
                self.summary_tables["summary_recommended"][product["product_id"]]["product_name"] = product["product_name"]
                self.summary_tables["summary_recommended"][product["product_id"]]["num_recommended"] = product["num_recommended"]
            
            cnx.commit()
            cnx.close()

    def cache_to_disk(self):
        if self.optimizations["ivm"] and self.optimizations["ivm_cache"]:
            cnx = self.cnx_pool.get_connection()
            cursor = cnx.cursor(prepared=True)

            for product_id, product in self.summary_tables["summary_ratings"].items():
                insert_summary_ratings = "INSERT INTO summary_ratings (product_id, product_name, cnt, sum_ratings) VALUES(?, ?, ?, ?) " + \
                            "ON DUPLICATE KEY UPDATE cnt = ?, sum_ratings = ?"
                insert_data = (product_id, product["product_name"], product["cnt"], product["sum_ratings"], product["cnt"], product["sum_ratings"])
                cursor.execute(insert_summary_ratings, insert_data)

                insert_recom = "INSERT INTO summary_recommended (product_id, product_name, num_recommended) VALUES(?, ?, ?) " + \
                        "ON DUPLICATE KEY UPDATE num_recommended = ?"
                insert_data = (product_id, product["product_name"], product["num_recommended"], product["num_recommended"])
                cursor.execute(insert_recom, insert_data)

            cnx.commit()
            cnx.close()
    
    # Helper Function
    def _get_id_insert_if_needed(self, select_query, select_data, insert_query, insert_data):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)
        
        cursor.execute(select_query, select_data)
        results = list(cursor)
        if len(results) == 0:
            cursor.execute(insert_query, insert_data)
            id = cursor.lastrowid
        else:
            id = results[0][0]

        cursor.close()
        cnx.commit()
        cnx.close()
        return id
    
    # Manufacturers SQL Queries
    def get_manufacturer_id(self, manufacturer_name):
        select_manufacturer_by_name = "SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name=?"
        select_data = (manufacturer_name,)

        insert_manufacturer = "INSERT INTO manufacturers (manufacturer_name) VALUES (?)"
        insert_data = (manufacturer_name,)

        return self._get_id_insert_if_needed(select_manufacturer_by_name, select_data, insert_manufacturer, insert_data)

    def get_manufacturers(self):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)
        
        cursor.execute("SELECT manufacturer_name FROM manufacturers")
        results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        cursor.close()
        cnx.commit()
        cnx.close()
        return results

    # Products SQL Queries
    def get_product_id(self, product_name, product_brand, product_category, manufacturer_id):
        select_product_by_name = "SELECT product_id FROM products WHERE product_name=?"
        select_data = (product_name,)

        insert_product = "INSERT INTO products (product_name, product_brand, product_category, manufacturer_id) VALUES (?, ?, ?, ?)"
        insert_data = (product_name, product_brand, product_category, manufacturer_id)
        return self._get_id_insert_if_needed(select_product_by_name, select_data, insert_product, insert_data)
    
    def get_products(self):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)
        
        cursor.execute("SELECT product_id, product_name FROM products")
        results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        cursor.close()
        cnx.commit()
        cnx.close()
        return results

    def get_product_categories(self):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)
        
        cursor.execute("SELECT DISTINCT product_category FROM products")
        results = list(cursor)
        for i in range(0, len(results)):
            results[i] = results[i][0]

        cursor.close()
        cnx.commit()
        cnx.close()
        return results

    # Users SQL Queries
    def get_user_id(self, username):
        select_user_by_username = "SELECT user_id FROM users WHERE username=?"
        select_data = (username,)
        insert_user = "INSERT INTO users (username) VALUES (?)"
        insert_data = (username,)
        return self._get_id_insert_if_needed(select_user_by_username, select_data, insert_user, insert_data)

    def get_users(self):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)
        
        cursor.execute("SELECT user_id, username FROM users")
        results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        cursor.close()
        cnx.commit()
        cnx.close()
        return results

    # Reviews SQL Queries
    def insert_review(self, review):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)

        # Insert Review
        insert_review = "INSERT INTO reviews (title, text, rating, num_helpful, recommend, date_added, date_updated, user_id, product_id) VALUES" + \
                        "(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        insert_data = (review["title"], review["text"], review["rating"], review["num_helpful"], review["recommend"], review["date_added"], review["date_updated"], review["user_id"], review["product_id"])
        cursor.execute(insert_review, insert_data)

        # Summary Tables
        if self.optimizations["ivm"]:
            if self.optimizations["ivm_cache"]:
                self.summary_tables["summary_ratings"][review["product_id"]]["product_id"] = review["product_id"]
                self.summary_tables["summary_ratings"][review["product_id"]]["product_name"] = review["product_name"]
                self.summary_tables["summary_ratings"][review["product_id"]]["cnt"] += 1
                self.summary_tables["summary_ratings"][review["product_id"]]["sum_ratings"] += review["rating"]
                self.summary_tables["summary_ratings"][review["product_id"]]["avg_rating"] = self.summary_tables["summary_ratings"][review["product_id"]]["sum_ratings"] / self.summary_tables["summary_ratings"][review["product_id"]]["cnt"]

                self.summary_tables["summary_recommended"][review["product_id"]]["product_id"] = review["product_id"]
                self.summary_tables["summary_recommended"][review["product_id"]]["product_name"] = review["product_name"]
                self.summary_tables["summary_recommended"][review["product_id"]]["num_recommended"] += review["recommend"]

        cursor.close()
        cnx.commit()
        cnx.close()
    
    def batch_insert_reviews(self, reviews):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)

        # Batch
        data = []
        for review in reviews:
            data.append([])
            data[-1].append(review["title"])
            data[-1].append(review["text"])
            data[-1].append(review["rating"])
            data[-1].append(review["num_helpful"])
            data[-1].append(review["recommend"])
            data[-1].append(review["date_added"])
            data[-1].append(review["date_updated"])
            data[-1].append(review["user_id"])
            data[-1].append(review["product_id"])

        # Insert Review
        batch_insert_reviews = "INSERT INTO reviews (title, text, rating, num_helpful, recommend, date_added, date_updated, user_id, product_id) VALUES" + \
                               "(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.executemany(batch_insert_reviews, data)

        # Summary Tables
        if self.optimizations["ivm"]:
            if self.optimizations["ivm_cache"]:
                for review in reviews:
                    self.summary_tables["summary_ratings"][review["product_id"]]["product_id"] = review["product_id"]
                    self.summary_tables["summary_ratings"][review["product_id"]]["product_name"] = review["product_name"]
                    self.summary_tables["summary_ratings"][review["product_id"]]["cnt"] += 1
                    self.summary_tables["summary_ratings"][review["product_id"]]["sum_ratings"] += review["rating"]
                    self.summary_tables["summary_ratings"][review["product_id"]]["avg_rating"] = self.summary_tables["summary_ratings"][review["product_id"]]["sum_ratings"] / self.summary_tables["summary_ratings"][review["product_id"]]["cnt"]

                    self.summary_tables["summary_recommended"][review["product_id"]]["product_id"] = review["product_id"]
                    self.summary_tables["summary_recommended"][review["product_id"]]["product_name"] = review["product_name"]
                    self.summary_tables["summary_recommended"][review["product_id"]]["num_recommended"] += review["recommend"]

        cursor.close()
        cnx.commit()
        cnx.close()

    def upvote_review(self, id):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)

        cursor.execute("UPDATE reviews SET num_helpful=num_helpful+1 WHERE id={}".format(id))

        cursor.close()
        cnx.commit()
        cnx.close()

    # Aggregate SQL Queries
    def top_rated_products(self, count):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)

        results = []
        if self.optimizations["ivm"]:
            if self.optimizations["ivm_cache"]:
                results = sorted(self.summary_tables["summary_ratings"].values(), key=lambda x: x["avg_rating"], reverse=True)[:int(count)]
            else:
                cursor.execute((
                    "SELECT product_id, product_name, sum_ratings / cnt as avg_rating "
                    "FROM summary_ratings "
                    "ORDER BY avg_rating DESC LIMIT {}"
                ).format(count))
                results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        else:
            cursor.execute((
                "SELECT product_id, product_name, avg_rating "
                "FROM "
                    "(SELECT product_id, avg(rating) as avg_rating "
                    "FROM reviews "
                    "GROUP BY product_id "
                    "ORDER BY avg_rating DESC LIMIT {}) as foo "
                "NATURAL JOIN products "
                "ORDER BY avg_rating DESC"
            ).format(count))
            results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        cursor.close()
        cnx.commit()
        cnx.close()
        return results

    def top_recommended_products(self, count):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)

        results = []
        if self.optimizations["ivm"]:
            if self.optimizations["ivm_cache"]:
                results = sorted(self.summary_tables["summary_recommended"].values(), key=lambda x: x["num_recommended"], reverse=True)[:int(count)]
            else:
                cursor.execute((
                    "SELECT product_id, product_name, num_recommended "
                    "FROM summary_recommended "
                    "ORDER BY num_recommended DESC LIMIT {}"
                ).format(count))
                results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        else:
            cursor.execute((
                "SELECT product_id, product_name, num_recommended "
                "FROM "
                    "(SELECT product_id, sum(recommend) as num_recommended "
                    "FROM reviews "
                    "GROUP BY product_id "
                    "ORDER BY num_recommended DESC LIMIT {}) as foo "
                "NATURAL JOIN products "
                "ORDER BY num_recommended DESC"
            ).format(count))
            results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        cursor.close()
        cnx.commit()
        cnx.close()
        return results
    
    def top_rated_manufacturers(self, count):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)

        query = (
            "SELECT manufacturer_id, manufacturer_name, avg_rating "
            "FROM "
                "(SELECT manufacturer_id, avg(rating) as avg_rating "
                "FROM (SELECT manufacturer_id, product_id, rating FROM reviews NATURAL JOIN products) as foo "
                "GROUP BY manufacturer_id "
                "ORDER BY avg_rating DESC LIMIT {}) as bar "
            "NATURAL JOIN manufacturers "
            "ORDER BY avg_rating DESC"
        ).format(count)
        cursor.execute(query)
        results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        cursor.close()
        cnx.commit()
        cnx.close()
        return results

    def most_active_users(self, count):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)

        cursor.execute((
            "SELECT user_id, username, num_reviews "
            "FROM "
                "(SELECT user_id, count(*) as num_reviews "
                "FROM reviews "
                "GROUP BY user_id "
                "ORDER BY num_reviews DESC LIMIT {}) as bar "
            "NATURAL JOIN users "
            "ORDER BY num_reviews DESC"
        ).format(count))
        results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        cursor.close()
        cnx.commit()
        cnx.close()
        return results
    
    def most_helpful_reviews(self, product_id, count):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)

        cursor.execute("SELECT * FROM reviews WHERE product_id={} ORDER BY num_helpful DESC LIMIT {}".format(product_id, count))
        results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        cursor.close()
        cnx.commit()
        cnx.close()
        return results

    def most_recent_reviews(self, product_id, count):
        cnx = self.cnx_pool.get_connection()
        cursor = cnx.cursor(prepared=True)

        cursor.execute("SELECT * FROM reviews WHERE product_id={} ORDER BY date_updated DESC, num_helpful DESC LIMIT {}".format(product_id, count))
        results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        cursor.close()
        cnx.commit()
        cnx.close()
        return results
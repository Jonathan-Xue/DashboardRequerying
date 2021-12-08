from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import pandas as pd
import random
import time

from db_sql import *

# Initialize
app = Flask(__name__)
CORS(app, support_credentials=True)

sqlObject = DB(reset=False, ivm=True, ivm_cache=True)
currEntry = 1

# Helper Function
def random_date():
    return datetime.fromtimestamp(random.randint(1, int(time.time()))).strftime('%Y-%m-%d %H:%M:%S')

def parse_csv_row(row):
    global sqlObject

    # NAN -> 0
    nanToZero = lambda x: 0 if math.isnan(x) else x
    row['reviews.rating'] = int(row['reviews.rating'])
    row['reviews.numHelpful'] = nanToZero(row['reviews.numHelpful'])
    row['reviews.doRecommend'] = nanToZero(row['reviews.doRecommend'])

    # 'YYYY-MM-DDTHH:MM:SSZ' -> 'YYYY-MM-DD HH:MM:SS'
    date = random_date()

    # Primary Categories -> Primary Category
    row['primaryCategories'] = row['primaryCategories'].split(',')[0]
    
    # Review
    user_id = sqlObject.get_user_id(row['reviews.username'])
    manufacturer_id = sqlObject.get_manufacturer_id(row['manufacturer'])
    product_id = sqlObject.get_product_id(row['name'], row['brand'], row['primaryCategories'], manufacturer_id)

    return {
        'title': row['reviews.title'],
        'text': row["reviews.text"],
        'rating': row["reviews.rating"],
        'num_helpful': row["reviews.numHelpful"],
        'recommend': row["reviews.doRecommend"],
        'date_added': date,
        'date_updated': date,
        'user_id': user_id,
        'product_id': product_id,
        'product_name': row['name']
    }

# Routes
@app.route("/")
def default():
    return jsonify()

# Setup
@app.route("/reset", methods=['GET', 'POST'])
def reset():
    global sqlObject, currEntry

    sqlObject.setup(reset=True)

    return jsonify()

# SQL Post
@app.route("/autoinsert", methods=['GET', 'POST'])
def autoinsert():
    global sqlObject, currEntry
    count = request.args.get('count', default = 1, type = int)

    df = pd.read_csv('data.csv', nrows=count, skiprows=range(1, currEntry))
    if len(df.index) == 0:
        pass
    elif len(df.index) == 1:
        sqlObject.insert_review(parse_csv_row(next(df.iterrows())[1]))
    else:
        tmp = []
        for _, row in df.iterrows():
            tmp.append(parse_csv_row(row))
        sqlObject.batch_insert_reviews(tmp)
    currEntry += count

    return jsonify()

@app.route("/insert-review", methods=['GET', 'POST'])
def insert_review():
    global sqlObject, currEntry
    review = {
        'title': request.get_json()['title'],
        'text': request.get_json()['text'],
        'rating': request.get_json()['rating'],
        'num_helpful': request.get_json()['num_helpful'],
        'recommend': request.get_json()['recommend'],
        'date_added': request.get_json()['date_added'],
        'date_updated': request.get_json()['date_updated'],
        'user_id': request.get_json()['user_id'],
        'product_id': request.get_json()['product_id'],
    }

    sqlObject.insert_review(review)
    return jsonify()

@app.route("/upvote-review", methods=['GET', 'POST'])
def upvote_review():
    global sqlObject
    id = request.get_json()['id']

    sqlObject.upvote_review(id)
    return jsonify()

# SQL Get
@app.route("/users", methods=['GET'])
def users():
    global sqlObject
    
    data = sqlObject.get_users()
    return jsonify(data=data)

@app.route("/products", methods=['GET'])
def products():
    global sqlObject
    
    data = sqlObject.get_products()
    return jsonify(data=data)

@app.route("/product-categories", methods=['GET'])
def product_categories():
    global sqlObject
    
    data = sqlObject.get_product_categories()
    return jsonify(data=data)

@app.route("/manufacturers", methods=['GET'])
def manufacturers():
    global sqlObject
    
    data = sqlObject.get_manufacturers()
    return jsonify(data=data)

# SQL Aggregates
@app.route("/top-rated-products", methods=['GET'])
def top_rated_products():
    global sqlObject
    count = request.args['count']

    data = sqlObject.top_rated_products(count)
    return jsonify(data=data)

@app.route("/top-recommended-products", methods=['GET'])
def top_recommended_products():
    global sqlObject
    count = request.args['count']

    data = sqlObject.top_recommended_products(count)
    return jsonify(data=data)

@app.route("/top-rated-manufacturers", methods=['GET'])
def top_rated_manufacturers():
    global sqlObject
    count = request.args['count']

    data = sqlObject.top_rated_manufacturers(count)
    return jsonify(data=data)

@app.route("/most-active-users", methods=['GET'])
def most_active_users():
    global sqlObject
    count = request.args['count']

    data = sqlObject.most_active_users(count)
    return jsonify(data=data)

@app.route("/most-helpful-reviews", methods=['GET'])
def most_helpful_reviews():
    global sqlObject
    product_id = request.args['product_id']
    count = request.args['count']

    data = sqlObject.most_helpful_reviews(product_id, count)
    return jsonify(data=data)

@app.route("/most-recent-reviews", methods=['GET'])
def most_recent_reviews():
    global sqlObject
    product_id = request.args['product_id']
    count = request.args['count']

    data = sqlObject.most_recent_reviews(product_id, count)
    return jsonify(data=data)
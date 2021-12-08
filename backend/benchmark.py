from datetime import datetime
import argparse
import csv
import math
import matplotlib.pyplot as plt
import pandas as pd
import random
import statistics
import time

from db_sql import *

# Config
DB_CONFIGS = {
    'naive': { 'ivm': False, 'ivm_cache': False },
    'ivm' : { 'ivm': True, 'ivm_cache': False },
    'ivm_cache': { 'ivm': True, 'ivm_cache': True },
}

INSERT_ARR = [1, 10, 100, 1000]

# Helper Functions
def random_date():
    return datetime.fromtimestamp(random.randint(1, int(time.time()))).strftime('%Y-%m-%d %H:%M:%S')

def parse_csv_row(sqlObject, row):
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

# Insert Benchmarks
def insert_benchmarks():
    for config_name, config in DB_CONFIGS.items():
        for num_insert in INSERT_ARR:
            curr_row = 1
            with open('benchmarks/insert/' + config_name + '-' + str(num_insert) + '.csv', 'w') as fp:
                csv_writer = csv.writer(fp)
                csv_writer.writerow(['database_entries', 'insert'])

                # Database
                sqlObject = DB(reset=True, ivm=config['ivm'], ivm_cache=config['ivm_cache'])

                # Data
                while True:
                    insert_time = None

                    df = pd.read_csv('data.csv', nrows=num_insert, skiprows=range(1, curr_row))
                    if len(df.index) == 0:
                        break
                    elif len(df.index) == 1:
                        start = time.time()
                        sqlObject.insert_review(parse_csv_row(sqlObject, next(df.iterrows())[1]))
                        end = time.time()
                        insert_time = end - start
                    else:
                        tmp = []
                        for _, row in df.iterrows():
                            tmp.append(parse_csv_row(sqlObject, row))
                        
                        start = time.time()
                        sqlObject.batch_insert_reviews(tmp)
                        end = time.time()
                        insert_time = end - start
                
                    # CSV
                    csv_writer.writerow([curr_row + len(df.index) - 1, insert_time])
                    fp.flush()

                    # Increment Row
                    curr_row += len(df.index)

# Query Benchmarks
def query_benchmarks():
    for config_name, config in DB_CONFIGS.items():
        with open('benchmarks/query/' + config_name + '.csv', 'w') as fp:
            csv_writer = csv.writer(fp)
            csv_writer.writerow(['database_entries', 'top_rated_products', 'top_recommended_products'])

            # Database
            sqlObject = DB(reset=True, ivm=config['ivm'], ivm_cache=config['ivm_cache'])

            # Data
            df = pd.read_csv('data.csv')
            for idx, row in df.iterrows():
                # Insert
                sqlObject.insert_review(parse_csv_row(sqlObject, row))

                # Query
                start = time.time()
                sqlObject.top_rated_products(count=25)
                end = time.time()
                top_rated_products_query_time = end - start

                start = time.time()
                sqlObject.top_recommended_products(count=10)
                end = time.time()
                top_recommended_products_query_time = end - start

                # CSV
                csv_writer.writerow([idx, top_rated_products_query_time, top_recommended_products_query_time])
                fp.flush()

def query_graph():
    data = {}
    for config_name in DB_CONFIGS.keys():
        data[config_name] = {
            'database_entries': [],
            'top_rated_products': [],
            'top_recommended_products': [],
        }
    
    # Populate Data
    for config_name in DB_CONFIGS.keys():
        df = pd.read_csv('benchmarks/query/' + config_name + '.csv')
        for _, row in df.iterrows():
            data[config_name]['database_entries'].append(int(row['database_entries']))
            data[config_name]['top_rated_products'].append(float(row['top_rated_products']))
            data[config_name]['top_recommended_products'].append(float(row['top_recommended_products']))

    # Chunk Data
    # chunk_size = 1
    # for config_name in DB_CONFIGS.keys():
    #     for data_type, data_arr in data[config_name].items():
    #         data[config_name][data_type] = [data_arr[i:i + chunk_size] for i in range(0, len(data_arr), chunk_size)]

    # # Summarize Chunks
    # for config_name in DB_CONFIGS.keys():
    #     for data_type in data[config_name].keys():
    #         aggregate_data = []
            
    #         for chunk in data[config_name][data_type]:
    #             if data_type == 'database_entries':
    #                 aggregate_data.append(chunk[0])
    #             else:
    #                 aggregate_data.append(statistics.median(chunk))
     
    #         data[config_name][data_type] = aggregate_data

    # Plots
    plt.figure()
    plt.title("Top Rated Products")
    plt.xlabel("Database Entries")
    plt.ylabel("Time (s)")
    for config_name, config in data.items():
        plt.plot(config['database_entries'], config['top_rated_products'], label=config_name)
    plt.legend()
    plt.savefig("benchmarks/query/top_rated_products.png")

    plt.figure()
    plt.title("Top Recommended Products")
    plt.xlabel("Database Entries")
    plt.ylabel("Time (s)")
    for config_name, config in data.items():
        plt.plot(config['database_entries'], config['top_recommended_products'], label=config_name)
    plt.legend()
    plt.savefig("benchmarks/query/top_recommended_products.png")

    # Close
    plt.close()

def insert_graph():
    data = {}
    for config_name in DB_CONFIGS.keys():
        data[config_name] = {}
        for num_insert in INSERT_ARR:
            data[config_name][num_insert] = {
                'database_entries': [],
                'insert': [],
            }

    # Populate Data
    for config_name in DB_CONFIGS.keys():
        for num_insert in INSERT_ARR:
            df = pd.read_csv('benchmarks/insert/' + config_name + '-' + str(num_insert) + '.csv')
            for _, row in df.iterrows():
                data[config_name][num_insert]['database_entries'].append(int(row['database_entries']))
                data[config_name][num_insert]['insert'].append(float(row['insert']))

            # Remove Last Element To Prevent Partials
            data[config_name][num_insert]['database_entries'].pop()
            data[config_name][num_insert]['insert'].pop()

    # Plots
    for config_name in DB_CONFIGS.keys():
        for num_insert in INSERT_ARR:
            plt.figure()
            plt.title(config_name + ": insert " + str(num_insert))
            plt.xlabel("Database Entries")
            plt.ylabel("Time (s)")
            plt.plot(data[config_name][num_insert]['database_entries'], data[config_name][num_insert]['insert'])
            plt.savefig("benchmarks/insert/" + config_name + '-' + str(num_insert) + ".png")
    
# Main
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--benchmark", action="store_true")
    parser.add_argument("-g", "--graph", action="store_true")
    
    args = parser.parse_args()
    if args.benchmark:
        print("benchmark")
        insert_benchmarks()
        query_benchmarks()
    if args.graph:
        print("graph")
        query_graph()
        insert_graph()
            
if __name__ == '__main__':
    main()
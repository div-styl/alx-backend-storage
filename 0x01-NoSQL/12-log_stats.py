#!/usr/bin/env python3
"""Mongodb through pymongo"""
from pymongo import MongoClient

if __name__ == "__main__":
    """provides some stats about Nginx logs stored in MongoDB"""
    client = MongoClient('mongodb://127.0.0.1:27017')
    db = client.logs.nginx
    logs = db.count_documents({})
    print("{} logs".format(logs))

    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    print("Methods:")
    for method in methods:
        count = db.count_documents({"method": method})
        print("\tmethod {}: {}".format(method, count))

    check = db.count_documents({"method": "GET", "path": "/status"})
    print("{} status check".format(check))

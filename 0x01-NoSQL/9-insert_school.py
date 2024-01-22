#!/usr/bin/env python3
""" Mongodb op using pymongo """


def insert_school(mongo_collection, **kwargs):
    """ inserts a new document in a collection """
    return mongo_collection.insert(kwargs)

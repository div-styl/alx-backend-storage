#!/usr/bin/env python3
"""MongoDB with pymango"""


def list_all(mongo_collection):
    """lists all documents in a collection"""
    doc = mongo_collection.find()

    if doc.count() == 0:
        return []

    return doc

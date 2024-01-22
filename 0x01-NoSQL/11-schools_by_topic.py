#!/usr/bin/env python3
"""returns the list of school having a specific topic"
"""


def schools_by_topic(mongo_collection, topic):
    """returns the list of school having a specific topic"""
    topic = {
            'topics': {
                '$elemMatch': {
                    '$eq': topic,
                },
            },
        }
    return [doc for doc in mongo_collection.find(topic)]

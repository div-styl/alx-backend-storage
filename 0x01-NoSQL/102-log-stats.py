#!/usr/bin/env python3
""" MongoDB """

if __name__ == "__main__":
    """provides some stats about NOSQL collection"""
    client = MongoClient('mongodb://127.0.0.1:27017')
    ngix_c = client.logs.nginx

    n_lg = ngix_c.count_documents({})
    print(f'{n_lg} logs')

    methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    print('Methods:')
    for method in methods:
        cnt = ngix_c.count_documents({'method': method})
        print(f'\tmethod {method}: {cnt}')
    status_check = ngix_c.count_documents({'method': 'GET',
                                            'path': '/status'})
    print(f'{status_check} status check')

    top_ip = ngix_c.aggregate([
        {
            '$group': {
                '_id': '$ip',
                'count': {'$sum': 1}
            }
        },
        {
            '$sort': {
                'count': -1
            }
        },
        {
            '$limit': 10
        },
        {
            '$project': {
                '_id': 0,
                'ip': '$_id',
                'count': 1
            }
        }
    ])

    print('IPs:')
    for ip in top_ip:
        ip = top_ip.get('ip')
        cnt = top_ip.get('count')
        print(f'\t{ip}: {cnt}')

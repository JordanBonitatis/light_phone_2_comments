import csv
import requests


def get_batch_of_comments(after=None):
    url = "https://www.indiegogo.com/private_api/graph/query"
    payload = {
        "operation_id": "campaign_comments_query",
        "variables": {
            "project_id": "2309410",
            "first": 800
        }
    }
    # "after" tells the request where to begin offset
    if after is not None:
        payload["variables"]["after"] = after
    print "Requesting comments (after: {})".format(after)
    return requests.post(url, json=payload).json()


def get_all_comments():
    comments = []
    after = None
    has_next_page = True
    while has_next_page is True:
        res = get_batch_of_comments(after=after)
        # add the new comments to our list
        fetched_comments = res['data']['project']['comments']['edges']
        print "Got {} comments\n".format(len(fetched_comments))
        comments += [comment['node'] for comment in fetched_comments]
        # collect the info so we can proceed getting the rest of the comments
        page_info = res['data']['project']['comments']['pageInfo']
        has_next_page = page_info.get('hasNextPage', False)
        after = page_info['endCursor']
    return comments


def write_comments_to_csv(comments, filename="light_phone_2_comments.csv"):
    print "writing to csv"
    with open(filename, 'w') as csvfile:
        fieldnames = ['comment', 'timestamp', 'replies']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for comment in comments:
            writer.writerow({
                'comment': comment['comment_text'].replace('\n', '').replace(',', ';').encode('ascii', 'ignore'),
                'timestamp': comment['timestamp'],
                'replies': '\n\n'.join(r['reply_text'].replace('\n', '').replace(',', ';').encode('ascii', 'ignore') for r in comment['replies'])
            })


if __name__ == "__main__":
    write_comments_to_csv(comments=get_all_comments())

from taskcluster import helper
import sys
import codecs

secrets_service = helper.TaskclusterConfig().get_service("secrets")
secret_names = set()
secrets = set()

def get_values_from_json(obj):
    out = set()

    def flatten(x):
        if type(x) is dict:
            for value in x.values():
                flatten(value)
        elif type(x) is list:
            for a in x:
                flatten(a)
        else:
            out.add(x)

    flatten(obj)
    return out

continuation = None
while True:
    res = secrets_service.list(continuationToken=continuation)
    secret_names.update(set(res['secrets']))
    if not res.get('continuationToken'):
        break
    continuation = res['continuationToken']

for name in secret_names:
    try:
        res = secrets_service.get(name)
        secrets.update(get_values_from_json(res['secret']))
    except:
        # This happens when we're not allowed to read the secret. Unfortunately
        # there's no way of filtering out secrets we can't read from the
        # listing so we have to try to get them all.
        pass

stdin = codecs.getreader('utf-8')(sys.stdin.buffer)
for line in stdin.readlines():
    for secret in secrets:
        line = line.replace(secret, "https://www.youtube.com/watch?v=zwZISypgA9M")
    sys.stdout.write(line)
    sys.stdout.flush()

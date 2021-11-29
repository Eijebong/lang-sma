from taskcluster import helper
import sys
import codecs
import decisionlib

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

stdin = codecs.getreader('utf-8')(sys.stdin.buffer, errors='replace')
outputs = {}
line = ""
while True:
    # We can't use readlines here because it buffers the entirety of stdin for
    # reasons
    char = stdin.read(1)
    if not char:
        break
    line += char
    if char != '\n':
        continue

    line = line.strip().lstrip()

    # Support gha core.setSecret
    if line.startswith('::add-mask::'):
        secret = line[len('::add-mask::'):]
        secrets.add(secret)
        line = ''
        continue

    # Support gha core.setOutput
    if line.startswith('::set-output'):
        output = line[len('::set-output'):]
        name, value = output.split('::', 1)
        name = name.split('=')[1]
        outputs[name] = value
        line = ''
        continue

    for secret in secrets:
        line = line.replace(secret, "https://www.youtube.com/watch?v=zwZISypgA9M")
    print(line)
    line = ''


output_content_sh = 'env '
for name, value in outputs.items():
    output_content_sh += f' INPUT_{name}="{value}"'
decisionlib.create_extra_artifact('outputs.sh', output_content_sh.encode())

import difflib

# output
# the(insert " fast and") quick brown (replace "fox" with "duck") jumped over the lazy (replace "dog" with "cat")

s1 = 'the quick brown fox jumped over the lazy dog'
s2 = 'the fast and quick brown duck jumped over the lazy cat'


def show_diff(seqm):
    output = []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append('(insert "{}")'.format(seqm.b[b0:b1], a0))
        elif opcode == 'delete':
            output.append('(delete "{}")'.format(seqm.a[a0:a1]))
        elif opcode == 'replace':
            output.append('(replace "{}" with "{}")'.format(seqm.a[a0:a1], seqm.b[b0:b1]))
            # print('range {}..{} of a with {}..{} of b'.format(a0, a1, b0, b1))
        else:
            raise RuntimeError("unexpected opcode")
    return ''.join(output)


sm = difflib.SequenceMatcher(None, s1, s2)
print(show_diff(sm))

import difflib
import os
import subprocess


def edit_file_message(initial_message):
    content_file = '.message_edit.txt'
    vim_options_file = 'options.vim'
    with open(content_file, 'w') as tf:
        tf.write(initial_message)

    subprocess.call(['vim', '-S', vim_options_file, content_file])

    with open(content_file, 'r') as fp:
        content = fp.read()

    os.remove(content_file)
    return content


def read_file(path):
    with open(path, 'r') as fp:
        content = fp.read()
    return content


s1 = 'the quick brown fox jumped over the lazy dog'
s2 = 'the fast and quick brown duck jumped over the lazy cat'


def show_diff(seqm):
    output = []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append('(insert "{}")'.format(seqm.b[b0:b1]))
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

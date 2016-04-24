import difflib
import os
import subprocess
import json


def edit_file_message(initial_message):
    content_file = '.message_edit.txt'
    vim_options_file = 'options.vim'
    with open(content_file, 'w') as tf:
        tf.write(initial_message)

    editor_command = ['vim']
    if os.path.isfile('options.vim'):
        editor_command += ['-S', vim_options_file]
    subprocess.call(editor_command + [content_file])

    with open(content_file, 'r') as fp:
        content = fp.read()

    if content[-1] == "\n":
        content = content[:-1]

    os.remove(content_file)
    return content


def read_file(path):
    with open(path, 'r') as fp:
        content = fp.read()
    return content


class Patch(object):
    def __init__(self, old_text, new_length, instructions=None):
        self.old_text = old_text
        self.new_length = new_length
        self.instructions = instructions
        if instructions is not None:
            self.instructions = instructions
        else:
            self.instructions = []

    def add_instruction(self, opt):
        self.instructions.append(opt)


def create_patch(s1, s2) -> Patch:
    seqm = difflib.SequenceMatcher(None, s1, s2)
    result = Patch(s1, len(s2))
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            result.add_instruction(['e', a0, a1, b0, b1])
        elif opcode == 'insert':
            result.add_instruction(['i', a1, seqm.b[b0:b1]])
        elif opcode == 'delete':
            pass
        elif opcode == 'replace':
            result.add_instruction(['r', b0, b1, seqm.b[b0:b1]])
        else:
            print(opcode)
            raise RuntimeError("unexpected opcode")
    return result


def run_patch(patch: Patch):
    output = patch.new_length * ' '

    def replace(old_str, start, end, new_str):
        s = old_str
        s = s[:start] + new_str + s[end:]
        return s

    for opt in patch.instructions:
        if opt[0] == 'e':
            output = replace(output, opt[3], opt[4], patch.old_text[opt[1]:opt[2]])
        elif opt[0] == 'i':
            output = replace(output, opt[1], opt[1] + len(opt[2]), opt[2])
        elif opt[0] == 'r':
            output = replace(output, opt[1], opt[2], opt[3])
    return output


def get_history(json_file):
    try:
        with open(json_file, 'r') as fp:
            data = json.load(fp)
    except FileNotFoundError:
        data = {}

    if "versions" not in data or type(data["versions"]).__name__ != 'list':
        data["versions"] = []

    return data


def save_patch(json_file, instructions, new_length):
    history = get_history(json_file)
    if len(instructions) == 1:
        if instructions[0][0] == 'e':
            return
    new_version = {
        "new_length": new_length,
        "instructions": instructions
    }
    history["versions"].append(new_version)

    with open(json_file, 'w') as fp:
        json.dump(history, fp)


def get_current_text(file_history):
    if len(file_history["versions"]) == 0:
        pass

    last_text = ''
    for version in file_history["versions"]:
        last_text = run_patch(Patch(last_text, version["new_length"], version["instructions"]))
    return last_text


if __name__ == '__main__':
    history_file = 'history.json'
    history = get_history(history_file)
    old_text = get_current_text(history)

    new_text = edit_file_message(old_text)

    patch_result = create_patch(old_text, new_text)
    save_patch(history_file, patch_result.instructions, patch_result.new_length)

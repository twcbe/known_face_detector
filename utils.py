def load_file(filename, extension='pkl'):
    with open(filename+"."+extension, 'rb') as file_handle:
        result = load(file_handle)
    return result

def save_file(data, filename, extension='pkl'):
    with open(filename+"."+extension, 'rb') as file_handle:
        save(data, file_handle)

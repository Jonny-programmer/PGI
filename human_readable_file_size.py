def human_readable_file_size(bytes_size):
    table = [('GB', 1073741824), ('MB', 1048576), ('KB', 1024), ('B', 1)]
    for key, val in table:
        ans = round(bytes_size / val, 2)
        if ans > 0:
            return f"{ans} {key}"

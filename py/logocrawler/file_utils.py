def get_urls(fp):
    '''
    Reads file with the given filepath, and returns a list where
    each URL is an element.

    Parameters:
        fp (str): Filepath for the URL file.

    Returns:
        List of URLs as strings.
    '''
    with open(fp, 'r') as in_f:
        return [x.strip() for x in in_f]


def write_results(directory, results):
    '''
    Writes two files, results.txt and candidates.txt. results.txt will output
    one logo per line, in the same order as the corresponding websites. If
    no logo was found, the word NULL will appear instead.

    candidates.txt is similar, but each line can have multiple comma separated
    values, these are candidates that could potentially be the logo.

    Parameters:
        directory (str): Path to output directory.
        results (list of str): Logo candidates
    '''
    with (open(f'{directory}/results.txt', 'w') as res_f,
          open(f'{directory}/candidates.txt', 'w') as can_f):
        for l in results:
            if not l:
                res_f.write('NULL\n')
                can_f.write('NULL\n')
            else:
                l = [x.strip() for x in l]
                res_f.write(f'{l[0]}\n')
                can_f.write(f'{",".join(l)}\n')

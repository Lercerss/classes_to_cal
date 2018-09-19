def table_to_2d_list(html_table):
    """
    Assumes table headers (<th>) are present for every column in the table

    :param html_table: bs4 Tag for table to be parsed into list of list
    :return: 2D list without table headers, empty elements populated with None
    """
    t_rows = html_table.find_all('tr')
    num_rows = len(t_rows)
    num_cols = sum(int(th.get('colspan', 1)) for th in t_rows[0].children)

    result = [[None for _ in range(num_cols)] for _ in range(num_rows - 1)]

    for i, tr in enumerate(t_rows[1:]):
        row_cells = tr.children
        for j in range(num_cols):
            if result[i][j]:
                continue
            td = next(row_cells)
            for x in range(i, i + int(td.get('rowspan', 1))):
                colspan = int(td.get('colspan', 1))
                result[x][j:j + colspan] = [td.contents[0] for _ in range(colspan)]

    return result

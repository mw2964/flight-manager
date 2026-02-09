from prettytable import PrettyTable, TableStyle, ALL, NONE

def format_table(table: PrettyTable) -> str:

    # Set table formatting
    table.set_style(TableStyle.SINGLE_BORDER)
    table.align = "l"
    table.max_width = 20
    table.hrules = ALL
    table.vrules = NONE
    
    indented_table = ""
    for row in table.get_string().split("\n"):
        indented_table += (" " * 5) + row + "\n"
    
    return indented_table
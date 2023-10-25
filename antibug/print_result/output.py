from tabulate import tabulate
from colored import fg, attr
import os


class Output():
    @staticmethod
    def output_logic(func, result, detect_list):
        table_data = []
        for i in range(len(func)):
            if func[i]['function'] in result[i]:
                row = [f"{fg('green')}{func[i]['fname']}", f"{func[i]['detect']}",
                       f"{func[i]['detector']}", f"{func[i]['score']}", f"{'Satisfied'}{attr('reset')}"]
                table_data.append(row)
            elif func[i]['function'] not in result[i]:
                if func[i]['detector'] in detect_list:
                    row = [f"{fg('red')}{func[i]['fname']}", f"{func[i]['detect']}",
                           f"{func[i]['detector']}", f"{func[i]['score']}", f"{'Unsatisfied'}{attr('reset')}"]
                    table_data.append(row)
                else:
                    pass

        headers = ['Target', 'Detect', 'Detector',
                   'Similarity', 'Satisfaction']

        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

    @staticmethod
    def output_simil(similar):
        headers = ["Compared with", "Contract", "Function", "Score"]
        table_data = [[os.path.basename(s[0]), s[1], s[2], s[3]]
                      for s in similar]
        print(tabulate(table_data, headers=headers))

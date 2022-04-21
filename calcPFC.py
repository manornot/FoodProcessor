#awaited_data = {'Prot': 0, 'Fat': 0, 'Carb': 0, 'Weight':0}


def dict2text(data):
    return f"Б:{data.get('Prot')} Ж:{data.get('Fat')} У:{data.get('Carb')} К:{data.get('KCal')}"


class bujda:
    components: list = []

    def __init__(self) -> None:
        pass

    def addComponent(self, component):
        self.components.append(component)

    def calculate(self, finalWeight=None):
        if finalWeight:
            totProt = sum([
                comp['Prot'] * comp['Weight'] / 100 for comp in self.components
            ])
            totFat = sum([
                comp['Fat'] * comp['Weight'] / 100 for comp in self.components
            ])
            totCarb = sum([
                comp['Carb'] * comp['Weight'] / 100 for comp in self.components
            ])
            totKCal = totProt * 4 + totFat * 9 + totCarb * 4
            return {
                'Prot': totProt / finalWeight * 100,
                'Fat': totFat / finalWeight * 100,
                'Carb': totCarb / finalWeight * 100,
                'Kcal': totKCal / finalWeight * 100
            }
        else:
            totProt = sum([
                comp['Prot'] * comp['Weight'] / 100 for comp in self.components
            ])
            totFat = sum([
                comp['Fat'] * comp['Weight'] / 100 for comp in self.components
            ])
            totCarb = sum([
                comp['Carb'] * comp['Weight'] / 100 for comp in self.components
            ])
            totKCal = totProt * 4 + totFat * 9 + totCarb * 4
            totWeight = sum([comp['Weight'] for comp in self.components])
            return {
                'Prot': totProt / totWeight * 100,
                'Fat': totFat / totWeight * 100,
                'Carb': totCarb / totWeight * 100,
                'Kcal': totKCal / totWeight * 100
            }


if __name__ == '__main__':
    test = bujda()
    awaited_data = {'Prot': 1, 'Fat': 10, 'Carb': 1, 'Weight': 100}
    test.addComponent(awaited_data)
    awaited_data = {'Prot': 12, 'Fat': 10, 'Carb': 2, 'Weight': 200}
    test.addComponent(awaited_data)
    awaited_data = {'Prot': 0.1, 'Fat': 15, 'Carb': 2, 'Weight': 150}
    test.addComponent(awaited_data)
    awaited_data = {'Prot': 5, 'Fat': 7, 'Carb': 20, 'Weight': 750}
    test.addComponent(awaited_data)
    awaited_data = {'Prot': 3, 'Fat': 0, 'Carb': 13, 'Weight': 100}
    test.addComponent(awaited_data)
    print(test.calculate())
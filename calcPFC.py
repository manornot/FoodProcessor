#awaited_data = {'Prot': 0, 'Fat': 0, 'Carb': 0, 'KCal': 0, 'Weight':0}
class bujda:
    components:list = []
    def __init__(self) -> None:
        pass
    def addComponent(self,component):
        self.components.add(component)
    def calculate(self,finalWeight = None):
        if finalWeight:
            totProt = sum([comp['Prot']*comp['Weight']/100 for comp in self.components])
            totFat = sum([comp['Fat']*comp['Weight']/100 for comp in self.components])
            totCarb = sum([comp['Carb']*comp['Weight']/100 for comp in self.components])
            totKCal = totProt*4 + totFat*9 + totCarb*4
            return totProt/finalWeight*100,totFat/finalWeight*100,totCarb/finalWeight*100,totKCal/finalWeight*100


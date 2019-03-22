import json

import pandas as pd

class CensusUpdater():

    def __init__(self):
        self.stateCodeMap = {
            '01':'AL','05':'AR','04':'AZ','06':'CA','08':'CO','09':'CT','11':'DC','10':'DE','12':'FL','13':'GA',
            '19':'IA','16':'ID','17':'IL','18':'IN','20':'KS','21':'KY','22':'LA','25':'MA','24':'MD','23':'ME',
            '26':'MI','27':'MN','29':'MO','28':'MS','30':'MT','37':'NC','38':'ND','31':'NE','33':'NH','34':'NJ',
            '35':'NM','32':'NV','36':'NY','39':'OH','40':'OK','41':'OR','42':'PA','44':'RI','45':'SC','46':'SD',
            '47':'TN','48':'TX','49':'UT','51':'VA','50':'VT','53':'WA','55':'WI','54':'WV','56':'WY','02':'AK',
            '15':'HI','72':'PR','78':'VI'}

    def update(self, filepath):
        changeset_df = self.readFromPath(filepath)

        recordMap = {}
        for index, row in changeset_df.iterrows():
            blockid = '0' + row["blockid"]
            operation = row["change"].strip()

            state = self.getStateForCode(blockid[1:3])
            print("State = " + state)
            pathToFile = 'C:\\Users\Chris Stolte\IdeaProjects\HEM\census\\Blks_' + state + '.json'
            with open(pathToFile, "r") as read_file:
                data = json.load(read_file)
                print(str(len(data)))
                replaced = [self.mutate(x, operation, row)
                    if x['IDMARPLOT']==blockid
                    else x for x in data if x['IDMARPLOT']!=blockid or (operation == 'Move' or operation == 'Zero')]

            pathToNewFile = 'C:\\Users\Chris Stolte\IdeaProjects\HEM\census\\Blks_' + state + '1.json'
            with open(pathToNewFile, "w") as write_file:
                print(str(len(replaced)))
                json.dump(replaced, write_file, indent=4)

    def mutate(self, record, operation, row):
        if operation == 'Move':
            print("Moving...")
            record['LAT'] = float(row['lat'])
            record['LON'] = float(row['lon'])
        elif operation == 'Zero':
            print("Zeroing...")
            record['POPULATION'] = 0

        return record

    def readFromPath(self, filepath):
        colnames = ["facid", "category", "blockid", "lat", "lon", "change"]
        with open(filepath, "rb") as f:
            df = pd.read_excel(f, skiprows=1, names=colnames, dtype=str, na_values=[''], keep_default_na=False)
            return df

    def getStateForCode(self, code):
        return self.stateCodeMap[code]

updater = CensusUpdater()
updater.update('C:\\Users\Chris Stolte\IdeaProjects\HEM\changeset.xlsx')
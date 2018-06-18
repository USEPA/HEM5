import os
import pandas as pd
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

class FileUploader():

    def __init__(self):
        pass

    def upload(self, file):

        filename = askopenfilename()

        #if the upload is canceled
        if filename is None:
            print("Canceled!")
            # TODO eventually open box or some notification to say this is required
            
        elif not self.is_excel(filename):
            messagebox.showinfo("Invalid file format", "Not a valid file format, please upload an excel file for " + file +".")
            
        else:
            file_path = os.path.abspath(filename)

            if file == "facilities options list":

                # FACILITIES LIST excel to dataframe
                # HEADER----------------------
                # FacilityID|met_station|rural_urban|max_dist|model_dist|radials|circles|overlap_dist|acute|hours|elev|
                # multiplier|ring1|dep|depl|phase|pdep|pdepl|vdep|vdepl|All_rcpts|user_rcpt|bldg_dw|urban_pop|fastall
                faclist_df = pd.read_excel(open(file_path,'rb'),
                                                names=("fac_id","met_station","rural_urban","max_dist","model_dist","radial","circles","overlap_dist",
                                                       "acute","hours","elev","multiplier","ring1","dep","depl","phase","pdep","pdepl","vdep","vdepl",
                                                       "all_rcpts","user_rcpt","bldg_dw","urban_pop","fastall"),
                                                converters={0:str,1:str,2:str,8:str,10:str,13:str,14:str,15:str,16:str,17:str,18:str,19:str,
                                                            20:str,21:str,22:str,24:str})

                # TODO why manually convert fac_list to numeric? converters?
                
                faclist_df["model_dist"] = pd.to_numeric(faclist_df["model_dist"],errors="coerce")
                faclist_df["radial"] = pd.to_numeric(faclist_df["radial"],errors="coerce")
                faclist_df["circles"] = pd.to_numeric(faclist_df["circles"],errors="coerce")
                faclist_df["overlap_dist"] = pd.to_numeric(faclist_df["overlap_dist"],errors="coerce")
                faclist_df["hours"] = pd.to_numeric(faclist_df["hours"],errors="coerce")
                faclist_df["multiplier"] = pd.to_numeric(faclist_df["multiplier"],errors="coerce")
                faclist_df["ring1"] = pd.to_numeric(faclist_df["ring1"],errors="coerce")
                faclist_df["urban_pop"] = pd.to_numeric(faclist_df["urban_pop"],errors="coerce")
                faclist_df["max_dist"] = pd.to_numeric(faclist_df["max_dist"],errors="coerce")

                logMsg = "Uploaded facilities options list file for " + str(faclist_df['fac_id'].count()) + " facilities\n"

                return {'path': file_path, 'df': faclist_df, 'messages': [logMsg]}

            elif file == "hap emissions":

                #HAP EMISSIONS excel to dataframe
                # HEADER------------------------
                # FacilityID|SourceID|HEM3chem|SumEmissionTPY|FractionParticulate
                hapemis_df = pd.read_excel(open(file_path, "rb"),
                        names=("fac_id","source_id","pollutant","emis_tpy","part_frac"),
                        converters={0:str,1:str,2:str,3:float,4:float})

                #fill Nan with 0
                hapemis_df.fillna(0)

                #turn part_frac into a decimal
                hapemis_df['part_frac'] = hapemis_df['part_frac'] / 100

                #create additional columns, one for particle mass and the other for gas/vapor mass...
                hapemis_df['particle'] = hapemis_df['emis_tpy'] * hapemis_df['part_frac']
                hapemis_df['gas'] = hapemis_df['emis_tpy'] * (1 - hapemis_df['part_frac'])

                #get list of pollutants from dose library
                dose = pd.read_excel(open('resources/Dose_Response_Library.xlsx', 'rb'))
                master_list = list(dose['Pollutant'])
                lower = [x.lower() for x in master_list]

                user_haps = set(hapemis_df['pollutant'])
                missing_pollutants = []

                for hap in user_haps:
                    if hap.lower() not in lower:
                        missing_pollutants.append(hap)


                #                missing_pollutants = {}
                #                for row in self.hapemis_df.itertuples():
                #
                #                    if row[3].lower() not in lower:
                #
                #                        if row[1] in missing_pollutants.keys():
                #
                #                            missing_pollutants[row[1]].append(row[3])
                #
                #                        else:
                #                            missing_pollutants[row[1]] = [row[3]]
                #
                #                for key in missing_pollutants.keys():
                #                    missing_pollutants[key] = ', '.join(missing_pollutants[key])


                logMessages = []
                #if there are any missing pollutants
                if len(missing_pollutants) > 0:
                    fix_pollutants = messagebox.askyesno("Missing Pollutants in dose response library", "The following pollutants were not found in HEM4's Dose Response Library: " + ', '.join(missing_pollutants) + ".\n Would you like to add them to the dose response library in the resources folder (they will be removed otherwise). ")
                    #if yes, clear box and empty dataframe

                    if fix_pollutants:
                        #clear hap emis upload area
                        file_path = ''

                    #if no, remove them from dataframe
                    else:
                        missing = list(missing_pollutants.values())
                        remove = set(missing[0].split(', '))


                        #remove them from data frame

                        for p in remove:

                            hapemis_df = hapemis_df[hapemis_df.pollutant != str(p)]

                            #record upload in log
                            #add another essage to say the following pollutants were assigned a generic value...
                            logMessages.append("Removed " + p + " from hap emissions file\n")


                else:
                    #record upload in log
                    hap_num = set(hapemis_df['fac_id'])
                    logMessages.append("Uploaded HAP emissions file for " + str(len(hap_num)) + " facilities\n")

                return {'path': file_path, 'df': hapemis_df, 'messages': logMessages}

            elif file == "emissions locations":

                #EMISSIONS LOCATION excel to dataframe
                # HEADER------------------------
                # FacilityID|SourceID|LocationType|Longitude|Latitude|UTMzone|SourceType|Lengthx|Lengthy|Angle|HorzDim|
                # VertDim|AreaVolReleaseHgt|StackHgt_m|StackDiameter_m|ExitGasVel_m|ExitGasTemp_K|Elevation_m|X2|Y2
                emisloc_df = pd.read_excel(open(file_path, "rb"),
                        names=("fac_id","source_id","location_type","lon","lat","utmzone","source_type","lengthx","lengthy",
                           "angle","horzdim","vertdim","areavolrelhgt","stkht","stkdia","stkvel","stktemp","elev","x2","y2"),
                        converters={0:str,1:str,2:str,3:float,4:float,5:float,6:str,7:float,8:float,9:float,10:float,
                            11:float,12:float,13:float,14:float,15:float,16:float,17:float,18:float,19:float})

                #record upload in log
                emis_num = set(emisloc_df['fac_id'])
                logMsg = "Uploaded emissions location file for " + str(len(emis_num)) + " facilities\n"

                return {'path': file_path, 'df': emisloc_df, 'messages': [logMsg]}


            elif file == "building downwash":

                file_path = os.path.abspath(filename)
                # self.bd_list.set(file_path)
                # self.bd_path = file_path
                #
                # #building downwash dataframe
                # self.bd_df = pd.read_csv(open(self.bd_path ,"rb"))
                #
                # #record upload in log
                # self.scr.insert(tk.INSERT, "Uploaded building downwash for...")
                # self.scr.insert(tk.INSERT, "\n")


            elif file == "particle depletion":

                file_path = os.path.abspath(filename)
                # self.dep_part.set(file_path)
                # self.dep_part_path = file_path
                #
                # #particle dataframe
                # self.particle_df = pd.read_excel(open(self.dep_part_path, "rb")
                #                                  , names=("fac_id", "source_id", "diameter", "mass", "density"))
                #
                # #record upload in log
                # self.scr.insert(tk.INSERT, "Uploaded particle depletion for...")
                # self.scr.insert(tk.INSERT, "\n")

            elif file == "land use description":

                file_path = os.path.abspath(filename)
                # self.dep_land.set(file_path)
                # self.dep_land_path = file_path
                #
                # self.land_df = pd.read_excel(open(self.dep_land_path, "rb"))
                # self.land_df.rename({"Facility ID " : "fac_id"})
                #
                # #record upload in log
                # self.scr.insert(tk.INSERT, "Uploaded land use description for...")
                # self.scr.insert(tk.INSERT, "\n")


            elif file == "season vegetation":

                file_path = os.path.abspath(filename)
                # self.dep_veg.set(file_path)
                # self.dep_veg_path = file_path
                #
                # self.veg_df = pd.read_csv(open(self.dep_veg_path, "rb"))
                # self.veg_df.rename({"Facility ID": "fac_id"})
                # #record upload in log
                # self.scr.insert(tk.INSERT, "Uploaded season vegetation for...")
                # self.scr.insert(tk.INSERT, "\n")


            elif file == "emissions variation":

                file_path = os.path.abspath(filename)
                # self.evar_list.set(file_path)
                # self.evar_list_path = file_path
                #
                # #record upload in log
                # self.scr.insert(tk.INSERT, "Uploaded emissions variance for...")
                # self.scr.insert(tk.INSERT, "\n")

    def uploadDependent(self, file, dependency):

        filename = askopenfilename()

        #if the upload is canceled
        if filename is None:
            print("Canceled!")

        elif not self.is_excel(filename):
            messagebox.showinfo("Invalid file format", "Not a valid file format, please upload an excel file for " + file +".")

        else:
            file_path = os.path.abspath(filename)

            if file == "polyvertex":

                emisloc_df = dependency;

                #POLYVERTEX excel to dataframe
                multipoly_df = pd.read_excel(open(file_path, "rb"),
                     names=("fac_id","source_id","location_type","lon","lat","utmzone","numvert","area", "fipstct"),
                     converters={"FacilityID":str,"source_id":str,"location_type":str,"lon":float,"lat":float,
                         "utmzone":str,"numvert":float,"area":float})

                #get polyvertex facility list for check
                find_is = emisloc_df[emisloc_df['source_type'] == "I"]
                fis = find_is['fac_id']

                #check for unassigned polyvertex
                check_poly_assignment = set(multipoly_df["fac_id"])
                poly_unassigned = []
                logMsg = ""

                for fac in fis:
                    if fac not in check_poly_assignment:
                        poly_unassigned.append(fac)

                if len(poly_unassigned) > 0:
                    messagebox.showinfo("Unassigned Polygon Sources",
                        "Polygon Sources for " + ", ".join(poly_unassigned) +
                        " have not been assigned. Please edit the 'source_type' column in the Emissions Locations file.")
                    #clear box and empty data frame
                else:
                    logMsg = "Uploaded polygon sources for " + " ".join(check_poly_assignment) + "\n"

                return {'path': file_path, 'df': multipoly_df, 'messages': [logMsg]}

            elif file == "bouyant line":

                self.bouyant_list.set(file_path)
                self.bouyant_path = file_path

                #BOUYANT LINE excel to dataframe
                self.multibuoy_df = pd.read_excel(open(self.bouyant_path, "rb")
                                                  , names=("fac_id", "avgbld_len", "avgbld_hgt", "avgbld_wid", "avglin_wid", "avgbld_sep", "avgbuoy"))


                #get bouyant line facility list
                self.emisloc_df['source_type'].str.upper()
                find_bs = self.emisloc_df[self.emisloc_df['source_type'] == "B"]

                fbs = find_bs['fac_id'].unique()

                #check for unassigned buoyants

                check_bouyant_assignment = set(self.multibuoy_df["fac_id"])

                bouyant_unassigned = []
                for fac in fbs:

                    if fac not in check_bouyant_assignment:
                        bouyant_unassigned.append(fac)

                if len(bouyant_unassigned) > 0:
                    messagebox.showinfo("Unassigned Bouyant Line parameters", "Bouyant Line parameters for " + ", ".join(bouyant_unassigned) + " have not been assigned. Please edit the 'source_type' column in the Emissions Locations file.")
                else:
                    pass
                    #record upload in log
                    #self.scr.insert(tk.INSERT, "Uploaded bouyant line parameters for " + " ".join(check_bouyant_assignment))
                    #self.scr.insert(tk.INSERT, "\n")


            elif file == "user receptors":

                #USER RECEPTOR dataframe
                faclist_df = dependency
                ureceptor_df = pd.read_excel(open(file_path, "rb"),
                                            names=("fac_id", "loc_type", "lon", "lat", "utmzone", "elev", "rec_type", "rec_id"),
                                            converters={0:str})

                #check for unassigned user receptors

                check_receptor_assignment = ureceptor_df["fac_id"]

                receptor_unassigned = []
                for receptor in check_receptor_assignment:
                    #print(receptor)
                    row = faclist_df.loc[faclist_df['fac_id'] == receptor]
                    #print(row)
                    check = row['user_rcpt'] == 'Y'
                    #print(check)

                    if check is False:
                        receptor_unassigned.append(str(receptor))

                logMsg = ''
                if len(receptor_unassigned) > 0:
                    facilities = set(receptor_unassigned)
                    messagebox.showinfo("Unassigned User Receptors", "Receptors for " + ", ".join(facilities) + " have not been assigned. Please edit the 'user_rcpt' column in the facility options file.")
                else:
                    check_receptor_assignment = [str(facility) for facility in check_receptor_assignment]
                    logMsg = "Uploaded user receptors for " + " ".join(check_receptor_assignment) + "\n"

                return {'path': file_path, 'df': ureceptor_df, 'messages': [logMsg]}

    def is_excel(self, filepath):
        extensions = [".xls", ".xlsx"]
        return any(ext in filepath for ext in extensions)
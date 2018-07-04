# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 09:46:16 2018

@author: dlindsey
"""

def upload(self, file):
    """ This is a generic upload function """
    
    #checks
    if file == "polyvertex":
    
        if hasattr(self, "emisloc_df"): 
            filename = askopenfilename()
        else:
            messagebox.showinfo("Emissions Locations File Missing", "Please upload an Emissions Locations file before adding a Polyvertex file.")
    
    elif file == "bouyant":
       
        if hasattr(self, "emisloc_df"): 
            filename = askopenfilename()
        else:
            messagebox.showinfo("Emissions Locations File Missing", "Please upload an Emissions Locations file before adding a Bouyant line file.")
    

    elif file == "user receptors":
        
        if hasattr(self, "faclist_df"): 
            filename = askopenfilename()
        else:
            messagebox.showinfo("Facilities List Option File Missing", "Please upload a Facilities List Options file before selecting a User Receptors file.")
    
    else:
        #get file name from open dialogue
        filename = askopenfilename()
    
    #if the upload is canceled 
    if filename == None:
        print("Canceled!")
        #eventually open box or some notification to say this is required 
    elif is_excel(filename) == False:
        messagebox.showinfo("Invalid file format", "Not a valid file format, please upload an excel file for " + file +".")
    elif is_excel(filename) == True:
        file_path = os.path.abspath(filename)
                      
        if file == "facilities options list":
            
            self.fac_list.set(file_path)
            self.fac_path = file_path
            
            #   FACILITIES LIST excel to dataframe

            self.faclist_df = pd.read_excel(open(self.fac_path,'rb')
                , names=("fac_id","met_station","rural_urban","max_dist","model_dist"
                        ,"radial","circles","overlap_dist","acute","hours"
                        ,"elev","multiplier","ring1","dep","depl","phase"
                        ,"pdep","pdepl","vdep","vdepl","all_rcpts","user_rcpt"
                        ,"bldg_dw","urban_pop","fastall")
                , converters={"fac_id":str,"met_station":str,"rural_urban":str
                        ,"acute":str
                        ,"elev":str,"dep":str,"depl":str,"phase":str
                        ,"pdep":str,"pdepl":str,"vdep":str,"vdepl":str,"all_rcpts":str,"user_rcpt":str
                        ,"bldg_dw":str,"fastall":str})
    
            #manually convert fac_list to numeric
            self.faclist_df["model_dist"] = pd.to_numeric(self.faclist_df["model_dist"],errors="coerce")
            self.faclist_df["radial"] = pd.to_numeric(self.faclist_df["radial"],errors="coerce")
            self.faclist_df["circles"] = pd.to_numeric(self.faclist_df["circles"],errors="coerce")
            self.faclist_df["overlap_dist"] = pd.to_numeric(self.faclist_df["overlap_dist"],errors="coerce")
            self.faclist_df["hours"] = pd.to_numeric(self.faclist_df["hours"],errors="coerce")
            self.faclist_df["multiplier"] = pd.to_numeric(self.faclist_df["multiplier"],errors="coerce")
            self.faclist_df["ring1"] = pd.to_numeric(self.faclist_df["ring1"],errors="coerce")
            self.faclist_df["urban_pop"] = pd.to_numeric(self.faclist_df["urban_pop"],errors="coerce")
            self.faclist_df["max_dist"] = pd.to_numeric(self.faclist_df["max_dist"],errors="coerce")
            
            #grab facility ideas for comparison with hap emission and emission location files
            self.facids = self.faclist_df['fac_id']
                
            self.scr.insert(tk.INSERT, "Uploaded facilities options list file for " + str(self.facids.count()) + " facilities" )
            self.scr.insert(tk.INSERT, "\n")
            
        elif file == "hap emissions":
                
            self.hap_list.set(file_path)
            self.hap_path = file_path
            
            #HAP EMISSIONS excel to dataframe    
            self.hapemis_df = pd.read_excel(open(self.hap_path, "rb")
                , names=("fac_id","source_id","pollutant","emis_tpy","part_frac")
                , converters={"fac_id":str,"source_id":str,"pollutant":str,"emis_tpy":float,"part_frac":float})
            
            #fill Nan with 0
            self.hapemis_df.fillna(0)
            
            #turn part_frac into a decimal
            self.hapemis_df['part_frac'] = self.hapemis_df['part_frac'] / 100

            #create additional columns, one for particle mass and the other for gas/vapor mass...
            self.hapemis_df['particle'] = self.hapemis_df['emis_tpy'] * self.hapemis_df['part_frac']
            self.hapemis_df['gas'] = self.hapemis_df['emis_tpy'] * (1 - self.hapemis_df['part_frac'])


            #get unique list of polutants from input
            pollutants = set(self.hapemis_df['pollutant'])

            #get list of pollutants from dose library
            dose = pd.read_excel(open('Dose_Response_Library.xlsx', 'rb'))
            master_list = set(dose['Pollutant'])

            #check pollutants against pollutants in dose library
            missing_pollutants = []
            for pollutant in pollutants:
                if pollutant not in master_list:
                    missing_pollutants.append(pollutant)
            
            #if there are any missing pollutants
            if len(missing_pollutants) > 0:
                fix_pollutants = messagebox.askyesno("Unassigned Missing Pollutants in dose response library", "The following pollutants were not found in HEM4's Dose Response Library: " + ", ".join(missing_pollutants) + "\n. have not been assigned. Would you like to continue with a generic value or go to the resources folder and add missing pollutants?")
                #if yes, clear box and empty dataframe
                if fix_pollutants == 'yes':
                    pass
                
                    
                #if no, assign generic value and continue 
                elif fix_pollutants == 'no':
                    pass
                        #record upload in log
                        #add another essage to say the following pollutants were assigned a generic value...
                
            else:
                    #record upload in log
                hap_num = set(self.hapemis_df['fac_id'])
                self.scr.insert(tk.INSERT, "Uploaded HAP emissions file for " + str(len(hap_num)) + " facilities" )
                self.scr.insert(tk.INSERT, "\n")
            
            
        elif file == "emissions locations":
                
            self.emisloc_list.set(file_path)
            self.emisloc_path = file_path
              
                #EMISSIONS LOCATION excel to dataframe
            self.emisloc_df = pd.read_excel(open(self.emisloc_path, "rb")
            , names=("fac_id","source_id","location_type","lon","lat","utmzone","source_type"
                     ,"lengthx","lengthy","angle","horzdim","vertdim","areavolrelhgt","stkht"
                     ,"stkdia","stkvel","stktemp","elev","x2","y2")
            , converters={"fac_id":str,"source_id":str,"location_type":str,"lon":float,"lat":float
                    ,"utmzone":float,"source_type":str,"lengthx":float,"lengthy":float,"angle":float
                    ,"horzdim":float,"vertdim":float,"areavolrelhgt":float,"stkht":float,"stkdia":float
                    ,"stkvel":float,"stktemp":float,"elev":float,"x2":float,"y2":float})
            
                #record upload in log
            emis_num = set(self.emisloc_df['fac_id'])
            self.scr.insert(tk.INSERT, "Uploaded emissions location file for " + str(len(emis_num)) + " facilities" )
            self.scr.insert(tk.INSERT, "\n")
            
            
        elif file == "polyvertex":
            
            self.poly_list.set(file_path)
            self.poly_path = file_path
            
            #POLYVERTEX excel to dataframe
            self.multipoly_df = pd.read_excel(open(self.poly_path, "rb")
                  , names=("fac_id","source_id","location_type","lon","lat","utmzone"
                           ,"numvert","area")
                  , converters={"fac_id":str,"source_id":str,"location_type":str,"lon":float
                                ,"lat":float,"utmzone":str,"numvert":float,"area":float})
            
            #get polyvertex facility list for check
            find_is = self.emisloc_df[self.emisloc_df['source_type'] == "I"]
            fis = find_is['fac_id']
                
            #check for unassigned polyvertex            
            check_poly_assignment = set(self.multipoly_df["fac_id"])
            poly_unassigned = []             
            
            for fac in fis:
                if fac not in check_poly_assignment:   
                    poly_unassigned.append(fac)
            
            if len(poly_unassigned) > 0:
                messagebox.showinfo("Unassigned Polygon Sources", "Polygon Sources for " + ", ".join(poly_unassigned) + " have not been assigned. Please edit the 'source_type' column in the Emissions Locations file.")
                #clear box and empty data frame
            else:
                #record upload in log
                self.scr.insert(tk.INSERT, "Uploaded polygon sources for " + " ".join(check_poly_assignment))
                self.scr.insert(tk.INSERT, "\n")
            
        
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
                #record upload in log
                self.scr.insert(tk.INSERT, "Uploaded bouyant line parameters for " + " ".join(check_bouyant_assignment))
                self.scr.insert(tk.INSERT, "\n")
                
        
        elif file == "user receptors":
            
            file_path = os.path.abspath(filename)
            self.urep_list.set(file_path)
            self.urep_path = file_path
            
            #USER RECEPTOR dataframe
            self.ureceptr_df = pd.read_excel(open(self.urep_path, "rb")
                  , names=("fac_id", "loc_type", "lon", "lat", "utmzone", "elev", "rec_type", "rec_id"))
            
            #check for unassigned user receptors
            
            check_receptor_assignment = self.ureceptr_df["fac_id"]
            
            receptor_unassigned = []     
            for receptor in check_receptor_assignment:
                #print(receptor)
                row = self.faclist_df.loc[self.faclist_df['fac_id'] == receptor]
                #print(row)
                check = row['user_rcpt'] == 'Y'
                #print(check)
            
                if check is False:   
                    receptor_unassigned.append(str(receptor))
            
            
            if len(receptor_unassigned) > 0:
                facilities = set(receptor_unassigned)
                messagebox.showinfo("Unassigned User Receptors", "Receptors for " + ", ".join(facilities) + " have not been assigned. Please edit the 'user_rcpt' column in the facility options file.")
            #else:
                #record upload in log
                #self.scr.insert(tk.INSERT, "Uploaded user receptors for " + " ".join(check_receptor_assignment))
                #self.scr.insert(tk.INSERT, "\n")
        
        
        elif file == "building downwash":
            
            file_path = os.path.abspath(filename)
            self.bd_list.set(file_path)
            self.bd_path = file_path
            
            #building downwash dataframe
            self.bd_df = pd.read_csv(open(bd_path ,"rb"))
            
             #record upload in log
            self.scr.insert(tk.INSERT, "Uploaded building downwash for...")
            self.scr.insert(tk.INSERT, "\n")
            
            
        elif file == "particle depletion":
                
            file_path = os.path.abspath(filename)
            self.dep_part.set(file_path)
            self.dep_part_path = file_path
            
            #particle dataframe
            self.particle_df = pd.read_excel(open(self.dep_part_path, "rb")
                  , names=("fac_id", "source_id", "diameter", "mass", "density"))
            
             #record upload in log
            self.scr.insert(tk.INSERT, "Uploaded particle depletion for...")
            self.scr.insert(tk.INSERT, "\n")
            
        elif file == "land use description":
            
            file_path = os.path.abspath(filename)
            self.dep_land.set(file_path)
            self.dep_land_path = file_path
            
            self.land_df = pd.read_excel(open(self.dep_land_path, "rb"))
            self.land_df.rename({"Facility ID " : "fac_id"})
            
             #record upload in log
            self.scr.insert(tk.INSERT, "Uploaded land use description for...")
            self.scr.insert(tk.INSERT, "\n")
            
            
        elif file == "season vegetation":
            
            file_path = os.path.abspath(filename)
            self.dep_veg.set(file_path)
            self.dep_veg_path = file_path
            
            self.veg_df = pd.read_csv(open(self.dep_veg_path, "rb"))
            self.veg_df.rename({"Facility ID": "fac_id"})
             #record upload in log
            self.scr.insert(tk.INSERT, "Uploaded season vegetation for...")
            self.scr.insert(tk.INSERT, "\n")
  
    
        elif file == "emissions variation":
            
            file_path = os.path.abspath(filename)
            self.evar_list.set(file_path)
            self.evar_list_path = file_path
            
             #record upload in log
            self.scr.insert(tk.INSERT, "Uploaded emissions variance for...")
            self.scr.insert(tk.INSERT, "\n")
            
            
            
            
            
            
                
                
                
                
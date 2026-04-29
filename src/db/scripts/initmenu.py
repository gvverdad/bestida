import json

menus = """
{"Mainmenu": {"id": "MenuInit", "name": "Main Menu", "items": [
    {"MenuItem": {"line": 900, "id": "MenuSysAdmin", "name": "System Administration", "items": [
        {"MenuItem": {"line": 100, "id": "MenuCompany", "name": "Companies Menu", "items": [
	        {"MenuItem": {"line": 100, "description": "Companies", "type": "Grid", 
		                "table": "Companies", "programname": "Companies",
		                "program": "GridCompanies",
		                "run": 0, "create": 999, "update": 999, "delete": 999,
		                "url": "/grid/GridCompanies"}},
			{"MenuItem": {"line": 200, "description": "Address Types", "type": "Grid",
		                "program": "GridCompanyAddressTypes", "programname": "Company Address Types",
		                "run": 0, "create": 999, "update": 999, "delete": 999,			     
				        "url": "/grid/GridCompanyAddressTypes"}},
			{"MenuItem": {"line": 300, "description": "Phone Types", "type": "Grid",
		                "program": "GridCompanyPhoneTypes", "programname": "Company Phone Types",
		                "run": 0, "create": 999, "update": 999, "delete": 999,			     
				        "url": "/grid/GridCompanyPhoneTypes"}},
			{"MenuItem": {"line": 400, "description": "Email Types", "type": "Grid",
		                "program": "GridCompanyEmailTypes", "programname": "Company Email Types",
		                "run": 0, "create": 999, "update": 999, "delete": 999,			     
				        "url": "/grid/GridCompanyEmailTypes"}},
			{"MenuItem": {"line": 900, "description": "Copy Company Data", "type": "Script",
		                "program": "CopyCompanyData", "programname": "Copy Company Data",
		                "run": 999, "create": 999, "update": 999, "delete": 999,			     
				        "url": "/copycompanydata"}}				        				        				        				        				        				        				        				        
		    ]}
	    },
	    {"MenuItem": {"line": 200, "id": "MenuControl", "name": "Controls Menu", "items": [
		    {"MenuItem": {"line": 100, "id": "MenuControlAddress", "name": "Address Menu", "items": [
			    {"MenuItem": {"line": 100, "description": "States", "type": "Grid",
				            "table": "CountryStates", "programname": "Country States",					     
				            "program": "GridCountryStates",
				            "run": 0, "create": 999, "update": 999, "delete": 999,
				            "url": "/grid/GridCountryStates"}},	
			    {"MenuItem": {"line": 200, "description": "Localities", "type": "Grid",
				            "table": "CountryLocalities", "programname": "Country Localities",					     
				            "program": "GridCountryLocalities",
				            "run": 0, "create": 999, "update": 999, "delete": 999,
				            "url": "/grid/GridCountryLocalities"}},	
			    {"MenuItem": {"line": 300, "description": "Postcodes", "type": "Grid",
				            "table": "CountryPostcodes", "programname": "Country Postcodes",					     
				            "program": "GridCountryPostcodes",
				            "run": 0, "create": 999, "update": 999, "delete": 999,
				            "url": "/grid/GridCountryPostcodes"}}					            	
		        ]}
	        },
	        {"MenuItem": {"line": 200, "id": "MenuControlPersonal", "name": "Personal Menu", "items": [
		        {"MenuItem": {"line": 100, "description": "Genders", "type": "Grid",
		                    "table": "PersonGenders", "programname": "Genders",					     
				            "program": "GridGenders",
				            "run": 0, "create": 800, "update": 800, "delete": 800,
				            "url": "/grid/GridGenders"}}, 
		        {"MenuItem": {"line": 200, "description": "Titles", "type": "Grid",
				            "table": "PersonTitles", "programname": "Personal Titles",					     
				            "program": "GridPersonTitles",
				            "run": 0, "create": 800, "update": 800, "delete": 800,
				            "url": "/grid/GridPersonTitles"}},	        
		        {"MenuItem": {"line": 300, "description": "Address Types", "type": "Grid",
			                "table": "PersonAddressTypes", "programname": "Personal Address Types",					     
				            "program": "GridPersonAddressTypes",
				            "run": 0, "create": 800, "update": 800, "delete": 800,
				            "url": "/grid/GridPersonAddressTypes"}}, 
			    {"MenuItem": {"line": 400, "description": "Phone Types", "type": "Grid",
				            "table": "PersonPhoneTypes", "programname": "Personal Phone Types",					     
				            "program": "GridPersonPhoneTypes",
				            "run": 0, "create": 800, "update": 800, "delete": 800,
				            "url": "/grid/GridPersonPhoneTypes"}},
			    {"MenuItem": {"line": 500, "description": "Email Types", "type": "Grid",
				            "table": "PersonEmailTypes", "programname": "Personal Email Types",					     
				            "program": "GridPersonEmailTypes",
				            "run": 0, "create": 800, "update": 800, "delete": 800,
				            "url": "/grid/GridPersonEmailTypes"}}				            	        
		        ]}
		    },
	        {"MenuItem": {"line": 300, "id": "MenuControlSystem", "name": "System Menu", "items": [
			    {"MenuItem": {"line": 100, "description": "Devices", "type": "Grid",
				            "table": "Devices", "programname": "Devices",					     
				            "program": "GridDevices",
				            "run": 0, "create": 999, "update": 999, "delete": 999,
				            "url": "/grid/GridDevices"}},
			    {"MenuItem": {"line": 200, "description": "Documents", "type": "Grid",
				            "table": "Documents", "programname": "Documents",					     
				            "program": "GridDocuments",
				            "run": 0, "create": 999, "update": 999, "delete": 999,
				            "url": "/grid/GridDocuments"}}				            
			    ]}
		    }								
	        ]}
	    },
	    {"MenuItem": {"line": 300, "id": "MenuSysConfig", "name": "System Configuration Menu", "items": [
		    {"MenuItem": {"line": 100, "id": "MenuSysSecurity", "name": "Securities Menu", "items": [
		        {"MenuItem": {"line": 100, "description": "Groups", "type": "Grid",
				            "table": "Groups", "programname": "Security Groups",					        
				            "program": "GridGroups",
				            "run": 0, "create": 999, "update": 999, "delete": 999,
				            "url": "/grid/GridGroups"}},
		        {"MenuItem": {"line": 200, "description": "Roles", "type": "Grid",
				            "table": "Roles", "programname": "Security Roles",					        
				            "program": "GridRoles",
				            "run": 0, "create": 999, "update": 999, "delete": 999,
				            "url": "/grid/GridRoles"}}, 				             
			    {"MenuItem": {"line": 300, "description": "Menus", "type": "Grid",
				            "table": "Menus", "programname": "Menus",					        
				            "program": "GridMenus",
				            "run": 0, "create": 999, "update": 999, "delete": 999,
				            "url": "/grid/GridMenus"}}, 
			    {"MenuItem": {"line": 400, "description": "Users", "type": "Grid",
				            "table": "Users", "programname": "Users",					        
				            "program": "GridUsers",
				            "run": 800, "create": 999, "update": 999, "delete": 999,
				            "url": "/grid/GridUsers"}},
			    {"MenuItem": {"line": 500, "description": "Audit", "type": "Script",
				            "program": "Audit", "programname": "Audit",					        				            
				            "run": 800, "create": 999, "update": 999, "delete": 999,
				            "url": "/script/Audit"}},
			    {"MenuItem": {"line": 600, "description": "Templates", "type": "Grid",
				            "table": "Templates", "programname": "Templates",					        
				            "program": "GridTemplates",
				            "run": 999, "create": 999, "update": 999, "delete": 999,
				            "url": "/grid/GridTemplates"}}
			    ]}
		    },
		    {"MenuItem": {"line": 200, "id": "MenuSysPurge", "name": "Purges Menu", "items": [
		        {"MenuItem": {"line": 100, "description": "Purge JobQ", "type": "Script",
		                     "program": "PurgeJobs", "programname": "Purge Jobs",
		                     "run": 999, "create": 999, "update": 999, "delete": 999,
				            "url": "/purgejobs"}}, 
			    {"MenuItem": {"line": 200, "description": "Purge Spooler", "type": "Script",
		                     "program": "PurgeSpool", "programname": "Purge Spool",	
		                     "run": 999, "create": 999, "update": 999, "delete": 999,		                     		     
				            "url": "/purgespool"}},
			    {"MenuItem": {"line": 300, "description": "Purge Notifications", "type": "Script",
		                     "program": "PurgeNotifications", "programname": "Purge Notifications",
		                     "run": 999, "create": 999, "update": 999, "delete": 999,		                     			     
				            "url": "/purgenotifications"}},
			    {"MenuItem": {"line": 400, "description": "Purge Workfiles", "type": "Script",
		                     "program": "PurgeWorkfiles", "programname": "Purge Workfiles",
		                     "run": 999, "create": 999, "update": 999, "delete": 999,		                     			     
				            "url": "/purgeworkfiles"}}				            				            				            
			    ]}
		    },
		    {"MenuItem": {"line": 300, "id": "MenuSysSystem", "name": "Systems Menu", "items": [
			    {"MenuItem": {"line": 100, "description": "Programs", "type": "Grid",
				            "table": "Programs", "programname": "Programs",					        
				            "program": "Programs",
		                     "run": 0, "create": 999, "update": 999, "delete": 999,				            
				            "url": "/grid/Programs"}},
			    {"MenuItem": {"line": 200, "description": "Program States", "type": "Grid",
				            "table": "ProgramStates", "programname": "Program States",					        
				            "program": "ProgramStates",
		                    "run": 0, "create": 999, "update": 999, "delete": 999,
				            "url": "/grid/ProgramStates"}}				            
			    ]}
		    },
		    {"MenuItem": {"line": 400, "id": "MenuSysRelease", "name": "Release Menu", "items": [
			    {"MenuItem": {"line": 100, "description": "Export Release Tables", "type": "Script",
		                     "program": "ExportReleaseTables", "programname": "Export Release Tables",
		                     "run": 999, "create": 999, "update": 999, "delete": 999,			     
				             "url": "/exportreleasetables"}},
			    {"MenuItem": {"line": 200, "description": "Import Release Tables", "type": "Script",
		                     "program": "ImportReleaseTables", "programname": "Import Release Tables",
		                     "run": 999, "create": 999, "update": 999, "delete": 999,			     
				             "url": "/importreleasetables"}}				            				             				            
			    ]}
		    },
		    {"MenuItem": {"line": 500, "id": "MenuDatabase", "name": "Database", "items": [
			    {"MenuItem": {"line": 100, "description": "Import Tables", "type": "Script",
		                     "program": "ImportTables", "programname": "Import Tables",
                             "run": 999, "create": 999, "update": 999, "delete": 999,			     
				             "url": "/importtables"}},		    
			    {"MenuItem": {"line": 200, "description": "Dump Database", "type": "Script",
		                     "program": "DumpDatabase", "programname": "Dump Database",
		                     "run": 999, "create": 999, "update": 999, "delete": 999,			     
				             "url": "/dumpdatabase"}},
			    {"MenuItem": {"line": 300, "description": "Load Database", "type": "Script",
		                     "program": "LoadDatabase", "programname": "Load Database",
		                     "run": 999, "create": 999, "update": 999, "delete": 999,			     
				             "url": "/loaddatabase"}}				            				             				            
			    ]}
		    }									    									    									    							
	        ]}
	    }
	    ]}
	}
]}
}
"""
menujson = json.loads(menus)

if __name__ == '__main__':

    def walk_menu(obj, tab=0):
        print("", end="\t" * tab)
        line = ""
        if "line" in obj:
            line = obj["line"]
        print(f"{line} Menu: {obj['name']}")
        tab = tab + 1
        for o in obj["items"]:
            if "items" in o["MenuItem"]:
                walk_menu(o["MenuItem"], tab)
            else:
                print("", end="\t" * tab)
                print(f"{o['MenuItem']['line']} MenuItem: {o['MenuItem']['description']}")

    print(json.dumps(menujson, indent=2))
    print("*" * 80)
    walk_menu(menujson["Mainmenu"])
    print("*" * 80)

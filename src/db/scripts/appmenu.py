import json

menus = """
{"Mainmenu": {"id": "MenuMain", "name": "Main Menu", "items": [
    {"MenuItem": {"line": 100, "id": "MenuProducts", "name": "Products", "items": [
	        {"MenuItem": {"line": 100, "description": "Styles", "type": "Grid", 
		                "table": "Products", "programname": "Product Styles",
		                "program": "GridStyles",
		                "run": 0, "create": 800, "update": 800, "delete": 800,
		                "url": "/grid/GridStyles"}},
	        {"MenuItem": {"line": 200, "description": "Colour/Fit/Dimensions", "type": "Grid", 
		                "table": "ProductColourFitDims", "programname": "Product Colour/Fit/Dimensions",
		                "program": "GridProductColFitDims",
		                "run": 0, "create": 800, "update": 800, "delete": 800,
		                "url": "/grid/GridProductColFitDims"}},
	        {"MenuItem": {"line": 300, "description": "SKUs", "type": "Grid", 
		                "table": "ProductSKUs", "programname": "Product SKUs",
		                "program": "GridProductSKUs",
		                "run": 0, "create": 800, "update": 800, "delete": 800,
		                "url": "/grid/GridProductSKUs"}},	
            {"MenuItem": {"line": 400, "id": "MenuProductPrices", "name": "Prices", "items": [
    	        {"MenuItem": {"line": 100, "description": "Price Lists", "type": "Grid", 
	    	                "table": "PriceLists", "programname": "Price Lists",
		                    "program": "GridPriceLists",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridPriceLists"}},
    	        {"MenuItem": {"line": 200, "description": "Price Bands", "type": "Grid", 
	    	                "table": "PriceBands", "programname": "Price Bands",
		                    "program": "GridPriceBands",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridPriceBands"}},
    	        {"MenuItem": {"line": 300, "description": "Contract Prices/Discounts", "type": "Grid", 
	    	                "table": "ContractPriceDiscounts", "programname": "Contract Prices/Discounts",
		                    "program": "GridContractPriceDiscounts",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridContractPriceDiscounts"}},            
                {"MenuItem": {"line": 900, "id": "MenuProductPriceControls", "name": "Controls", "items": [
        	        {"MenuItem": {"line": 100, "description": "Price Types", "type": "Grid", 
	        	                "table": "PriceTypes", "programname": "Price Types",
		                        "program": "GridPriceTypes",
		                        "run": 0, "create": 800, "update": 800, "delete": 800,
		                        "url": "/grid/GridPriceTypes"}}                
                    ]}
                }		                                
                ]}
            },
            {"MenuItem": {"line": 500, "id": "MenuProductCosts", "name": "Costs", "items": [
    	        {"MenuItem": {"line": 100, "description": "Costs", "type": "Grid", 
	    	                "table": "Costs", "programname": "Costs",
		                    "program": "GridCosts",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridCosts"}},            
                {"MenuItem": {"line": 900, "id": "MenuProductCostControls", "name": "Controls", "items": [
        	        {"MenuItem": {"line": 100, "description": "Cost Types", "type": "Grid", 
	        	                "table": "CostTypes", "programname": "Cost Types",
		                        "program": "GridCostTypes",
		                        "run": 0, "create": 800, "update": 800, "delete": 800,
		                        "url": "/grid/GridCostTypes"}}                
                    ]}
                }		                                            
                ]}
            },
            {"MenuItem": {"line": 900, "id": "MenuProductControls", "name": "Controls", "items": [
    	        {"MenuItem": {"line": 100, "description": "Colours", "type": "Grid", 
	    	                "table": "Colours", "programname": "Colours",
		                    "program": "GridProductColours",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductColours"}},            
    	        {"MenuItem": {"line": 200, "description": "Fittings", "type": "Grid", 
	    	                "table": "Fittings", "programname": "Fittings",
		                    "program": "GridProductFittings",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductFittings"}},            
    	        {"MenuItem": {"line": 300, "description": "Dimensions", "type": "Grid", 
	    	                "table": "Dimensions", "programname": "Dimensions",
		                    "program": "GridProductDimensions",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductDimensions"}},            
    	        {"MenuItem": {"line": 400, "description": "Unit of Measure", "type": "Grid", 
	    	                "table": "UOMs", "programname": "Unit of Measure",
		                    "program": "GridProductUOMs",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductUOMs"}},            
    	        {"MenuItem": {"line": 500, "description": "Size Scales", "type": "Grid", 
	    	                "table": "SizeScales", "programname": "Size Scales",
		                    "program": "GridProductSizeScales",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductSizeScales"}},            
    	        {"MenuItem": {"line": 600, "description": "Seasons", "type": "Grid", 
	    	                "table": "ProductSeasons", "programname": "Seasons",
		                    "program": "GridProductSeasons",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductSeasons"}},            
    	        {"MenuItem": {"line": 700, "description": "Genders", "type": "Grid", 
	    	                "table": "ProductGenders", "programname": "Genders",
		                    "program": "GridProductGenders",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductGenders"}},            
    	        {"MenuItem": {"line": 800, "description": "Brands", "type": "Grid", 
	    	                "table": "ProductBrands", "programname": "Product Brands",
		                    "program": "GridProductBrands",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductBrands"}},            
    	        {"MenuItem": {"line": 900, "description": "Fabrics", "type": "Grid", 
	    	                "table": "ProductFabrics", "programname": "Product Main Fabric",
		                    "program": "GridProductFabrics",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductFabrics"}},            
    	        {"MenuItem": {"line": 1000, "description": "Categories", "type": "Grid", 
	    	                "table": "ProductCategories", "programname": "Product Categories",
		                    "program": "GridProductCategories",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductCategories"}},            
    	        {"MenuItem": {"line": 1100, "description": "Classes", "type": "Grid", 
	    	                "table": "ProductClasses", "programname": "Product Classes",
		                    "program": "GridProductClasses",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductClasses"}},            
    	        {"MenuItem": {"line": 1200, "description": "Types", "type": "Grid", 
	    	                "table": "ProductTypes", "programname": "Product Types",
		                    "program": "GridProductTypes",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductTypes"}},            
    	        {"MenuItem": {"line": 1300, "description": "Groups", "type": "Grid", 
	    	                "table": "ProductGroups", "programname": "Product Groups",
		                    "program": "GridProductGroups",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductGroups"}},            
    	        {"MenuItem": {"line": 1400, "description": "Description Types", "type": "Grid", 
	    	                "table": "ProductDescriptionTypes", "programname": "Product Description Types",
		                    "program": "GridProductDescriptionTypes",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductDescriptionTypes"}},
    	        {"MenuItem": {"line": 1500, "description": "Search Keywords", "type": "Grid", 
	    	                "table": "ProductKeywords", "programname": "Product Keywords",
		                    "program": "GridProductKeywords",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridProductKeywords"}},            		                                
                {"MenuItem": {"line": 1600, "id": "MenuProductControlProcessingGroups", "name": "Processing Groups", "items": [
        	        {"MenuItem": {"line": 100, "description": "Reporting Process", "type": "Grid", 
	        	                "table": "ProductReportingGroups", "programname": "Product Reporting Process",
		                        "program": "GridProductReportingGroups",
		                        "run": 0, "create": 800, "update": 800, "delete": 800,
		                        "url": "/grid/GridProductReportingGroups"}},
        	        {"MenuItem": {"line": 200, "description": "Sales Process", "type": "Grid", 
	        	                "table": "ProductSalesGroups", "programname": "Product Sales Process",
		                        "program": "GridProductSalesGroups",
		                        "run": 0, "create": 800, "update": 800, "delete": 800,
		                        "url": "/grid/GridProductSalesGroups"}},
        	        {"MenuItem": {"line": 300, "description": "Allocation Process", "type": "Grid", 
	        	                "table": "ProductAllocationGroups", "programname": "Product Allocation Process",
		                        "program": "GridProductAllocationGroups",
		                        "run": 0, "create": 800, "update": 800, "delete": 800,
		                        "url": "/grid/GridProductAllocationGroups"}},
        	        {"MenuItem": {"line": 400, "description": "Picking Process", "type": "Grid", 
	        	                "table": "ProductPickingGroups", "programname": "Product Picking Process",
		                        "program": "GridProductPickingGroups",
		                        "run": 0, "create": 800, "update": 800, "delete": 800,
		                        "url": "/grid/GridProductPickingGroups"}},                            		                                                    		                                                    		                                                    
        	        {"MenuItem": {"line": 500, "description": "Packing Process", "type": "Grid", 
	        	                "table": "ProductPackingGroups", "programname": "Product Packing Process",
		                        "program": "GridProductPackingGroups",
		                        "run": 0, "create": 800, "update": 800, "delete": 800,
		                        "url": "/grid/GridProductPackingGroups"}},                            		                                                    		                                                    		                                                    
        	        {"MenuItem": {"line": 600, "description": "Despatch Process", "type": "Grid", 
	        	                "table": "ProductDespatchGroups", "programname": "Product Despatch Process",
		                        "program": "GridProductDespatchGroups",
		                        "run": 0, "create": 800, "update": 800, "delete": 800,
		                        "url": "/grid/GridProductDespatchGroups"}},                            		                                                    		                                                    		                                                    
        	        {"MenuItem": {"line": 700, "description": "Returns Process", "type": "Grid", 
	        	                "table": "ProductReturnsGroups", "programname": "Product Returns Process",
		                        "program": "GridProductReturnsGroups",
		                        "run": 0, "create": 800, "update": 800, "delete": 800,
		                        "url": "/grid/GridProductReturnsGroups"}},                            		                                                    		                                                    		                                                    
        	        {"MenuItem": {"line": 800, "description": "Cancel Process", "type": "Grid", 
	        	                "table": "ProductCancelGroups", "programname": "Product Cancel Process",
		                        "program": "GridProductCancelGroups",
		                        "run": 0, "create": 800, "update": 800, "delete": 800,
		                        "url": "/grid/GridProductCancelGroups"}}                            		                                                    		                                                    		                                                    		                                                    		                                                    		                                                    		                                                    
                    ]}
                }                
                ]}    
            }   		                	                		                		                            		                	                		                		                
	    ]}
	},
    {"MenuItem": {"line": 200, "id": "MenuBusinessPartners", "name": "Business Partners", "items": [
        {"MenuItem": {"line": 100, "id": "MenuCustomers", "name": "Customers", "items": [
            {"MenuItem": {"line": 900, "id": "MenuCustomerControls", "name": "Controls", "items": [
                ]}
            }		                	                		                		                            		                	                		                		                        
            ]}
        },
        {"MenuItem": {"line": 200, "id": "MenuSuppliers", "name": "Suppliers", "items": [
            {"MenuItem": {"line": 900, "id": "MenuSupplierControls", "name": "Controls", "items": [
                ]}
            }		                	                		                		                            		                	                		                		                                
            ]}
        },
	    {"MenuItem": {"line": 300, "description": "Currency Exchange", "type": "Grid", 
		            "table": "CurrencyExchanges", "programname": "Currency Exchange",
		            "program": "GridCurrencyExchanges",
		            "run": 0, "create": 800, "update": 800, "delete": 800,
		            "url": "/grid/GridCurrencyExchanges"}},
	    {"MenuItem": {"line": 400, "description": "Tax Rates", "type": "Grid", 
		            "table": "TaxRates", "programname": "Tax Rates",
		            "program": "GridTaxRates",
		            "run": 0, "create": 800, "update": 800, "delete": 800,
		            "url": "/grid/GridTaxRates"}},        		                    
        {"MenuItem": {"line": 900, "id": "MenuBusinessPartnerControls", "name": "Controls", "items": [
    	    {"MenuItem": {"line": 100, "description": "Trading Terms", "type": "Grid", 
	    	            "table": "TradingTerms", "programname": "Trading Terms",
		                "program": "GridTradingTerms",
		                "run": 0, "create": 800, "update": 800, "delete": 800,
		                "url": "/grid/GridTradingTerms"}},        		                    
    	    {"MenuItem": {"line": 200, "description": "Tax Types", "type": "Grid", 
	    	            "table": "TaxTypes", "programname": "Tax Types",
		                "program": "GridTaxTypes",
		                "run": 0, "create": 800, "update": 800, "delete": 800,
		                "url": "/grid/GridTaxTypes"}}        		                            
            ]}
        }    
        ]}
    },
    {"MenuItem": {"line": 300, "id": "MenuSalesOrders", "name": "Sales Orders", "items": [
            {"MenuItem": {"line": 900, "id": "MenuSalesOrderControls", "name": "Controls", "items": [
                ]}
            }		                	                		                		                            		                	                		                		                    
        ]}
    },
    {"MenuItem": {"line": 400, "id": "MenuPurchaseOrders", "name": "Purchase Orders", "items": [
            {"MenuItem": {"line": 900, "id": "MenuPurchaseOrderControls", "name": "Controls", "items": [
                ]}
            }		                	                		                		                            		                	                		                		                        
        ]}
    },
    {"MenuItem": {"line": 700, "id": "MenuWarehouses", "name": "Warehouses", "items": [
    	    {"MenuItem": {"line": 100, "description": "Warehouses", "type": "Grid", 
	    	            "table": "Warehouses", "programname": "Warehouses",
		                "program": "GridWarehouses",
		                "run": 0, "create": 800, "update": 800, "delete": 800,
		                "url": "/grid/GridWarehouses"}},        		                    
    	    {"MenuItem": {"line": 200, "description": "Areas", "type": "Grid", 
	    	            "table": "WarehouseAreas", "programname": "Areas",
		                "program": "GridWarehouseAreas",
		                "run": 0, "create": 800, "update": 800, "delete": 800,
		                "url": "/grid/GridWarehouseAreas"}},
    	    {"MenuItem": {"line": 300, "description": "Locations", "type": "Grid", 
	    	            "table": "WarehouseLocations", "programname": "Locations",
		                "program": "GridWarehouseLocations",
		                "run": 0, "create": 800, "update": 800, "delete": 800,
		                "url": "/grid/GridWarehouseLocations"}},        		                                
		                        		                                
            {"MenuItem": {"line": 900, "id": "MenuWarehouseControls", "name": "Controls", "items": [
        	    {"MenuItem": {"line": 100, "description": "Address Types", "type": "Grid", 
	        	            "table": "WarehouseAddressTypes", "programname": "Address Types",
		                    "program": "GridWarehouseAddressTypes",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridWarehouseAddressTypes"}},
        	    {"MenuItem": {"line": 200, "description": "Phone Types", "type": "Grid", 
	        	            "table": "WarehousePhoneTypes", "programname": "Phone Types",
		                    "program": "GridWarehousePhoneTypes",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridWarehousePhoneTypes"}},        		                                
        	    {"MenuItem": {"line": 300, "description": "Email Types", "type": "Grid", 
	        	            "table": "WarehouseEmailTypes", "programname": "Email Types",
		                    "program": "GridWarehouseEmailTypes",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridWarehouseEmailTypes"}},        		                                
        	    {"MenuItem": {"line": 400, "description": "Contact Types", "type": "Grid", 
	        	            "table": "WarehouseContactTypes", "programname": "Contact Types",
		                    "program": "GridWarehouseContactTypes",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridWarehouseContactTypes"}}        		                                		                            		                                
                ]}
            }		                	                		                		                            		                	                		                		                            
        ]}
    },
    {"MenuItem": {"line": 800, "id": "MenuStocks", "name": "Stocks", "items": [
            {"MenuItem": {"line": 100, "id": "MenuStockProducts", "name": "Products", "items": [
			    {"MenuItem": {"line": 100, "description": "Stock On Hand", "type": "Script",
				            "program": "ProductStockOnHand", "programname": "Stock On Hand",					        				            
				            "run": 0, "create": 999, "update": 999, "delete": 999,
				            "url": "/script/ProductStockOnHand"}},        
			    {"MenuItem": {"line": 200, "description": "Stock Adjustment", "type": "Script",
				            "program": "ProductStockAdjustment", "programname": "Stock Adjustment",					        				            
				            "run": 800, "create": 800, "update": 800, "delete": 800,
				            "url": "/script/ProductStockAdjustment"}},
			    {"MenuItem": {"line": 300, "description": "Net Position", "type": "Script",
				            "program": "ProductNetPositionRequestor", "programname": "Net Position",					        				            
				            "run": 0, "create": 800, "update": 800, "delete": 800,
				            "url": "/script/ProductNetPositionRequestor"}}            
                ]}
            },		                	                		                		                            		                	                		                		                                
            {"MenuItem": {"line": 200, "id": "MenuStockRawMaterials", "name": "Raw Materials", "items": [
                ]}
            },		                	                		                		                            		                	                		                		                                    
            {"MenuItem": {"line": 900, "id": "MenuStockControls", "name": "Controls", "items": [
        	    {"MenuItem": {"line": 100, "description": "Adjustment Reasons", "type": "Grid", 
	        	            "table": "StockAdjustmentReasons", "programname": "Adjustment Reasons",
		                    "program": "GridStockAdjustmentReasons",
		                    "run": 0, "create": 800, "update": 800, "delete": 800,
		                    "url": "/grid/GridStockAdjustmentReasons"}}            
                ]}
            }		                	                		                		                            		                	                		                		                                
        ]}
    }    	        	        	        	        	        	        	        	        	        	        	        	        	        	        	        	
]}
}
"""
appmenujson = json.loads(menus)

if __name__ == '__main__':

    def walk_menu(obj, tab=0):
        print("", end="\t" * tab)
        print("Menu: {}".format(obj["name"]))
        tab = tab + 1
        for o in obj["items"]:
            if "items" in o["MenuItem"]:
                walk_menu(o["MenuItem"], tab)
            else:
                print("", end="\t" * tab)
                print("MenuItem: {}".format(o["MenuItem"]["description"]))

    print(json.dumps(appmenujson, indent=2))
    print("*" * 80)
    walk_menu(appmenujson["Mainmenu"])
    print("*" * 80)

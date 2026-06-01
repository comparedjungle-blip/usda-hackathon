import pdfplumber
import pandas as pd
import sys
import re
import os
import glob
import tkinter as tk
from tkinter import filedialog, messagebox

STOP_KEYWORDS = ['NUMBER OF SALES']
UNIT_SUFFIXES = [
    r'\bTON\b', r'\bEACH\b', r'\bLBS\b', r'\bLNFT\b', 
    r'\bCUFT\b', r'\bPIECE\b', r'\bCORDS\b'
]

def clean_num(val):
    if pd.isna(val) or val == "" or val is None:
        return None
    s = re.sub(r'[^0-9.]', '', str(val))
    try:
        return float(s) if s else None
    except ValueError:
        return None
    
def save_raw_csv(all_pages_data, base_name, output_dir):
    if all_pages_data:
        raw_path = os.path.join(output_dir, f"raw_converted_{base_name}.csv")
        pd.concat(all_pages_data, ignore_index=True).to_csv(raw_path, index=False)

def standardize_forest_name(raw_name):
    """
    Removes all spaces from the extracted name to find a match, 
    then returns the perfectly formatted name.
    """
    normalized = raw_name.replace(" ", "").upper()
    
    # Complete lookup mapping for all forests in your data
    forest_lookup = {
        "DAHOPANHANDLENATIONALFOREST": "Idaho Panhandle National Forest",
        "NEZPERCE-CLEARWATERNATIONALFOREST": "Nez Perce-Clearwater National Forest",
        "BEAVERHEAD/DEERLODGENATIONALFOREST": "Beaverhead/Deerlodge National Forest",
        "BITTERROOTNATIONALFOREST": "Bitterroot National Forest",
        "CUSTERGALLATINNATIONALFOREST": "Custer Gallatin National Forest",
        "FLATHEADNATIONALFOREST": "Flathead National Forest",
        "HELENA-LEWISANDCLARKNATIONALFOREST": "Helena - Lewis and Clark National Forest",
        "KOOTENAINATIONALFOREST": "Kootenai National Forest",
        "LOLONATIONALFOREST": "Lolo National Forest",
        "CHUGACHNATIONALFOREST": "Chugach National Forest",
        "TONGASSNATIONALFOREST": "Tongass National Forest",
        "ARAPAHOANDROOSEVELTNATIONALFOREST": "Arapaho and Roosevelt National Forest",
        "GRANDMESA/UNCOMPAHGRE/GUNNISONNATIONALFOREST": "Grand Mesa/Uncompahgre/Gunnison National Forest",
        "MEDICINEBOW-ROUTTNATIONALFOREST": "Medicine Bow-Routt National Forest",
        "PIKE-SANISABELNATIONALFOREST": "Pike-San Isabel National Forest",
        "RIOGRANDENATIONALFOREST": "Rio Grande National Forest",
        "SANJUANNATIONALFOREST": "San Juan National Forest",
        "WHITERIVERNATIONALFOREST": "White River National Forest",
        "NEBRASKANATIONALFOREST": "Nebraska National Forest",
        "BLACKHILLSNATIONALFOREST": "Black Hills National Forest",
        "BIGHORNNATIONALFOREST": "Bighorn National Forest",
        "SHOSHONENATIONALFOREST": "Shoshone National Forest",
        "APACHE-SITGREAVESNATIONALFORESTS": "Apache-Sitgreaves National Forests",
        "COCONINONATIONALFOREST": "Coconino National Forest",
        "CORONADONATIONALFOREST": "Coronado National Forest",
        "KAIBABNATIONALFOREST": "Kaibab National Forest",
        "PRESCOTTNATIONALFOREST": "Prescott National Forest",
        "TONTONATIONALFOREST": "Tonto National Forest",
        "CARSONNATIONALFOREST": "Carson National Forest",
        "CIBOLANATIONALFOREST": "Cibola National Forest",
        "GILANATIONALFOREST": "Gila National Forest",
        "INCOLNNATIONALFOREST": "Lincoln National Forest",  
        "LINCOLNNATIONALFOREST": "Lincoln National Forest",
        "SANTAFENATIONALFOREST": "Santa Fe National Forest",
        "HUMBOLDT&TOIYNATIONALFOREST": "Humboldt & Toiyabe National Forest",
        "BOISENATIONALFOREST": "Boise National Forest",
        "CARIBOU/TARGHEENATIONALFOREST": "Caribou/Targhee National Forest",
        "PAYETTENATIONALFOREST": "Payette National Forest",
        "SALMON-CHALLISNATIONALFOREST": "Salmon-Challis National Forest",
        "SAWTOOTHNATIONALFOREST": "Sawtooth National Forest",
        "ASHLEYNATIONALFOREST": "Ashley National Forest",
        "DIXIENATIONALFOREST": "Dixie National Forest",
        "FISHLAKENATIONALFOREST": "Fishlake National Forest",
        "MANTI-LASALNATIONALFOREST": "Manti-La Sal National Forest",
        "UINTA-WASATCH-CACHENATIONALFOREST": "Uinta-Wasatch-Cache National Forest",
        "BRIDGER-TETONNATIONALFOREST": "Bridger-Teton National Forest",
        "ANGELESNATIONALFOREST": "Angeles National Forest",
        "CLEVELANDNATIONALFOREST": "Cleveland National Forest",
        "ELDORADONATIONALFOREST": "Eldorado National Forest",
        "NYONATIONALFOREST": "Inyo National Forest",        
        "INYONATIONALFOREST": "Inyo National Forest",
        "KLAMATHNATIONALFOREST": "Klamath National Forest",
        "LAKETAHOEBASINNATIONALFOREST": "Lake Tahoe Basin National Forest",
        "LASSENNATIONALFOREST": "Lassen National Forest",
        "LOSPADRESNATIONALFOREST": "Los Padres National Forest",
        "MENDOCINONATIONALFOREST": "Mendocino National Forest",
        "MODOCNATIONALFOREST": "Modoc National Forest",
        "PLUMASNATIONALFOREST": "Plumas National Forest",
        "SANBERNARDINONATIONALFOREST": "San Bernardino National Forest",
        "SEQUOIANATIONALFOREST": "Sequoia National Forest",
        "SHASTA-TRINITYNATIONALFOREST": "Shasta-Trinity National Forest",
        "SIERRANATIONALFOREST": "Sierra National Forest",
        "SIXRIVERSNATIONALFOREST": "Six Rivers National Forest",
        "STANISLAUSNATIONALFOREST": "Stanislaus National Forest",
        "TAHOENATIONALFOREST": "Tahoe National Forest",
        "DESCHUTESNATIONALFOREST": "Deschutes National Forest",
        "FREMONT-WINEMANATIONALFOREST": "Fremont-Winema National Forest",
        "MALHEURNATIONALFOREST": "Malheur National Forest",
        "MTHOODNATIONALFOREST": "Mt. Hood National Forest",
        "OCHOCONATIONALFOREST": "Ochoco National Forest",
        "ROGUERIVER-SISKIYOUNATIONALFOREST": "Rogue River-Siskiyou National Forest",
        "SIUSLAWNATIONALFOREST": "Siuslaw National Forest",
        "UMATILLANATIONALFOREST": "Umatilla National Forest",
        "UMPQUANATIONALFOREST": "Umpqua National Forest",
        "WALLOWA-WHITMANNATIONALFOREST": "Wallowa-Whitman National Forest",
        "WILLAMETTENATIONALFOREST": "Willamette National Forest",
        "COLVILLENATIONALFOREST": "Colville National Forest",
        "GIFFORDPINCHOTNATIONALFOREST": "Gifford Pinchot National Forest",
        "MTBAKER/SNOQUALMIENATIONALFOREST": "Mt. Baker/Snoqualmie National Forest",
        "OKANOGAN-WENATCHEENATIONALFOREST": "Okanogan-Wenatchee National Forest",
        "OLYMPICNATIONALFOREST": "Olympic National Forest",
        "NFSINALABAMANATIONALFOREST": "NFS In Alabama National Forest",
        "OUACHITANATIONALFOREST": "Ouachita National Forest",
        "OZARKSTFRANCISNATIONALFOREST": "Ozark St. Francis National Forest",
        "NFSINFLORIDANATIONALFOREST": "NFS In Florida National Forest",
        "CHATTAHOOCHEE/OCONEENATIONALFOREST": "Chattahoochee/Oconee National Forest",
        "DANIELBOONENATIONALFOREST": "Daniel Boone National Forest",
        "LANDBETWEENTHELAKESNATIONALFOREST": "Land Between The Lakes National Forest",
        "KISATCHIENATIONALFOREST": "Kisatchie National Forest",
        "NFSINMISSISSIPPINATIONALFOREST": "NFS In Mississippi National Forest",
        "NFSINNCAROLINANATIONALFOREST": "NFS in N. Carolina National Forest",
        "FRANCISMARION-SUMTERNATIONALFOREST": "Francis Marion-Sumter National Forest",
        "CHEROKEENATIONALFOREST": "Cherokee National Forest",
        "NFSINTEXASNATIONALFOREST": "NFS In Texas National Forest",
        "GEORGEWASHINGTON&JEFFERSONNATIONALFOREST": "George Washington & Jefferson National Forest",
        "SHAWNEENATIONALFOREST": "Shawnee National Forest",
        "HOOSIERNATIONALFOREST": "Hoosier National Forest",
        "HIAWATHANATIONALFOREST": "Hiawatha National Forest",
        "HURONMANISTEENATIONALFOREST": "Huron Manistee National Forest",
        "OTTAWANATIONALFOREST": "Ottawa National Forest",
        "CHIPPEWANATIONALFOREST": "Chippewa National Forest",
        "SUPERIORNATIONALFOREST": "Superior National Forest",
        "MARKTWAINNATIONALFOREST": "Mark Twain National Forest",
        "WHITEMOUNTAINNATIONALFOREST": "White Mountain National Forest",
        "GREENMOUNTAINNATIONALFOREST": "Green Mountain National Forest",
        "WAYNENATIONALFOREST": "Wayne National Forest",
        "ALLEGHENYNATIONALFOREST": "Allegheny National Forest",
        "MONONGAHELANATIONALFOREST": "Monongahela National Forest",
        "CHEQUAMEGON/NICOLETNATIONALFOREST": "Chequamegon/Nicolet National Forest"
    }
    
    # Strip common secondary unit suffixes from the end of the clean lookup string
    for suffix in ["LNFT", "CUFT", "TON", "EACH", "LBS", "PIECE"]:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)]
            
    return forest_lookup.get(normalized, f"Unmapped: {raw_name}")

def process_pdf(pdf_path):
    extracted_rows = []
    all_pages_data = [] 
    seen_forests = set()
    
    settings = {
        "vertical_strategy": "text",
        "horizontal_strategy": "text",
        "snap_tolerance": 3,
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_dir = os.path.dirname(pdf_path)
            
            for i, page in enumerate(pdf.pages):
                table = page.extract_table(table_settings=settings)
                if not table:
                    continue
                
                df_page = pd.DataFrame(table)
                df_page['page_number'] = i + 1
                all_pages_data.append(df_page)
                
                for _, row in df_page.iterrows():
                    row_values = [str(x).strip() if x is not None else "" for x in row.values]
                    full_row_text = "".join(row_values)
                    normalized_text = full_row_text.replace(" ", "").upper()

                    # 1. Non-destructive summary totals row bypass filter
                    if "STATE TOTALS" in normalized_text or "REGION TOTALS" in normalized_text:
                        continue  
                    
                    # 2. Match National Forest (Fuzzy)
                    if "NATIONAL" in normalized_text and "FOREST" in normalized_text and "TOTAL" not in normalized_text:
                        name_parts = [x for x in row_values if re.search('[a-zA-Z]', x) and "PAGE" not in x.upper()]
                        raw_name = "".join(name_parts)
                        
                        clean_name = standardize_forest_name(raw_name)
                        if not clean_name:
                            continue
                        
                        if clean_name in seen_forests:
                            continue
                        
                        nums = [clean_num(x) for x in row_values if clean_num(x) is not None]
                        
                        if len(nums) >= 4:
                            vol_mbf = nums[1]
                            sold_val = nums[3]
                            
                            if vol_mbf > 0:
                                extracted_rows.append({
                                    "Source File": os.path.basename(pdf_path),
                                    "Forest Name": clean_name,
                                    "Sold Volume (MBF)": vol_mbf,
                                    "Sold Value ($)": sold_val,
                                    "Value per MBF": round(sold_val / vol_mbf, 2) if vol_mbf > 0 else 0
                                })
                                seen_forests.add(clean_name)

            save_raw_csv(all_pages_data, base_name, output_dir)

    except Exception as e:
        print(f"  [Error] {e}")
        
    return extracted_rows

def run_conversion(label_status):
    # Ask user to select files visually
    file_paths = filedialog.askopenfilenames(
        title="Select USDA Forest Cut and Sold PDFs",
        filetypes=[("PDF Files", "*.pdf")]
    )
    
    if not file_paths:
        label_status.config(text="No files selected.", fg="red")
        return
        
    label_status.config(text="Processing files... Please wait.", fg="blue")
    root.update_idletasks()
    
    master_data = []
    for pdf_file in file_paths:
        master_data.extend(process_pdf(pdf_file))

    if master_data:
        df = pd.DataFrame(master_data)
        df = df.drop_duplicates(subset=['Source File', 'Forest Name'])
        
        # Save output next to the first file selected
        output_directory = os.path.dirname(file_paths[0])
        final_destination = os.path.join(output_directory, "forest_only_summary.csv")
        
        df.to_csv(final_destination, index=False)
        
        label_status.config(text="Done!", fg="green")
        messagebox.showinfo("Success!", f"Successfully extracted {len(df)} entries!\n\nSaved to:\n{final_destination}")
    else:
        label_status.config(text="Extraction failed.", fg="red")
        messagebox.showwarning("No Data Found", "Could not locate matching forest rows in the selected files.")

# --- Build GUI Frame ---
root = tk.Tk()
root.title("USDA Forest Report Converter")
root.geometry("450x200")
root.resizable(False, False)

# App descriptive titles
lbl_title = tk.Label(root, text="National Forest Data Extractor", font=("Arial", 14, "bold"))
lbl_title.pack(pady=15)

lbl_instructions = tk.Label(root, text="Select one or multiple PDF files to combine them into an aggregate CSV spreadsheet.", wraplength=400, justify="center")
lbl_instructions.pack(pady=5)

# Status bar text tracking
lbl_status = tk.Label(root, text="Awaiting selection...", fg="gray")

# Main Action button
btn_select = tk.Button(root, text="Select PDFs & Run", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", padx=10, pady=5, command=lambda: run_conversion(lbl_status))
btn_select.pack(pady=15)

lbl_status.pack()

if __name__ == "__main__":
    root.mainloop()